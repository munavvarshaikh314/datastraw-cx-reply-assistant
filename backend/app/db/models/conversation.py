from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.brand import Brand
    from app.db.models.customer import Customer
    from app.db.models.message import Message
    from app.db.models.order import Order


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    brand_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "brands.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "customers.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
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

    brand: Mapped["Brand"] = relationship(
    "Brand",
    back_populates="conversations",
    lazy="selectin",
   )

    customer: Mapped["Customer"] = relationship(
    "Customer",
    back_populates="conversations",
    lazy="selectin",
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        order_by="Message.created_at",
        lazy="selectin",
    )

    order: Mapped["Order | None"] = relationship(
        "Order",
        back_populates="conversation",
        uselist=False,
        lazy="selectin",
    )