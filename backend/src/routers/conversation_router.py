
from fastapi import APIRouter

from controllers.conversation_controller import (
    handle_create_conversation,
    handle_get_messages,
    handle_list_conversations,
)
from schemas.conversation_schema import (
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post("", response_model=ConversationResponse)
def create_conversation_endpoint(request: ConversationCreate):
    return handle_create_conversation(request)


@router.get("", response_model=list[ConversationResponse])
def list_conversations_endpoint():
    return handle_list_conversations()


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_conversation_messages(conversation_id: str):
    return handle_get_messages(conversation_id)
