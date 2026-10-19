
import pytest
from fastapi import HTTPException, UploadFile
from io import BytesIO

from src.utils.upload_validation import read_upload_with_limit


@pytest.mark.anyio
async def test_upload_at_size_limit_is_accepted():
    file = UploadFile(
        filename="notes.txt",
        file=BytesIO(b"a" * (5 * 1024 * 1024)),
    )

    content = await read_upload_with_limit(file)

    assert len(content) == 5 * 1024 * 1024


@pytest.mark.anyio
async def test_upload_over_size_limit_is_rejected():
    file = UploadFile(
        filename="large.txt",
        file=BytesIO(b"a" * (5 * 1024 * 1024 + 1)),
    )

    with pytest.raises(HTTPException) as exc_info:
        await read_upload_with_limit(file)

    assert exc_info.value.status_code == 413
