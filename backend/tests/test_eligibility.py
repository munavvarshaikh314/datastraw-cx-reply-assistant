from datetime import date, timedelta

from app.services.eligibility import check_refund_eligibility


def test_damaged_order_message_does_not_promise_refund() -> None:
    verdict = check_refund_eligibility(
        customer_message="My order arrived damaged. What can you do?",
        delivery_date=date(2026, 8, 30),
        refund_window_days=7,
        today=date(2026, 9, 1),
    )

    assert verdict.applicable is True
    assert verdict.eligible is None
    assert verdict.action == "do_not_promise"


def test_explicit_refund_request_uses_policy_window() -> None:
    today = date(2026, 9, 1)

    verdict = check_refund_eligibility(
        customer_message="I want a refund for my order.",
        delivery_date=today - timedelta(days=3),
        refund_window_days=7,
        today=today,
    )

    assert verdict.applicable is True
    assert verdict.eligible is True
    assert verdict.action == "may_offer_refund"


def test_unrelated_message_is_not_applicable() -> None:
    verdict = check_refund_eligibility(
        customer_message="When will this ship?",
        delivery_date=None,
        refund_window_days=7,
        today=date(2026, 9, 1),
    )

    assert verdict.applicable is False
    assert verdict.eligible is None
    assert verdict.action == "normal_ai_response"
