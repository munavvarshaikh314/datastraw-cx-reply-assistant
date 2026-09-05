from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.conversation import Conversation
from app.db.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Database access for customer conversations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Conversation)

    async def get_with_context(
        self,
        conversation_id: UUID,
    ) -> Conversation | None:
        """
        Load a conversation with all information required
        by the CX Reply Assistant.
        """

        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .options(
                selectinload(Conversation.customer),
                selectinload(Conversation.brand),
                selectinload(Conversation.order),
                selectinload(Conversation.messages),
            )
        )

        return result.scalar_one_or_none()

    async def list_conversations(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> list[Conversation]:
        """Return conversations for the agent workspace."""

        query = (
            select(Conversation)
            .options(
                selectinload(Conversation.customer),
                selectinload(Conversation.brand),
            )
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if status:
            query = query.where(
                Conversation.status == status
            )

        result = await self.session.execute(query)

        return list(result.scalars().all())
