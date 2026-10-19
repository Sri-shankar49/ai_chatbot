
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    filename: str
    chunks_stored: int
    message: str
