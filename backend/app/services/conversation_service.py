from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.conversation import ConversationRepository


class ConversationService:
    """Application logic for customer conversations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = ConversationRepository(session)

    async def get_conversation(
        self,
        conversation_id: UUID,
    ):
        """
        Return a conversation together with its customer,
        brand, order, and message history.
        """

        conversation = await self.repository.get_with_context(
            conversation_id
        )

        if conversation is None:
            raise ValueError(
                f"Conversation {conversation_id} not found"
            )

        return conversation