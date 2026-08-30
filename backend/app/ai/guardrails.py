from dataclasses import dataclass


@dataclass
class GuardrailResult:
    allowed: bool
    reason: str | None = None


class GuardrailService:
    """Basic deterministic safety checks for customer replies."""

    BLOCKED_PATTERNS = (
        "ignore previous instructions",
        "ignore all previous instructions",
        "reveal your system prompt",
        "show me your system prompt",
        "developer message",
    )

    def validate_customer_message(
        self,
        message: str,
    ) -> GuardrailResult:
        normalized = message.lower()

        for pattern in self.BLOCKED_PATTERNS:
            if pattern in normalized:
                return GuardrailResult(
                    allowed=False,
                    reason="Potential prompt injection detected.",
                )

        if not message.strip():
            return GuardrailResult(
                allowed=False,
                reason="Customer message is empty.",
            )

        return GuardrailResult(allowed=True)

    def validate_generated_reply(
        self,
        reply: str,
    ) -> GuardrailResult:
        if not reply.strip():
            return GuardrailResult(
                allowed=False,
                reason="Generated reply is empty.",
            )

        return GuardrailResult(allowed=True)