
from io import BytesIO

from fastapi.testclient import TestClient

from main import app
from controllers import document_controller as controller

client = TestClient(app)


def test_upload_rejects_unsupported_extension():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "malware.exe",
                BytesIO(b"not allowed"),
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400


def test_upload_rejects_oversized_file(monkeypatch):
    def unexpected_embed(*args, **kwargs):
        raise AssertionError("Embedding must not run")

    monkeypatch.setattr(controller, "embed_text", unexpected_embed)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "large.txt",
                BytesIO(b"a" * (5 * 1024 * 1024 + 1)),
                "text/plain",
            )
        },
    )

    assert response.status_code == 413


def test_upload_success_returns_expected_response(monkeypatch):
    # Avoid calling the real Gemini API.
    monkeypatch.setattr(
        controller,
        "embed_text",
        lambda text: [0.1] * 768,
    )

    # Avoid modifying the real ChromaDB collection.
    stored_chunks = []

    def fake_add_document(
        document_id,
        text,
        embedding,
        source,
        chunk_index,
    ):
        stored_chunks.append(
            {
                "id": document_id,
                "text": text,
                "source": source,
                "chunk_index": chunk_index,
            }
        )

    monkeypatch.setattr(
        controller,
        "add_document",
        fake_add_document,
    )

    monkeypatch.setattr(
        controller,
        "chunk_text",
        lambda text: ["Example policy content"],
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "policy.txt",
                BytesIO(b"Example policy content"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["filename"] == "policy.txt"
    assert data["chunks_stored"] == 1
    assert data["message"] == "Document indexed successfully."

    assert len(stored_chunks) == 1
    assert stored_chunks[0]["text"] == "Example policy content"
    
    

def test_upload_embedding_failure_returns_502(monkeypatch):
    def fail_embedding(text):
        raise RuntimeError("Simulated embedding failure")

    def unexpected_storage(**kwargs):
        raise AssertionError(
            "Storage must not run when embedding generation fails"
        )

    monkeypatch.setattr(
        controller,
        "embed_text",
        fail_embedding,
    )
    monkeypatch.setattr(
        controller,
        "add_document",
        unexpected_storage,
    )
    monkeypatch.setattr(
        controller,
        "chunk_text",
        lambda text: ["Example policy content"],
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "policy.txt",
                BytesIO(b"Example policy content"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "Embedding generation failed. "
        "Check the Google API configuration and quota."
    )
