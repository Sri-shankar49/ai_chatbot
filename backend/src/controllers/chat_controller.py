
from fastapi import HTTPException
from groq import APIError, AuthenticationError, RateLimitError

from schemas.chat_schema import ChatRequest
from services.conversation_service import (
    add_message,
    create_conversation,
    get_messages,
)
from services.groq_service import generate_response
from services.rag_service import answer_question

import logging

logger = logging.getLogger(__name__)

# async def handle_chat(request: ChatRequest) -> dict:
#     message = request.message.strip()

#     if not message:
#         raise HTTPException(
#             status_code=400,
#             detail="Please enter a message.",
#         )

#     try:
#         reply = await generate_response(message)
#         return {"reply": reply}

#     except AuthenticationError:
#         raise HTTPException(
#             status_code=502,
#             detail="Groq authentication failed.",
#         ) from None

#     except RateLimitError:
#         raise HTTPException(
#             status_code=429,
#             detail="Groq rate limit reached.",
#         ) from None

#     except APIError:
#         raise HTTPException(
#             status_code=502,
#             detail="The Groq API request failed.",
#         ) from None

#     except RuntimeError:
#         raise HTTPException(
#             status_code=500,
#             detail="Groq configuration is missing.",
#         ) from None




# async def handle_chat(request: ChatRequest) -> dict:
#     message = request.message.strip()

#     if not message:
#         raise HTTPException(
#             status_code=400,
#             detail="Please enter a message.",
#         )

#     try:
#         return await answer_question(message)

#     except AuthenticationError:
#         raise HTTPException(
#             status_code=502,
#             detail="Groq authentication failed.",
#         ) from None

#     except RateLimitError:
#         raise HTTPException(
#             status_code=429,
#             detail="Groq rate limit reached.",
#         ) from None

#     except APIError:
#         raise HTTPException(
#             status_code=502,
#             detail="The Groq API request failed.",
#         ) from None

#     except RuntimeError:
#         raise HTTPException(
#             status_code=500,
#             detail="An AI service configuration error occurred.",
#         ) from None

#     # except Exception:
#     #     raise HTTPException(
#     #         status_code=502,
#     #         detail="The AI request failed. Check the backend logs.",
#     #     ) from None

#     except Exception:
#         logger.exception("Unexpected error while processing chat request")
#         raise HTTPException(
#             status_code=500,
#             detail="An unexpected server error occurred.",
#         ) from None


async def handle_chat(request: ChatRequest) -> dict:
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Please enter a message.",
        )

    conversation_id = request.conversation_id

    try:
        if conversation_id:
            # Fetch previous messages before saving this new question.
            history = get_messages(conversation_id, limit=20)
            if not history and not any(
                item["id"] == conversation_id
                for item in __import__(
                    "src.services.conversation_service",
                    fromlist=["list_conversations"],
                ).list_conversations()
            ):
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found.",
                )
        else:
            conversation = create_conversation()
            conversation_id = conversation["id"]
            history = []

        add_message(conversation_id, "user", message)

        result = await answer_question(
            message,
            history=history,
        )

        add_message(
            conversation_id,
            "assistant",
            result["reply"],
            sources=result.get("sources", []),
        )

        return {
            **result,
            "conversation_id": conversation_id,
        }

    except HTTPException:
        raise

    except AuthenticationError:
        raise HTTPException(
            status_code=502,
            detail="Groq authentication failed.",
        ) from None

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Groq rate limit reached.",
        ) from None

    except APIError:
        logger.exception("Groq API request failed")
        raise HTTPException(
            status_code=502,
            detail="The Groq API request failed.",
        ) from None

    except Exception:
        logger.exception("Unexpected error processing chat request")
        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred.",
        ) from None