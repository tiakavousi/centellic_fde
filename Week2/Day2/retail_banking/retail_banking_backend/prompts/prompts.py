from typing import Any

# TODO:
# Add to prompts/prompts.py:
# - GROUNDED_SYSTEM_PROMPT — your SYSTEM_PROMPT plus two sentences: 
# "Use only the sources below. Cite source IDs in square brackets, e.g. [doc-003]. 
# If the sources do not answer the question, say so."
# - build_grounded_user_prompt(question, hits) — 
# formats as Question:\n...\n\nSources\n---\n[doc-003] Title\nbody\n\n[doc-005] Title\nbody\n---.


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