from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from app.core.config import settings


class QdrantService:
    """Infrastructure wrapper around Qdrant."""

    def __init__(self) -> None:
        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection

    async def ensure_collection(self) -> None:
        """Create the knowledge collection if it does not exist."""

        collections = await self.client.get_collections()

        exists = any(
            collection.name == self.collection_name
            for collection in collections.collections
        )

        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE,
                ),
            )
            
        await self.client.create_payload_index(
        collection_name=self.collection_name,
        field_name="brand_id",
        field_schema=models.PayloadSchemaType.KEYWORD,
    )    

    async def upsert(
        self,
        point_id: UUID,
        vector: list[float],
        payload: dict,
    ) -> None:
        """Insert or update a knowledge vector."""

        await self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=str(point_id),
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    async def search(
        self,
        vector: list[float],
        limit: int = 3,
        brand_id: UUID | None = None,
    ) -> list[models.ScoredPoint]:
        """Search for relevant knowledge vectors."""

        query_filter = None

        if brand_id is not None:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="brand_id",
                        match=models.MatchValue(
                            value=str(brand_id)
                        ),
                    )
                ]
            )

        response = await self.client.query_points(
        collection_name=self.collection_name,
        query=vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    )

        return response.points

    async def close(self) -> None:
        """Close the Qdrant connection."""

        await self.client.close()