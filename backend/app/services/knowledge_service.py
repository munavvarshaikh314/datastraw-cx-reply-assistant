from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import EmbeddingService
from app.ai.qdrant import QdrantService
from app.db.models.knowledge_document import KnowledgeDocument
from app.db.repositories.knowledge import KnowledgeRepository


class KnowledgeService:
    """Application logic for brand knowledge and RAG indexing."""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = KnowledgeRepository(session)
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    async def get_brand_knowledge(
        self,
        brand_id: UUID,
    ) -> list[KnowledgeDocument]:
        """Return all knowledge documents belonging to a brand."""

        return await self.repository.get_by_brand(brand_id)

    async def get_policy(
        self,
        brand_id: UUID,
        document_type: str,
    ) -> KnowledgeDocument | None:
        """Return the latest version of a specific brand policy."""

        return await self.repository.get_latest_by_type(
            brand_id=brand_id,
            document_type=document_type,
        )

    async def index_document(
        self,
        document: KnowledgeDocument,
    ) -> None:
        """Create an embedding and index a knowledge document in Qdrant."""

        vector = await self.embedding_service.embed(
            document.content
        )

        payload = {
            "document_id": str(document.id),
            "brand_id": str(document.brand_id),
            "document_type": document.document_type,
            "title": document.title,
            "content": document.content,
            "version": document.version,
        }

        await self.qdrant_service.upsert(
            point_id=document.id,
            vector=vector,
            payload=payload,
        )

    async def index_brand_knowledge(
        self,
        brand_id: UUID,
    ) -> int:
        """Index all knowledge documents for a brand."""

        documents = await self.get_brand_knowledge(brand_id)

        for document in documents:
            await self.index_document(document)

        return len(documents)