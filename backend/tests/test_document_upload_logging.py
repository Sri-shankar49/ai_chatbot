
from io import BytesIO
from unittest.mock import Mock

from fastapi.testclient import TestClient

from main import app
from controllers import document_controller as controller

client = TestClient(app)


def test_rollback_failure_is_logged_without_exposing_details(
    monkeypatch,
):
    logger_exception = Mock()

    monkeypatch.setattr(
        controller.logger,
        "exception",
        logger_exception,
    )
    monkeypatch.setattr(
        controller,
        "embed_text",
        lambda text: [0.1] * 768,
    )
    monkeypatch.setattr(
        controller,
        "chunk_text",
        lambda text: ["Example policy content"],
    )

    def fail_storage(**kwargs):
        raise RuntimeError("Internal storage details")

    def fail_rollback(document_ids):
        raise RuntimeError("Internal rollback details")

    monkeypatch.setattr(
        controller,
        "add_document",
        fail_storage,
    )
    monkeypatch.setattr(
        controller,
        "delete_documents",
        fail_rollback,
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

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Failed to store document chunks."
    )

    response_text = response.text
    assert "Internal storage details" not in response_text
    assert "Internal rollback details" not in response_text

    assert logger_exception.call_count == 2
