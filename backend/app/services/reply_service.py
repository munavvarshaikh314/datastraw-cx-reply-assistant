
from datetime import datetime, timezone
from time import perf_counter
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.guardrails import GuardrailService
from app.ai.prompts import (
    build_reply_system_prompt,
    build_reply_user_prompt,
)
from app.core.config import settings
from app.db.models.conversation import Conversation
from app.db.models.reply_generation import ReplyGeneration
from app.db.repositories.reply_generation import ReplyGenerationRepository
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService


class ReplyService:
    """Orchestrates retrieval, guardrails, LLM generation, and persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()
        self.guardrail_service = GuardrailService()
        self.repository = ReplyGenerationRepository(session)

    async def generate_reply(
        self,
        conversation: Conversation,
        agent_id: UUID,
        customer_message: str,
    ) -> ReplyGeneration:
        """Generate and persist a grounded customer-support reply."""

        # 1. Validate customer input
        guardrail_result = (
            self.guardrail_service.validate_customer_message(
                customer_message
            )
        )

        if not guardrail_result.allowed:
            raise ValueError(
                guardrail_result.reason
                or "Customer message failed validation."
            )

        started_at = perf_counter()

        # 2. Retrieve brand-specific knowledge
        context = await self.retrieval_service.retrieve(
            query=customer_message,
            brand_id=conversation.brand_id,
        )

        # 3. Build grounded prompt
        system_prompt = build_reply_system_prompt()

        user_prompt = build_reply_user_prompt(
            customer_message=customer_message,
            context=context,
        )

        # 4. Generate response
        ai_response = await self.llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # 5. Validate generated response
        generated_guardrail = (
            self.guardrail_service.validate_generated_reply(
                ai_response
            )
        )

        if not generated_guardrail.allowed:
            raise ValueError(
                generated_guardrail.reason
                or "Generated reply failed validation."
            )

        latency_ms = int(
            (perf_counter() - started_at) * 1000
        )

        # 6. Determine generation number
        generation_number = (
            await self.repository.get_next_generation_number(
                conversation.id
            )
        )

        # 7. Create generation
        generation = ReplyGeneration(
            conversation_id=conversation.id,
            agent_id=agent_id,
            generation_number=generation_number,
            customer_message=customer_message,
            retrieved_context=context,
            ai_response=ai_response,
            status="generated",
            model=settings.openrouter_model,
            latency_ms=latency_ms,
        )

        # 8. Persist generation
        await self.repository.create(generation)

        await self.session.flush()

        return generation

    async def update_reply(
        self,
        generation: ReplyGeneration,
        edited_response: str,
    ) -> ReplyGeneration:
        """Edit a generated reply before approval."""

        if generation.status == "approved":
            raise ValueError(
                "Approved replies cannot be edited."
            )

        generated_guardrail = (
            self.guardrail_service.validate_generated_reply(
                edited_response
            )
        )

        if not generated_guardrail.allowed:
            raise ValueError(
                generated_guardrail.reason
                or "Edited reply failed validation."
            )

        generation.edited_response = edited_response
        generation.status = "edited"

        await self.session.flush()

        return generation

    async def approve_reply(
        self,
        generation: ReplyGeneration,
    ) -> ReplyGeneration:
        """Approve a reply and make it final."""

        if generation.status == "approved":
            raise ValueError(
                "Reply is already approved."
            )

        final_response = (
            generation.edited_response
            or generation.ai_response
        )

        if not final_response:
            raise ValueError(
                "Reply has no response to approve."
            )

        generated_guardrail = (
            self.guardrail_service.validate_generated_reply(
                final_response
            )
        )

        if not generated_guardrail.allowed:
            raise ValueError(
                generated_guardrail.reason
                or "Final reply failed validation."
            )

        generation.final_response = final_response
        generation.status = "approved"
        generation.approved_at = datetime.now(timezone.utc)

        await self.session.flush()

        return generation
