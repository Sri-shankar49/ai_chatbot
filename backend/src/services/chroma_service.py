
from pathlib import Path

import chromadb

from config.settings import (
    BACKEND_DIR,
    CHROMA_PERSIST_DIR,
    EMBEDDING_DIMENSIONS,
)

persist_path = Path(CHROMA_PERSIST_DIR)

if not persist_path.is_absolute():
    persist_path = BACKEND_DIR / persist_path

persist_path.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(persist_path))

collection = client.get_or_create_collection(
    name="chatbot_documents",
    metadata={"hnsw:space": "cosine"},
)


def add_document(
    document_id: str,
    text: str,
    embedding: list[float],
    source: str = "unknown",
    chunk_index: int = 0,
) -> None:
    if len(embedding) != EMBEDDING_DIMENSIONS:
        raise ValueError("Unexpected embedding dimensions.")

    collection.upsert(
        ids=[document_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[
            {
                "source": source,
                "chunk_index": chunk_index,
            }
        ],
    )

def delete_documents(document_ids: list[str]) -> None:
    """Delete specific document chunks by their IDs."""
    if not document_ids:
        return

    collection.delete(ids=document_ids)
    
def search_documents(
    query_embedding: list[float],
    limit: int = 3,
) -> list[dict]:
    if len(query_embedding) != EMBEDDING_DIMENSIONS:
        raise ValueError("Unexpected embedding dimensions.")

    total = collection.count()

    if total == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(limit, total),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for i, document_id in enumerate(results["ids"][0]):
        matches.append(
            {
                "id": document_id,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    return matches


def get_all_documents() -> list[dict]:
    """Return stored document chunks for offline evaluation."""
    results = collection.get(
        include=["documents", "metadatas"],
    )

    documents = []

    for index, document_id in enumerate(results["ids"]):
        documents.append(
            {
                "id": document_id,
                "text": results["documents"][index],
                "metadata": (results["metadatas"] or [])[index]
                if results["metadatas"]
                else None,
            }
        )

    return documents

