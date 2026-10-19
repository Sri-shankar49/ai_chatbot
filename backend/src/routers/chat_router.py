
from fastapi import APIRouter

from controllers.chat_controller import handle_chat
from schemas.chat_schema import ChatRequest

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    return await handle_chat(request)
