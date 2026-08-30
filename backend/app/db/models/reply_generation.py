from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReplyGeneration(Base):
    __tablename__ = "reply_generations"

    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
            "generation_number",
            name="uq_reply_generation_conversation_number",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "conversations.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    agent_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "profiles.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    generation_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    customer_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    retrieved_context: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    ai_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    edited_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    final_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="generated",
    )

    model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    latency_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )