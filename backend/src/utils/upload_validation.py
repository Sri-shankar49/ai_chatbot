
from fastapi import HTTPException, UploadFile

MAX_UPLOAD_SIZE = 5 * 1024 * 1024


async def read_upload_with_limit(file: UploadFile) -> bytes:
    content = await file.read(MAX_UPLOAD_SIZE + 1)

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 5 MiB upload limit.",
        )

    return content
