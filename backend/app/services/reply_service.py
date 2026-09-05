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
from app.db.repositories.knowledge import KnowledgeRepository
from app.db.repositories.reply_generation import ReplyGenerationRepository
from app.services.eligibility import check_refund_eligibility
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService


class ReplyService:
    """Orchestrates retrieval, eligibility guardrails,
    LLM generation, and persistence.
    """

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

        # ---------------------------------------------------------
        # 1. Validate customer input
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 2. Retrieve brand-specific knowledge
        # ---------------------------------------------------------

        context = await self._retrieve_context(
            query=customer_message,
            conversation=conversation,
        )

        # ---------------------------------------------------------
        # 3. Extract refund policy from retrieved KB
        # ---------------------------------------------------------

        refund_window_days = self._extract_refund_window(context)

        # ---------------------------------------------------------
        # 4. Deterministic eligibility check
        # ---------------------------------------------------------

        order = conversation.order

        eligibility = check_refund_eligibility(
            customer_message=customer_message,
            delivery_date=order.delivery_date if order else None,
            refund_window_days=refund_window_days,
        )

        # ---------------------------------------------------------
        # 5. Add deterministic verdict to audit context
        # ---------------------------------------------------------

        eligibility_verdict = {
            "applicable": eligibility.applicable,
            "eligible": eligibility.eligible,
            "reason": eligibility.reason,
            "action": eligibility.action,
            "refund_window_days": eligibility.refund_window_days,
            "days_since_delivery": eligibility.days_since_delivery,
        }

        audit_context = {
            "documents": context,
            "eligibility_verdict": eligibility_verdict,
        }

        # ---------------------------------------------------------
        # 6. Build grounded prompt
        # ---------------------------------------------------------

        system_prompt = build_reply_system_prompt()

        user_prompt = build_reply_user_prompt(
            customer_message=customer_message,
            context=audit_context,
        )

        # ---------------------------------------------------------
        # 7. Generate AI response
        # ---------------------------------------------------------

        ai_response = await self.llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # ---------------------------------------------------------
        # 8. Validate generated response
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # 9. Determine generation number
        # ---------------------------------------------------------

        generation_number = (
            await self.repository.get_next_generation_number(
                conversation.id
            )
        )

        # ---------------------------------------------------------
        # 10. Persist generation + complete audit context
        # ---------------------------------------------------------

        generation = ReplyGeneration(
            conversation_id=conversation.id,
            agent_id=agent_id,
            generation_number=generation_number,
            customer_message=customer_message,
            retrieved_context=audit_context,
            ai_response=ai_response,
            status="generated",
            model=settings.openrouter_model,
            latency_ms=latency_ms,
        )

        await self.repository.create(generation)

        await self.session.flush()

        return generation

    async def _retrieve_context(
        self,
        query: str,
        conversation: Conversation,
    ) -> list[dict]:
        try:
            context = await self.retrieval_service.retrieve(
                query=query,
                brand_id=conversation.brand_id,
            )

            if context:
                return context
        except Exception:
            pass

        knowledge_repository = KnowledgeRepository(self.session)
        documents = await knowledge_repository.get_by_brand(
            conversation.brand_id
        )

        return [
            {
                "id": str(document.id),
                "score": None,
                "title": document.title,
                "content": document.content,
                "document_type": document.document_type,
                "brand_id": str(document.brand_id),
                "version": document.version,
                "source": "postgresql",
            }
            for document in documents
        ]

    @staticmethod
    def _extract_refund_window(
        context: list[dict],
    ) -> int:
        """
        Extract the refund window from retrieved brand knowledge.

        For the assignment, the KB should contain a numeric refund
        window such as 7 days.
        """

        for item in context:
            content = item.get("content", "").lower()

            if "refund" not in content:
                continue

            import re

            match = re.search(
                r"(\d+)\s*[-]?\s*day",
                content,
            )

            if match:
                return int(match.group(1))

        # No policy window found.
        # Returning 0 means the deterministic check will not
        # promise eligibility.
        return 0

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
