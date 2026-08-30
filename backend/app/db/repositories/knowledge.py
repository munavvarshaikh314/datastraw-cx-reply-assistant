from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.knowledge_document import KnowledgeDocument
from app.db.repositories.base import BaseRepository


class KnowledgeRepository(BaseRepository[KnowledgeDocument]):
    """Database access for brand knowledge documents."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, KnowledgeDocument)

    async def get_by_brand(
        self,
        brand_id: UUID,
    ) -> list[KnowledgeDocument]:
        """Return all knowledge documents for a brand."""

        result = await self.session.execute(
            select(KnowledgeDocument)
            .where(
                KnowledgeDocument.brand_id == brand_id
            )
            .order_by(
                KnowledgeDocument.document_type,
                desc(KnowledgeDocument.version),
            )
        )

        return list(result.scalars().all())

    async def get_latest_by_type(
        self,
        brand_id: UUID,
        document_type: str,
    ) -> KnowledgeDocument | None:
        """Return the latest version of one policy type."""

        result = await self.session.execute(
            select(KnowledgeDocument)
            .where(
                KnowledgeDocument.brand_id == brand_id,
                KnowledgeDocument.document_type == document_type,
            )
            .order_by(
                desc(KnowledgeDocument.version)
            )
            .limit(1)
        )

        return result.scalar_one_or_none()