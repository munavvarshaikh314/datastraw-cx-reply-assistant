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

        try:
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
        except Exception:
            if settings.environment != "production":
                return self._development_fallback_reply(user_prompt)

            raise

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("LLM returned an empty response")

        return content.strip()

    @staticmethod
    def _development_fallback_reply(user_prompt: str) -> str:
        if "Action: do_not_promise" in user_prompt:
            return (
                "I am sorry your order arrived damaged. I can help get this "
                "reviewed, but I cannot promise a refund or replacement until "
                "the order details and brand policy are confirmed. Please share "
                "photos of the damage and packaging, and our support team will "
                "review the next available option."
            )

        return (
            "Thank you for reaching out. I reviewed the conversation and the "
            "available brand policy context, and our support team can help with "
            "the next step. Please confirm any missing order details so we can "
            "handle this accurately."
        )
