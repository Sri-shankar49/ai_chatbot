
import logging
import asyncio
import io
import uuid
from pathlib import Path

import fitz
# import pymupdf  # PyMuPDF
from fastapi import HTTPException, UploadFile

from schemas.document_schema import DocumentUploadResponse
from services.document_service import chunk_text
from services.embedding_service import embed_text
from services.chroma_service import (add_document, delete_documents)


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MiB

logger = logging.getLogger(__name__)

async def handle_document_upload(
    file: UploadFile,
) -> DocumentUploadResponse:
    # filename = Path(file.filename or "").name
    # suffix = Path(filename).suffix.lower()

    raw_filename = (file.filename or "").replace("\\", "/")
    filename = Path(raw_filename).name
    suffix = Path(filename).suffix.lower()
    
    if suffix not in {".pdf", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 5 MiB upload limit.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    try:
        if suffix == ".pdf":
            with fitz.open(
                stream=content,
                filetype="pdf",
            ) as pdf:
                text = "\n".join(
                    page.get_text() for page in pdf
                )
        else:
            text = content.decode("utf-8-sig")
            
            if "\x00" in text:
                raise HTTPException(
                    status_code=400,
                    detail="The TXT file contains invalid binary content.",
                )

    except (ValueError, UnicodeDecodeError, RuntimeError):
        raise HTTPException(
            status_code=400,
            detail="The file could not be read. Check its format.",
        ) from None

    chunks = chunk_text(text)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found. "
                "Scanned PDFs need OCR, which we will add later."
            ),
        )

    # Prepare every embedding before storing the document.
    document_id = str(uuid.uuid4())
    prepared_chunks = []

    try:
        for index, chunk in enumerate(chunks):
            embedding = await asyncio.to_thread(
                embed_text,
                chunk,
            )

            prepared_chunks.append(
                (f"{document_id}-{index}", chunk, embedding, index)
            )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail=(
                "Embedding generation failed. "
                "Check the Google API configuration and quota."
            ),
        ) from None

    # Store the prepared chunks in the persistent collection.
    # try:
    #     for chunk_id, chunk, embedding, index in prepared_chunks:
    #         add_document(
    #             document_id=chunk_id,
    #             text=chunk,
    #             embedding=embedding,
    #             source=filename,
    #             chunk_index=index,
    #         )

    # except Exception:
    #     raise HTTPException(
    #         status_code=500,
    #         detail="Failed to store document chunks.",
    #     ) from None
    
    # Store the prepared chunks in ChromaDB.
    stored_chunk_ids = []
    
    try:
        for chunk_id, chunk, embedding, index in prepared_chunks:
            add_document(
                document_id=chunk_id,
                text=chunk,
                embedding=embedding,
                source=filename,
                chunk_index=index,
            )

            # Track only chunks that were stored successfully.
            stored_chunk_ids.append(chunk_id)

    except Exception:
        # Attempt to remove chunks stored by this upload.
        logger.exception(
            "Document chunk storage failed; attempting rollback."
        )
        
        try:
            delete_documents(stored_chunk_ids)
        except Exception:
            # Rollback failed. Do not expose internal details.
            # pass
            logger.exception(
                "Document upload rollback failed. "
                "Some chunks may remain in ChromaDB."
            )

        # Raise this whether rollback succeeds or fails.
        raise HTTPException(
            status_code=500,
            detail="Failed to store document chunks.",
        ) from None
        
    return DocumentUploadResponse(
        filename=filename,
        chunks_stored=len(prepared_chunks),
        message="Document indexed successfully.",
    )
