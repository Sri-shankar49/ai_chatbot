
# from services.embedding_service import embed_text
# from services.chroma_service import add_document


# DOCUMENT_ID = "evaluation_employee_policy_0"
# SOURCE = "employee_policy.txt"

# POLICY_TEXT = """
# Employee Leave Policy

# Employees receive 20 days of annual leave per year.
# Employees receive 10 days of sick leave per year.
# Annual leave requests must be submitted to the manager.
# """.strip()


# def main():
#     print("Generating policy embedding...")

#     embedding = embed_text(POLICY_TEXT)

#     add_document(
#         document_id=DOCUMENT_ID,
#         text=POLICY_TEXT,
#         embedding=embedding,
#         source=SOURCE,
#         chunk_index=0,
#     )

#     print("Evaluation document stored successfully.")
#     print(f"Source: {SOURCE}")
#     print(f"Document ID: {DOCUMENT_ID}")


# if __name__ == "__main__":
#     main()



from services.embedding_service import embed_text
from services.chroma_service import add_document


POLICY_CHUNKS = [
    {
        "id": "eval_annual_leave",
        "text": "Employees receive 20 days of annual leave per year.",
        "chunk_index": 1,
    },
    {
        "id": "eval_sick_leave",
        "text": "Employees receive 10 days of sick leave per year.",
        "chunk_index": 2,
    },
    {
        "id": "eval_leave_request",
        "text": "Annual leave requests must be submitted to the manager.",
        "chunk_index": 3,
    },
]


def main():
    for chunk in POLICY_CHUNKS:
        print(f"Embedding: {chunk['id']}")

        embedding = embed_text(chunk["text"])

        add_document(
            document_id=chunk["id"],
            text=chunk["text"],
            embedding=embedding,
            source="employee_policy.txt",
            chunk_index=chunk["chunk_index"],
        )

        print(f"Stored: {chunk['id']}")

    print("Evaluation chunks stored successfully.")


if __name__ == "__main__":
    main()
