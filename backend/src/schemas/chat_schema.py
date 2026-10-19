
# from pydantic import BaseModel, Field


# class ChatRequest(BaseModel):
#     message: str = Field(min_length=1, max_length=4000)
#     conversation_id: str | None = None



from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None

    @field_validator("conversation_id")
    @classmethod
    def validate_conversation_id(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        try:
            return str(UUID(value))
        except ValueError:
            raise ValueError(
                "conversation_id must be a valid UUID."
            ) from None
