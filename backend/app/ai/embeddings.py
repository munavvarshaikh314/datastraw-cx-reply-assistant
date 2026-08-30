from openai import AsyncOpenAI

from app.core.config import settings


class EmbeddingService:
    """Generate embeddings using an OpenAI-compatible API."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    async def embed(self, text: str) -> list[float]:
        """Generate an embedding for the supplied text."""

        response = await self.client.embeddings.create(
            model="openai/text-embedding-3-small",
            input=text,
        )

        return response.data[0].embedding