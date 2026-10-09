"""Structured complaint records. SYNTHETIC PLACEHOLDER DATA ONLY.

Each complaint belongs to exactly one customer (customer_id -> CUSTOMERS.id).
"""

from typing import Any

from data.enums import Channel, ComplaintStatus, ProductType, Severity

# complaints (product, channel, severity, status),
COMPLAINTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "customer_id": 1,
        "product": ProductType.credit_card,
        "channel": Channel.app,
        "severity": Severity.medium,
        "status": ComplaintStatus.resolved,
        "opened_date": "2026-08-14",
        "summary": (
            "Direct Debit set up two weeks before the due date but not "
            "applied in time; late payment fee charged and adverse marker "
            "reported to credit reference agency."
        ),
    },
    {
        "id": 2,
        "customer_id": 2,
        "product": ProductType.mortgage,
        "channel": Channel.phone,
        "severity": Severity.high,
        "status": ComplaintStatus.resolved,
        "opened_date": "2026-06-12",
        "summary": (
            "Arrears incorrectly reported to credit reference agency after "
            "a payment holiday that had been agreed in writing; customer "
            "has been chasing a correction for over three months."
        ),
    },
    {
        "id": 3,
        "customer_id": 3,
        "product": ProductType.current_account,
        "channel": Channel.branch,
        "severity": Severity.high,
        "status": ComplaintStatus.in_review,
        "opened_date": "2026-07-20",
        "summary": (
            "Account frozen following bereavement notification; customer "
            "unable to access joint funds for over five weeks despite "
            "providing probate documentation twice."
        ),
    },
    {
        "id": 4,
        "customer_id": 4,
        "product": ProductType.personal_loan,
        "channel": Channel.email,
        "severity": Severity.medium,
        "status": ComplaintStatus.resolved,
        "opened_date": "2026-05-03",
        "summary": (
            "Payment protection product sold at loan origination; customer "
            "self-employed at the time and would not have qualified to "
            "claim under the policy terms."
        ),
    },
    {
        "id": 5,
        "customer_id": 5,
        "product": ProductType.credit_card,
        "channel": Channel.webform,
        "severity": Severity.high,
        "status": ComplaintStatus.open,
        "opened_date": "2026-07-01",
        "summary": (
            "Repeated over-limit fees applied during a period of "
            "documented financial hardship; customer had contacted the "
            "hardship team but fees continued to be charged."
        ),
    },
    {
        "id": 6,
        "customer_id": 1,
        "product": ProductType.savings,
        "channel": Channel.app,
        "severity": Severity.low,
        "status": ComplaintStatus.resolved,
        "opened_date": "2026-09-10",
        "summary": (
            "Advertised introductory interest rate not applied for the "
            "first two months of the account; corrected on request but "
            "customer wants written confirmation and goodwill payment."
        ),
    },
    {
        "id": 7,
        "customer_id": 3,
        "product": ProductType.mortgage,
        "channel": Channel.phone,
        "severity": Severity.high,
        "status": ComplaintStatus.escalated,
        "opened_date": "2026-08-25",
        "summary": (
            "Late payment fee applied during the month following "
            "bereavement despite the account being flagged; customer "
            "asked for pause on collections activity twice."
        ),
    },
    {
        "id": 8,
        "customer_id": 6,
        "product": ProductType.current_account,
        "channel": Channel.app,
        "severity": Severity.medium,
        "status": ComplaintStatus.open,
        "opened_date": "2026-09-20",
        "summary": (
            "Authorised push payment disputed after customer was "
            "contacted by someone claiming to be from the bank's fraud "
            "team; bank declined initial reimbursement request."
        ),
    },
]


def get_complaint(complaint_id: int) -> dict[str, Any] | None:
    """Pure lookup. Returns the complaint dict or None"""
    return next((c for c in COMPLAINTS if c["id"] == complaint_id), None)
