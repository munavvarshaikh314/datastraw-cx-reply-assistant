from uuid import UUID

from app.ai.embeddings import EmbeddingService
from app.ai.qdrant import QdrantService
from app.core.config import settings


class RetrievalService:
    """Retrieves brand-specific knowledge from Qdrant."""

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        qdrant_service: QdrantService | None = None,
    ) -> None:
        self.embedding_service = (
            embedding_service or EmbeddingService()
        )
        self.qdrant_service = (
            qdrant_service or QdrantService()
        )

    async def retrieve(
        self,
        query: str,
        brand_id: UUID,
        top_k: int | None = None,
    ) -> list[dict]:
        """Retrieve relevant knowledge for a brand."""

        if not query.strip():
            return []

        vector = await self.embedding_service.embed(query)

        results = await self.qdrant_service.search(
            vector=vector,
            limit=top_k or settings.rag_top_k,
            brand_id=brand_id,
        )

        relevant_results = []

        for result in results:
            if result.score < settings.rag_relevance_threshold:
                continue

            payload = result.payload or {}

            relevant_results.append(
                {
                    "id": str(result.id),
                    "score": result.score,
                    "title": payload.get("title"),
                    "content": payload.get("content"),
                    "document_type": payload.get("document_type"),
                    "brand_id": payload.get("brand_id"),
                    "version": payload.get("version"),
                }
            )

        return relevant_results