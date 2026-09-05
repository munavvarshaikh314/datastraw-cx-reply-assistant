from dataclasses import dataclass
from datetime import date, datetime, timezone


@dataclass
class EligibilityVerdict:
    applicable: bool
    eligible: bool | None
    reason: str
    action: str
    refund_window_days: int | None = None
    days_since_delivery: int | None = None


REFUND_KEYWORDS = (
    "refund",
    "money back",
    "get my money",
    "return my money",
)

DAMAGE_KEYWORDS = (
    "arrived damaged",
    "damaged",
    "broken",
    "defective",
    "faulty",
    "not working",
    "cracked",
)


def _contains_any(message: str, keywords: tuple[str, ...]) -> bool:
    text = message.lower()
    return any(keyword in text for keyword in keywords)


def check_refund_eligibility(
    customer_message: str,
    delivery_date: date | datetime | None,
    refund_window_days: int,
    today: date | None = None,
) -> EligibilityVerdict:
    """Return a deterministic audit verdict for refund-sensitive replies."""

    is_refund_request = _contains_any(customer_message, REFUND_KEYWORDS)
    is_damage_report = _contains_any(customer_message, DAMAGE_KEYWORDS)

    if not is_refund_request and not is_damage_report:
        return EligibilityVerdict(
            applicable=False,
            eligible=None,
            reason="Customer message is not refund or damaged-order related.",
            action="normal_ai_response",
        )

    if is_damage_report and not is_refund_request:
        return EligibilityVerdict(
            applicable=True,
            eligible=None,
            reason=(
                "Customer reported a damaged order but did not explicitly "
                "request a refund. Do not promise a refund or replacement "
                "before human review confirms the remedy."
            ),
            action="do_not_promise",
            refund_window_days=refund_window_days or None,
            days_since_delivery=_days_since_delivery(delivery_date, today),
        )

    if refund_window_days <= 0:
        return EligibilityVerdict(
            applicable=True,
            eligible=None,
            reason="No refund policy window was found in retrieved brand knowledge.",
            action="do_not_promise",
            refund_window_days=None,
            days_since_delivery=_days_since_delivery(delivery_date, today),
        )

    if delivery_date is None:
        return EligibilityVerdict(
            applicable=True,
            eligible=None,
            reason="Delivery date is unavailable.",
            action="do_not_promise",
            refund_window_days=refund_window_days,
        )

    days_since_delivery = _days_since_delivery(delivery_date, today)

    if days_since_delivery is None:
        return EligibilityVerdict(
            applicable=True,
            eligible=None,
            reason="Delivery date is unavailable.",
            action="do_not_promise",
            refund_window_days=refund_window_days,
        )

    if days_since_delivery < 0:
        return EligibilityVerdict(
            applicable=True,
            eligible=None,
            reason="Delivery date is in the future.",
            action="do_not_promise",
            refund_window_days=refund_window_days,
            days_since_delivery=days_since_delivery,
        )

    if days_since_delivery <= refund_window_days:
        return EligibilityVerdict(
            applicable=True,
            eligible=True,
            reason=(
                f"Order was delivered {days_since_delivery} days ago, "
                f"within the {refund_window_days}-day refund window."
            ),
            action="may_offer_refund",
            refund_window_days=refund_window_days,
            days_since_delivery=days_since_delivery,
        )

    return EligibilityVerdict(
        applicable=True,
        eligible=False,
        reason=(
            f"Order was delivered {days_since_delivery} days ago, "
            f"outside the {refund_window_days}-day refund window."
        ),
        action="do_not_promise",
        refund_window_days=refund_window_days,
        days_since_delivery=days_since_delivery,
    )


def _days_since_delivery(
    delivery_date: date | datetime | None,
    today: date | None,
) -> int | None:
    if delivery_date is None:
        return None

    if isinstance(delivery_date, datetime):
        delivery_date = delivery_date.date()

    if today is None:
        today = datetime.now(timezone.utc).date()

    return (today - delivery_date).days
