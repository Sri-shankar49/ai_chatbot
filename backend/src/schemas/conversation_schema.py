
from pydantic import BaseModel, Field
from typing import Any
from pydantic import BaseModel

class ConversationCreate(BaseModel):
    title: str = Field(
        default="New conversation",
        min_length=1,
        max_length=100,
    )


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str
    sources: list[dict[str, Any]] = []


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int | None = None
