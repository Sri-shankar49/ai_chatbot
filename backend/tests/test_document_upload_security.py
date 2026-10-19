
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from controllers import document_controller as controller


@pytest.mark.anyio
async def test_rejects_unsupported_extension(monkeypatch):
    file = UploadFile(
        filename="notes.exe",
        file=BytesIO(b"not allowed"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await controller.handle_document_upload(file)

    assert exc_info.value.status_code == 400


@pytest.mark.anyio
async def test_rejects_empty_file(monkeypatch):
    file = UploadFile(
        filename="empty.txt",
        file=BytesIO(b""),
    )

    with pytest.raises(HTTPException) as exc_info:
        await controller.handle_document_upload(file)

    assert exc_info.value.status_code == 400
    assert "empty" in exc_info.value.detail.lower()


@pytest.mark.anyio
async def test_rejects_invalid_utf8_without_embedding(monkeypatch):
    def unexpected_embed(*args, **kwargs):
        pytest.fail("Embedding must not run for invalid text")

    monkeypatch.setattr(controller, "embed_text", unexpected_embed)

    file = UploadFile(
        filename="invalid.txt",
        file=BytesIO(b"\xff\xfe\xfa"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await controller.handle_document_upload(file)

    assert exc_info.value.status_code == 400


@pytest.mark.anyio
async def test_rejects_binary_content_in_txt(monkeypatch):
    def unexpected_embed(*args, **kwargs):
        pytest.fail("Embedding must not run for binary content")

    monkeypatch.setattr(controller, "embed_text", unexpected_embed)

    file = UploadFile(
        filename="binary.txt",
        file=BytesIO(b"hello\x00world"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await controller.handle_document_upload(file)

    assert exc_info.value.status_code == 400
    assert "binary" in exc_info.value.detail.lower()


@pytest.mark.anyio
async def test_rejects_malformed_pdf_without_embedding(monkeypatch):
    def unexpected_embed(*args, **kwargs):
        pytest.fail("Embedding must not run for malformed PDF")

    monkeypatch.setattr(controller, "embed_text", unexpected_embed)

    file = UploadFile(
        filename="invalid.pdf",
        file=BytesIO(b"This is not a PDF document"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await controller.handle_document_upload(file)

    assert exc_info.value.status_code == 400


@pytest.mark.anyio
async def test_valid_txt_uses_embedding_and_storage(monkeypatch):
    embedded_texts = []
    stored_documents = []

    def fake_embed(text, *args, **kwargs):
        embedded_texts.append(text)
        return [0.1, 0.2, 0.3]

    def fake_add_document(**kwargs):
        stored_documents.append(kwargs)

    monkeypatch.setattr(controller, "embed_text", fake_embed)
    monkeypatch.setattr(controller, "add_document", fake_add_document)

    file = UploadFile(
        filename="notes.txt",
        file=BytesIO(b"Employees receive 20 days of annual leave."),
    )

    result = await controller.handle_document_upload(file)

    assert result.filename == "notes.txt"
    assert result.chunks_stored == 1
    assert len(embedded_texts) == 1
    assert len(stored_documents) == 1
    assert stored_documents[0]["source"] == "notes.txt"
