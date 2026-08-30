from openai import AsyncOpenAI

from app.core.config import settings


class LLMService:
    """Service for generating customer-support replies through OpenRouter."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Generate a response from the configured LLM."""

        response = await self.client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("LLM returned an empty response")

        return content.strip()