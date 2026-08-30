from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.reply_generation import ReplyGeneration
from app.db.repositories.base import BaseRepository


class ReplyGenerationRepository(BaseRepository[ReplyGeneration]):
    """Database access for AI reply generation and audit records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ReplyGeneration)

    async def get_latest_for_conversation(
        self,
        conversation_id: UUID,
    ) -> ReplyGeneration | None:
        """Return the most recent generation for a conversation."""

        result = await self.session.execute(
            select(ReplyGeneration)
            .where(
                ReplyGeneration.conversation_id == conversation_id
            )
            .order_by(
                desc(ReplyGeneration.generation_number)
            )
            .limit(1)
        )

        return result.scalar_one_or_none()

    async def get_next_generation_number(
        self,
        conversation_id: UUID,
    ) -> int:
        """Return the next generation number for a conversation."""

        latest = await self.get_latest_for_conversation(
            conversation_id
        )

        if latest is None:
            return 1

        return latest.generation_number + 1
    