from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ReplyGenerateRequest(BaseModel):
    customer_message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )
    agent_id: UUID


class ReplyUpdateRequest(BaseModel):
    edited_response: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )
    
class ReplyEditRequest(BaseModel):
    edited_response: str = Field(
        ...,
        min_length=1,
        max_length=20000,
    )


class ReplyApproveRequest(BaseModel):
    pass


class ReplyGenerationResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    generation_number: int
    customer_message: str
    retrieved_context: dict[str, Any] | list[Any]
    ai_response: str | None
    edited_response: str | None
    final_response: str | None
    status: str
    model: str | None
    latency_ms: int | None
    created_at: datetime
    approved_at: datetime | None

    model_config = {
        "from_attributes": True,
    }
