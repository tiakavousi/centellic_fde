import os
from datetime import date

import config  # noqa: F401 — loads .env.local
import knowledge_store
from data.complaints import get_complaint
from data.customers import get_customer

RELEVANCE_FLOOR = float(os.environ["RELEVANCE_FLOOR"])
ACK_WINDOW_DAYS = int(os.environ.get("ACK_WINDOW_DAYS", "3"))
RESPONSE_WINDOW_DAYS = int(os.environ.get("RESPONSE_WINDOW_DAYS", "56"))

SEARCH_TOOLS = [
    {
        "name": "search_knowledge_base",
        "description": (
            "Search the retail banking knowledge base for documents "
            "relevant to the question about policy, methodology, ombudsman "
            "decisions and regulator guidance."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "the search query"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "check_sla_status",
        "description": "Return SLA windows and breach flags for a complaint id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "complaint_id": {"type": "integer"},
            },
            "required": ["complaint_id"],
        },
    },
    # find_similar_complaints — TODO add later
]

# tool 1
def search_knowledge_base(query: str, top_k: int = 3) -> list[dict] | dict:
    try:
        return [d for d in knowledge_store.search(query, top_k) if d["score"] >= RELEVANCE_FLOOR]
    except RuntimeError as e:
        return {"error": "search_failed", "detail": str(e)}

# tool 2
def check_sla_status(complaint_id: int) -> dict:
    complaint = get_complaint(complaint_id)
    if complaint is None:
        return {
            "error": "unknown_complaint_id",
            "detail": f"Complaint {complaint_id} not found",
        }

    customer = get_customer(complaint["customer_id"])
    is_vulnerable = bool(customer and customer["vulnerability_flag"])

    opened = date.fromisoformat(complaint["opened_date"])
    days_elapsed = (date.today() - opened).days

    return {
        "complaint_id": complaint["id"],
        "opened_date": complaint["opened_date"],
        "status": complaint["status"],
        "days_elapsed": days_elapsed,
        "ack_window_days": ACK_WINDOW_DAYS,
        "response_window_days": RESPONSE_WINDOW_DAYS,
        "ack_breached": days_elapsed > ACK_WINDOW_DAYS,
        "response_breached": days_elapsed > RESPONSE_WINDOW_DAYS,
        "days_until_response_deadline": RESPONSE_WINDOW_DAYS - days_elapsed,
        "is_vulnerable_customer": is_vulnerable,
    }

# tool 3
def find_similar_complaints():
    pass
