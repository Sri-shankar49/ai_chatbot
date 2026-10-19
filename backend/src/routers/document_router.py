
from fastapi import APIRouter, File, UploadFile

from controllers.document_controller import (
    handle_document_upload,
)
from schemas.document_schema import DocumentUploadResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
):
    try:
        return await handle_document_upload(file)
    finally:
        await file.close()
