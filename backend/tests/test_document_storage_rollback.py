import pytest

from fastapi import HTTPException
from fastapi import UploadFile
from io import BytesIO

from controllers import document_controller as controller


@pytest.mark.asyncio
# async def test_storage_failure_rolls_back_previously_stored_chunks(
async def test_storage_failure_rolls_back_previously_stored_chunks(
    monkeypatch,
):
    stored_ids = []
    deleted_ids = []

    def fake_embed_text(text):
        # return [0.1] * controller.EMBEDDING_DIMENSIONS
        return [0.1] * 768

    def fake_add_document(
        document_id,
        text,
        embedding,
        source,
        chunk_index,
    ):
        if chunk_index == 1:
            raise RuntimeError("Simulated storage failure")

        stored_ids.append(document_id)

    def fake_delete_documents(document_ids):
        deleted_ids.extend(document_ids)

    monkeypatch.setattr(controller, "embed_text", fake_embed_text)
    monkeypatch.setattr(controller, "add_document", fake_add_document)
    monkeypatch.setattr(
        controller,
        "delete_documents",
        fake_delete_documents,
    )
    monkeypatch.setattr(
        controller,
        "chunk_text",
        lambda text: ["First chunk", "Second chunk"],
    )

    upload = UploadFile(
        filename="policy.txt",
        file=BytesIO(b"Example policy content"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await controller.handle_document_upload(upload)

    assert exc_info.value.status_code == 500
    assert len(stored_ids) == 1
    assert deleted_ids == stored_ids


@pytest.mark.asyncio
async def test_empty_rollback_does_not_delete_anything(monkeypatch):
    deleted_ids = []

    monkeypatch.setattr(
        controller,
        "embed_text",
        lambda text: [0.1] * 768,
    )
    monkeypatch.setattr(
        controller,
        "add_document",
        lambda **kwargs: (_ for _ in ()).throw(
            RuntimeError("Simulated first-write failure")
        ),
    )
    monkeypatch.setattr(
        controller,
        "delete_documents",
        lambda ids: deleted_ids.extend(ids),
    )
    monkeypatch.setattr(
        controller,
        "chunk_text",
        lambda text: ["First chunk"],
    )

    upload = UploadFile(
        filename="policy.txt",
        file=BytesIO(b"Example policy content"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await controller.handle_document_upload(upload)

    assert exc_info.value.status_code == 500
    assert deleted_ids == []
    
    

@pytest.mark.asyncio
async def test_rollback_failure_still_returns_http_500(monkeypatch):
    def fake_add_document(**kwargs):
        raise RuntimeError("Simulated storage failure")

    def fake_delete_documents(document_ids):
        raise RuntimeError("Simulated rollback failure")

    monkeypatch.setattr(
        controller,
        "embed_text",
        lambda text: [0.1] * 768,
    )
    monkeypatch.setattr(
        controller,
        "add_document",
        fake_add_document,
    )
    monkeypatch.setattr(
        controller,
        "delete_documents",
        fake_delete_documents,
    )
    monkeypatch.setattr(
        controller,
        "chunk_text",
        lambda text: ["First chunk"],
    )

    upload = UploadFile(
        filename="policy.txt",
        file=BytesIO(b"Example policy content"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await controller.handle_document_upload(upload)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Failed to store document chunks."