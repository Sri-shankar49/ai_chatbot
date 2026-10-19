
import asyncio

from services import rag_service


def test_no_documents_uses_normal_chat(monkeypatch):
    history = [{"role": "user", "content": "Hello"}]
    calls = {}

    def fake_embed_text(text, *, is_query=False):
        return [0.1, 0.2]

    def fake_search_documents(embedding, limit):
        return []

    async def fake_generate_response(message, context="", history=None):
        calls["message"] = message
        calls["context"] = context
        calls["history"] = history
        return "Hello! How can I help?"

    monkeypatch.setattr(rag_service, "embed_text", fake_embed_text)
    monkeypatch.setattr(
        rag_service, "search_documents", fake_search_documents
    )
    monkeypatch.setattr(
        rag_service, "generate_response", fake_generate_response
    )

    result = asyncio.run(
        rag_service.answer_question("Hello", history=history)
    )

    assert result["reply"] == "Hello! How can I help?"
    assert result["sources"] == []
    assert result["retrieved_chunks"] == 0
    assert calls["message"] == "Hello"
    assert calls["history"] == history


def test_only_relevant_chunks_reach_groq(monkeypatch):
    calls = {}

    matches = [
        {
            "id": "chunk-1",
            "text": "The company provides 20 days of annual leave.",
            "metadata": {
                "source": "employee_policy.pdf",
                "chunk_index": 0,
            },
            "distance": 0.10,
        },
        {
            "id": "chunk-2",
            "text": "Unrelated information about cooking.",
            "metadata": {
                "source": "cooking.txt",
                "chunk_index": 1,
            },
            "distance": 0.90,
        },
    ]

    def fake_embed_text(text, *, is_query=False):
        return [0.1, 0.2]

    def fake_search_documents(embedding, limit):
        return matches

    async def fake_generate_response(message, context="", history=None):
        calls["context"] = context
        calls["history"] = history
        return "The policy provides 20 days of annual leave."

    monkeypatch.setattr(rag_service, "embed_text", fake_embed_text)
    monkeypatch.setattr(
        rag_service, "search_documents", fake_search_documents
    )
    monkeypatch.setattr(
        rag_service, "generate_response", fake_generate_response
    )

    history = [{"role": "user", "content": "Tell me about leave"}]

    result = asyncio.run(
        rag_service.answer_question(
            "How many annual leave days?",
            history=history,
        )
    )

    assert "20 days of annual leave" in calls["context"]
    assert "Unrelated information about cooking" not in calls["context"]
    assert calls["history"] == history
    assert result["sources"] == [
        {"filename": "employee_policy.pdf", "chunk_index": 0}
    ]
    assert result["retrieved_chunks"] == 1


def test_irrelevant_chunks_do_not_reach_groq(monkeypatch):
    groq_called = False

    def fake_embed_text(text, *, is_query=False):
        return [0.1, 0.2]

    def fake_search_documents(embedding, limit):
        return [
            {
                "id": "chunk-1",
                "text": "Unrelated cooking information.",
                "metadata": {"source": "cooking.txt", "chunk_index": 0},
                "distance": 0.90,
            }
        ]

    async def fake_generate_response(message, context="", history=None):
        nonlocal groq_called
        groq_called = True
        return "This should not be called."

    monkeypatch.setattr(rag_service, "embed_text", fake_embed_text)
    monkeypatch.setattr(
        rag_service, "search_documents", fake_search_documents
    )
    monkeypatch.setattr(
        rag_service, "generate_response", fake_generate_response
    )

    result = asyncio.run(
        rag_service.answer_question("What is the leave policy?")
    )

    assert "couldn't find enough relevant information" in result["reply"]
    assert result["sources"] == []
    assert result["retrieved_chunks"] == 0
    assert groq_called is False



def test_relevant_chunk_without_metadata_does_not_crash(monkeypatch):
    def fake_embed_text(text, *, is_query=False):
        return [0.1, 0.2]

    def fake_search_documents(embedding, limit):
        return [
            {
                "id": "chunk-1",
                "text": "The company provides 20 days of annual leave.",
                "metadata": None,
                "distance": 0.10,
            }
        ]

    async def fake_generate_response(message, context="", history=None):
        assert "20 days of annual leave" in context
        return "The policy provides 20 days of annual leave."

    monkeypatch.setattr(rag_service, "embed_text", fake_embed_text)
    monkeypatch.setattr(
        rag_service, "search_documents", fake_search_documents
    )
    monkeypatch.setattr(
        rag_service, "generate_response", fake_generate_response
    )

    result = asyncio.run(
        rag_service.answer_question("How many annual leave days?")
    )

    assert result["reply"] == (
        "The policy provides 20 days of annual leave."
    )
    assert result["sources"] == [
        {"filename": "unknown", "chunk_index": -1}
    ]
    assert result["retrieved_chunks"] == 1


def test_duplicate_source_citations_are_deduplicated(monkeypatch):
    def fake_embed_text(text, *, is_query=False):
        return [0.1, 0.2]

    def fake_search_documents(embedding, limit):
        return [
            {
                "id": "chunk-1",
                "text": "Annual leave is 20 days.",
                "metadata": {
                    "source": "employee_policy.pdf",
                    "chunk_index": 0,
                },
                "distance": 0.10,
            },
            {
                "id": "chunk-1-copy",
                "text": "Annual leave is 20 days.",
                "metadata": {
                    "source": "employee_policy.pdf",
                    "chunk_index": 0,
                },
                "distance": 0.12,
            },
        ]

    async def fake_generate_response(message, context="", history=None):
        return "Annual leave is 20 days."

    monkeypatch.setattr(rag_service, "embed_text", fake_embed_text)
    monkeypatch.setattr(
        rag_service, "search_documents", fake_search_documents
    )
    monkeypatch.setattr(
        rag_service, "generate_response", fake_generate_response
    )

    result = asyncio.run(
        rag_service.answer_question("How many annual leave days?")
    )

    assert result["sources"] == [
        {"filename": "employee_policy.pdf", "chunk_index": 0}
    ]
    assert result["retrieved_chunks"] == 2
