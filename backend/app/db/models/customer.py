from datetime import datetime
from uuid import UUID
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship


from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
if TYPE_CHECKING:
    from app.db.models.conversation import Conversation

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(320),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    
    conversations: Mapped[list["Conversation"]] = relationship(
    "Conversation",
    back_populates="customer",
)