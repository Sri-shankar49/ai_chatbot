
from src.services.embedding_service import embed_text
from src.services.chroma_service import add_document, search_documents


def main():
    documents = [
        (
            "python",
            "Python is a programming language used for "
            "web development, automation, and AI.",
        ),
        (
            "fastapi",
            "FastAPI is a Python framework used to build APIs.",
        ),
        (
            "react",
            "React is a JavaScript library for building user interfaces.",
        ),
    ]

    # Generate and store document vectors.
    for document_id, text in documents:
        vector = embed_text(text)
        print(f"{document_id}: {len(vector)} dimensions")

        add_document(document_id, text, vector)

    # Search for a conceptually related document.
    question = "Which technology helps me create a backend API with Python?"
    query_vector = embed_text(question, is_query=True)

    matches = search_documents(query_vector, limit=3)

    print("\nSearch results:")
    for match in matches:
        print(f"\nID: {match['id']}")
        print(f"Text: {match['text']}")
        print(f"Distance: {match['distance']:.4f}")


if __name__ == "__main__":
    main()
