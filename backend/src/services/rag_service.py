
# import asyncio
# import logging
# from modulefinder import test

# from services.embedding_service import embed_text
# from services.chroma_service import search_documents
# from services.groq_service import generate_response

# from config.settings import RAG_MAX_DISTANCE, RAG_TOP_K
# from services.chroma_service import search_documents

# logger = logging.getLogger(__name__)


# async def answer_question(message: str) -> dict:
#     # Convert the user's question into a vector.
#     query_embedding = await asyncio.to_thread(
#         embed_text,
#         message,
#         is_query=True,
#     )

#     # Retrieve the three most similar document chunks.
#     matches = search_documents(
#         query_embedding,
#         limit=3,
#     )

#     if not matches:
#         # Keep ordinary chatbot functionality if no files exist.
#         reply = await generate_response(message)

#         return {
#             "reply": reply,
#             "sources": [],
#             "retrieved_chunks": 0,
#         }

#     context_parts = []
#     sources = []

#     for match in matches:
#         source = match["metadata"]["source"]
#         chunk_index = match["metadata"]["chunk_index"]

#         context_parts.append(
#             f"[Source: {source}, chunk: {chunk_index}]\n"
#             f"{match['text']}"
#         )

#         source_info = {
#             "filename": source,
#             "chunk_index": chunk_index,
#         }

#         if source_info not in sources:
#             sources.append(source_info)

#     context = "\n\n---\n\n".join(context_parts)

#     reply = await generate_response(
#         message,
#         context=context,
#     )

#     return {
#         "reply": reply,
#         "sources": sources,
#         "retrieved_chunks": len(matches),
#     }







# async def answer_question(message: str) -> dict:
#     logger.info("RAG: generating query embedding")

#     query_embedding = await asyncio.to_thread(
#         embed_text,
#         message,
#         is_query=True,
#     )

#     logger.info(
#         "RAG: embedding generated; dimensions=%s",
#         len(query_embedding),
#     )

#     logger.info("RAG: searching ChromaDB")

#     matches = search_documents(query_embedding, limit=3)

#     logger.info("RAG: retrieved %s chunks", len(matches))

#     context = "\n\n---\n\n".join(
#         (
#             f"[Source: {match['metadata']['source']}, "
#             f"chunk: {match['metadata']['chunk_index']}]\n"
#             f"{match['text']}"
#         )
#         for match in matches
#     )

#     logger.info("RAG: calling Groq")

#     reply = await generate_response(
#         message,
#         context=context,
#     )

#     logger.info("RAG: completed successfully")

#     return {
#         "reply": reply,
#         "sources": [
#             {
#                 "filename": match["metadata"]["source"],
#                 "chunk_index": match["metadata"]["chunk_index"],
#             }
#             for match in matches
#         ],
#         "retrieved_chunks": len(matches),
#     }





# # test case
# def filter_relevant_matches(
#     matches: list[dict],
#     max_distance: float = RAG_MAX_DISTANCE,
# ) -> list[dict]:
#     """Keep matches whose cosine distance meets the threshold."""
#     return [
#         match
#         for match in matches
#         if match.get("distance") is not None
#         and match["distance"] <= max_distance
#     ]
    
    

# async def answer_question(message: str, history: list[dict] | None = None) -> dict:
#     logger.info("RAG: generating query embedding")

#     query_embedding = await asyncio.to_thread(
#         embed_text,
#         message,
#         is_query=True,
#     )

#     logger.info("RAG: searching ChromaDB")

#     # matches = search_documents(query_embedding, limit=3)
    
#     # After generating the query embedding:
#     matches = search_documents(
#         query_embedding,
#         limit=RAG_TOP_K,
#     )
    
#     # relevant_matches = [
#     #     match
#     #     for match in matches
#     #     if match.get("distance") is not None
#     #     and match["distance"] <= RAG_MAX_DISTANCE
#     # ]
    
#     relevant_matches = filter_relevant_matches(matches)

#     logger.info("RAG: retrieved %s chunks", len(matches))
    
#     if not relevant_matches:
#         return {
#             "reply": (
#                 "I couldn't find enough relevant information in "
#                 "the uploaded documents to answer that question. "
#                 "Try uploading a relevant document or asking a "
#                 "question about information it contains."
#             ),
#             "sources": [],
#             "retrieved_chunks": 0,
#         }

# # Build context and source citations from relevant_matches only.

#     if not matches:
#         reply = await generate_response(message, history=history)

#         return {
#             "reply": reply,
#             "sources": [],
#             "retrieved_chunks": 0,
#         }

#     context_parts = []
#     sources = []

#     for match in matches:
#         # Older records may not have metadata.
#         metadata = match.get("metadata") or {}

#         source = metadata.get("source", "unknown")
#         chunk_index = metadata.get("chunk_index", -1)

#         context_parts.append(
#             f"[Source: {source}, chunk: {chunk_index}]\n"
#             f"{match['text']}"
#         )

#         source_info = {
#             "filename": source,
#             "chunk_index": chunk_index,
#         }

#         if source_info not in sources:
#             sources.append(source_info)

#     context = "\n\n---\n\n".join(context_parts)

#     logger.info("RAG: calling Groq")

#     reply = await generate_response(
#         message,
#         context=context,
#         history=history,
#     )

#     logger.info("RAG: completed successfully")

#     return {
#         "reply": reply,
#         "sources": sources,
#         "retrieved_chunks": len(matches),
#     }
    
    



import asyncio
import logging

from config.settings import RAG_MAX_DISTANCE, RAG_TOP_K
from services.embedding_service import embed_text
from services.chroma_service import search_documents
from services.groq_service import generate_response

logger = logging.getLogger(__name__)


def filter_relevant_matches(
    matches: list[dict],
    max_distance: float = RAG_MAX_DISTANCE,
) -> list[dict]:
    """Keep matches whose cosine distance is within the threshold."""
    return [
        match
        for match in matches
        if match.get("distance") is not None
        and match["distance"] <= max_distance
    ]


async def answer_question(
    message: str,
    history: list[dict] | None = None,
) -> dict:
    logger.info("RAG: generating query embedding")

    query_embedding = await asyncio.to_thread(
        embed_text,
        message,
        is_query=True,
    )

    logger.info("RAG: searching ChromaDB")

    matches = search_documents(
        query_embedding,
        limit=RAG_TOP_K,
    )

    logger.info("RAG: retrieved %s chunks", len(matches))

    # No documents exist in the collection: use normal chatbot mode.
    if not matches:
        reply = await generate_response(
            message,
            history=history,
        )

        return {
            "reply": reply,
            "sources": [],
            "retrieved_chunks": 0,
        }

    # Keep only sufficiently relevant document chunks.
    relevant_matches = filter_relevant_matches(matches)

    logger.info(
        "RAG: retained %s relevant chunks",
        len(relevant_matches),
    )

    # Documents exist, but none are relevant enough.
    if not relevant_matches:
        return {
            "reply": (
                "I couldn't find enough relevant information in "
                "the uploaded documents to answer that question. "
                "Try uploading a relevant document or asking a "
                "question about information it contains."
            ),
            "sources": [],
            "retrieved_chunks": 0,
        }

    # Build context and citations using relevant chunks only.
    context_parts = []
    sources = []

    for match in relevant_matches:
        metadata = match.get("metadata") or {}

        source = metadata.get("source", "unknown")
        chunk_index = metadata.get("chunk_index", -1)

        context_parts.append(
            f"[Source: {source}, chunk: {chunk_index}]\n"
            f"{match['text']}"
        )

        source_info = {
            "filename": source,
            "chunk_index": chunk_index,
        }

        if source_info not in sources:
            sources.append(source_info)

    context = "\n\n---\n\n".join(context_parts)

    logger.info("RAG: calling Groq")

    reply = await generate_response(
        message,
        context=context,
        history=history,
    )

    logger.info("RAG: completed successfully")

    return {
        "reply": reply,
        "sources": sources,
        "retrieved_chunks": len(relevant_matches),
    }

