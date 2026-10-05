"""Pydantic schemas for complaint analysis (LLM structured output).

Enums here describe LLM analysis output, not stored complaint records.
Stored-record enums live in data/enums.py.
"""

from enum import Enum

from pydantic import BaseModel, Field

from data.enums import Severity


class Theme(str, Enum):
    bereavement = "bereavement"
    hardship = "hardship"
    fraud = "fraud"
    mis_selling = "mis_selling"
    credit_reporting = "credit_reporting"
    fees = "fees"
    service_failure = "service_failure"
    misleading_comms = "misleading_comms"
    other = "other"


THEME_DESCRIPTIONS: dict[Theme, str] = {
    Theme.bereavement: (
        "Customer has notified the bank of a death. Covers frozen accounts, "
        "probate delays, fees or collections activity continuing after notification, "
        "and failures to apply bereavement handling."
    ),
    Theme.hardship: (
        "Customer is in documented financial difficulty. Covers fees, charges or "
        "collections activity applied during a period of hardship the bank was "
        "aware of, and failure to apply forbearance."
    ),
    Theme.fraud: (
        "Disputed transactions, authorised push payment (APP) scams, card fraud, "
        "impersonation of bank staff. Includes reimbursement decisions under the "
        "CRM code."
    ),
    Theme.mis_selling: (
        "Product sold to a customer for whom it was not suitable or who could not "
        "have benefited from it. Covers PPI, unsuitable investments, and "
        "target-market or fair-value failures."
    ),
    Theme.credit_reporting: (
        "Incorrect or disputed data reported to a credit reference agency: "
        "arrears markers, defaults, late-payment flags, or failure to amend after "
        "an agreed correction."
    ),
    Theme.fees: (
        "Dispute about a fee or charge where the fee itself is the primary issue "
        "(not a symptom of hardship or credit reporting). Overdraft fees, "
        "over-limit fees, incorrect interest."
    ),
    Theme.service_failure: (
        "Operational failure: delays, incorrect processing, lost documents, "
        "unanswered requests, failure to action an agreed instruction. Use when "
        "no more specific theme fits."
    ),
    Theme.misleading_comms: (
        "Advertised rate, product terms or marketing material did not match what "
        "the customer received. Clear-fair-not-misleading breaches."
    ),
    Theme.other: (
        "Use only when no other theme fits. Prefer this over forcing a weak match."
    ),
}


class RedressCategory(str, Enum):
    fee_refund = "fee_refund"
    interest_adjustment = "interest_adjustment"
    credit_file_amendment = "credit_file_amendment"
    distress_and_inconvenience = "distress_and_inconvenience"
    premium_refund = "premium_refund"
    reimbursement = "reimbursement"
    goodwill_payment = "goodwill_payment"
    none = "none"
    requires_human_review = "requires_human_review"


REDRESS_CATEGORY_DESCRIPTIONS: dict[RedressCategory, str] = {
    RedressCategory.fee_refund: (
        "Refund of fees or charges incorrectly applied (overdraft, late payment, "
        "over-limit). Category only — the handler sets the amount."
    ),
    RedressCategory.interest_adjustment: (
        "Correction of interest incorrectly charged or not applied, including "
        "advertised rates that were not honoured."
    ),
    RedressCategory.credit_file_amendment: (
        "Removal or correction of adverse data reported to a credit reference "
        "agency (arrears markers, defaults, late-payment flags)."
    ),
    RedressCategory.distress_and_inconvenience: (
        "Payment for distress or inconvenience caused by the bank's handling, "
        "typically alongside another remedy. Category only — the handler sets the amount."
    ),
    RedressCategory.premium_refund: (
        "Refund of premiums paid for a product that should not have been sold "
        "(e.g. PPI mis-selling)."
    ),
    RedressCategory.reimbursement: (
        "Reimbursement of disputed transactions, typically under the CRM code "
        "for APP fraud or for unauthorised payments."
    ),
    RedressCategory.goodwill_payment: (
        "Discretionary gesture where no clear financial loss has occurred but "
        "service has fallen short."
    ),
    RedressCategory.none: (
        "No redress recommended because the complaint is not upheld or no loss "
        "or detriment has been identified."
    ),
    RedressCategory.requires_human_review: (
        "The analyst cannot responsibly identify a redress category from the "
        "material provided. Use when evidence is insufficient or the case "
        "turns on facts a human must verify."
    ),
}


class RecommendedNextStep(str, Enum):
    escalate = "escalate"
    request_more_info = "request_more_info"
    offer_redress = "offer_redress"
    uphold = "uphold"
    partially_uphold = "partially_uphold"
    decline = "decline"


RECOMMENDED_NEXT_STEP_DESCRIPTIONS: dict[RecommendedNextStep, str] = {
    RecommendedNextStep.escalate: (
        "Refer to a specialist team or senior handler. Required where the "
        "customer is vulnerable, the conduct risk is material, or the case "
        "exceeds routine handling authority."
    ),
    RecommendedNextStep.request_more_info: (
        "Insufficient information in the complaint to form a view. Ask the "
        "customer or internal teams for specific missing facts before proceeding."
    ),
    RecommendedNextStep.offer_redress: (
        "The complaint appears valid and a redress category has been identified; "
        "the handler should calculate the amount and offer it."
    ),
    RecommendedNextStep.uphold: (
        "Recommend upholding the complaint in full. The handler, not the model, "
        "makes the final decision and communicates it."
    ),
    RecommendedNextStep.partially_uphold: (
        "Recommend upholding only part of the complaint; the handler decides "
        "which elements and communicates the outcome."
    ),
    RecommendedNextStep.decline: (
        "Recommend declining the complaint. The model never closes a complaint; "
        "a handler must review and issue any decline decision."
    ),
}


class Confidence(str, Enum):
    low = "low"
    high = "high"
    medium = "medium"


CONFIDENCE_DESCRIPTIONS: dict[Confidence, str] = {
    Confidence.high: (
        "The complaint is clear and the analysis fields follow directly from "
        "the material. A reasonable handler would classify it the same way."
    ),
    Confidence.medium: (
        "Reasonable interpretation but with some ambiguity. Another handler "
        "could reach a different theme or next step on the same facts."
    ),
    Confidence.low: (
        "Material is thin, contradictory, or sits across multiple themes. "
        "Treat the analysis as a starting point; a handler should look closely."
    ),
}

def _enum_menu(label: str, mapping: dict) -> str:
    options = "\n".join(f"- {k.value}: {v}" for k, v in mapping.items())
    return f"{label}\n{options}"


class ComplaintAnalysis(BaseModel):
    theme: Theme = Field(
        ...,
        description=_enum_menu(
            "Dominant theme. Pick the theme that reflects the lasting harm, "
            "not the triggering event. Prefer the most specific theme; use "
            "'service_failure' only when no more specific theme fits.",
            THEME_DESCRIPTIONS,
        ),
    )
    severity: Severity = Field(
        ...,
        description=(
            "Independent reassessment of severity based on the complaint "
            "material. This is not a copy of the intake severity; note any "
            "disagreement with intake in 'rationale' or 'caveats'."
        ),
    )
    vulnerability_concern: bool = Field(
        ...,
        description=(
            "True when the complaint text itself raises a vulnerability "
            "signal (bereavement, financial hardship, serious illness, "
            "scam victimisation), regardless of the stored vulnerability "
            "flag on the customer record."
        ),
    )
    consumer_duty_risk: bool = Field(
        ...,
        description=(
            "True where foreseeable harm, fair-value or "
            "clear-fair-not-misleading concerns are present under the "
            "FCA Consumer Duty."
        ),
    )
    recommended_next_step: RecommendedNextStep = Field(
        ...,
        description=_enum_menu(
            "Recommended handler action. The system never closes a "
            "complaint; it only recommends.",
            RECOMMENDED_NEXT_STEP_DESCRIPTIONS,
        ),
    )
    redress_category: list[RedressCategory] = Field(
        ...,
        min_length=1,
        max_length=3,
        description=_enum_menu(
            "Redress categories addressing the complaint, ordered by importance "
            "(dominant harm first). Return 1 to 3 categories. Never state a "
            "redress amount.",
            REDRESS_CATEGORY_DESCRIPTIONS,
        ),
    )
    rationale: str = Field(
        ...,
        description=(
            "Two or three sentences grounded in the facts supplied, "
            "explaining the classification above."
        ),
    )
    confidence: Confidence = Field(
        ...,
        description=_enum_menu(
            "Self-reported confidence in the overall analysis.",
            CONFIDENCE_DESCRIPTIONS,
        ),
    )
    caveats: list[str] = Field(
        default_factory=list,
        description=(
            "Short notes on ambiguity, missing information, secondary "
            "themes or alternative classifications a handler should "
            "consider. Empty list is fine."
        ),
    )


class ComplaintAnalyzeResponse(BaseModel):
    id: int
    customer_id: int
    analysis: ComplaintAnalysis
    input_tokens: int
    output_tokens: int
    stop_reason: str | None = None



