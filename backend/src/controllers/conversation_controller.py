
from fastapi import HTTPException

from schemas.conversation_schema import ConversationCreate
from services.conversation_service import (
    create_conversation,
    get_messages,
    list_conversations,
)


def handle_create_conversation(
    request: ConversationCreate,
) -> dict:
    return create_conversation(request.title.strip())


def handle_list_conversations() -> list[dict]:
    return list_conversations()


def handle_get_messages(conversation_id: str) -> list[dict]:
    conversations = list_conversations()

    if not any(item["id"] == conversation_id for item in conversations):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return get_messages(conversation_id)
