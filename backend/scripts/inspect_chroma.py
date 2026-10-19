
from services.chroma_service import get_all_documents

documents = get_all_documents()

print(f"Total chunks: {len(documents)}\n")

for index, document in enumerate(documents[:15], start=1):
    metadata = document.get("metadata") or {}

    print(f"Chunk {index}")
    print(f"ID: {document['id']}")
    print(f"Source: {metadata.get('source', 'unknown')}")
    print(f"Chunk index: {metadata.get('chunk_index', -1)}")
    print(f"Text: {(document.get('text') or '')[:400]}")
    print("-" * 60)

sources = sorted({
    (document.get("metadata") or {}).get("source", "unknown")
    for document in documents
})

print("\nSources found in ChromaDB:")
for source in sources:
    print(f"- {source}")
