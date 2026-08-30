from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_type: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationListItem(BaseModel):
    id: UUID
    brand_id: UUID
    customer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: UUID
    brand_id: UUID
    customer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    messages: list[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)