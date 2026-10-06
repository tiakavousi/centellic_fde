from typing import Any

REFUSAL_SENTENCE = "The provided documents do not answer that question."

GROUNDED_SYSTEM_PROMPT = (
    "You are a complaints and conduct analyst at a UK retail bank. "
    "Answer using ONLY the sources provided below. "
    "Cite the document id in square brackets after each claim, like [doc-003]. "
    f"If the sources do not contain the answer, say exactly: '{REFUSAL_SENTENCE}' "
    "Never use knowledge from outside the sources. "
    "Never state a specific redress amount; identify the redress category only "
    "and defer the figure to a human handler. "
    "Never recommend closing or dismissing a complaint autonomously. "
    "Where the customer is flagged as vulnerable, apply the Vulnerable Customers "
    "Standard: escalate rather than resolve. "
    "Use British English and formal, neutral language. No em dash characters."
)

SYSTEM_PROMPT = (
    "You are a complaints and conduct analyst at a UK retail bank, writing for "
    "complaint handlers and the conduct-risk team. "
    "Use British English and formal, neutral language. "
    "Use only the complaint details, customer context and documents provided to you. "
    "Never invent facts, policy wording, redress figures or ombudsman outcomes "
    "that are not in the material supplied. "
    "Never state a specific redress amount — identify the redress category only, "
    "and defer the figure to a human handler applying the redress methodology. "
    "Never recommend closing or dismissing a complaint autonomously; recommend "
    "a next step for a handler to take. "
    "Where the customer is flagged as vulnerable, apply the Vulnerable Customers "
    "Standard: escalate rather than resolve, and never advise ending collections or recovery activity without specialist review."
)

def build_complaint_summary_user_prompt(complaint: dict[str, Any]) -> str:
    return (
        "Summarise this complaint in two short paragraphs.\n\n"
        f"Complaint channel: {complaint['channel']}\n"
        f"Intake severity: {complaint['severity']}\n"
        f"Status: {complaint['status']}\n"
        f"Product: {complaint['product']}\n"
        f"Opened: {complaint['opened_date']}\n"
        f"Description: {complaint['summary']}\n"
    )


def build_complaint_analysis_user_prompt(
    complaint: dict[str, Any],
    customer: dict[str, Any],
) -> str:
    return (
        "Classify this complaint and return every field of the ComplaintAnalysis "
        "schema.\n\n"
        "Guidance:\n"
        "- List redress categories ordered by importance, dominant harm first."
        " Use 'caveats' for ambiguity, not for secondary remedies.\n"
        "- If the complaint status is already 'resolved' or 'escalated', frame "
        "the recommended next step as a post-resolution review action.\n\n"
        "Complaint\n"
        f"- ID: {complaint['id']}\n"
        f"- Product: {complaint['product']}\n"
        f"- Channel: {complaint['channel']}\n"
        f"- Intake severity: {complaint['severity']}\n"
        f"- Status: {complaint['status']}\n"
        f"- Opened: {complaint['opened_date']}\n"
        f"- Description: {complaint['summary']}\n\n"
        "Customer\n"
        f"- ID: {customer['id']}\n"
        f"- Segment: {customer['segment']}\n"
        f"- Vulnerability flag (stored): {customer['vulnerability_flag']}\n"
    )

def build_grounded_user_prompt(question: str, hits: list[dict]) -> str:
      sources = "\n\n".join(f"[{h['id']}] {h['title']}\n{h['body']}" for h in hits)
      return f"Question: {question}\n\nSources\n---\n{sources}\n---"