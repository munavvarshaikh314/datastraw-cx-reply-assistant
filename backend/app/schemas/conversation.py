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


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    email: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BrandResponse(BaseModel):
    id: UUID
    name: str
    slug: str

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    order_number: str
    product_name: str
    status: str
    delivery_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ConversationListItem(BaseModel):
    id: UUID
    brand_id: UUID
    customer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    customer: CustomerResponse | None = None
    brand: BrandResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: UUID
    brand_id: UUID
    customer_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    customer: CustomerResponse | None = None
    brand: BrandResponse | None = None
    order: OrderResponse | None = None
    messages: list[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)
