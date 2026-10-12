import os
from datetime import date

import config  # noqa: F401 — loads .env.local
import knowledge_store
from data.complaints import COMPLAINTS, get_complaint
from data.customers import get_customer
from data.enums import ProductType

MAX_SIMILAR_RESULTS = 10
DEFAULT_SIMILAR_RESULTS = 5

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
    {
        "name": "find_similar_complaints",
        "description": (
            "Find historic complaints that match on product and/or theme, "
            "to drive consistent outcomes. At least one of product or "
            "theme must be provided. Results are sorted by opened_date "
            "descending."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product": {
                    "type": "string",
                    "enum": [p.value for p in ProductType],
                    "description": "Filter by product type (exact match).",
                },
                "theme": {
                    "type": "string",
                    "description": (
                        "Case-insensitive keyword matched against the "
                        "complaint summary (e.g. 'late payment', 'bereavement')."
                    ),
                },
                "vulnerable_only": {
                    "type": "boolean",
                    "description": "If true, keep only complaints from vulnerable customers.",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": MAX_SIMILAR_RESULTS,
                },
            },
        },
    },
]

# tool 1
def search_knowledge_base(query: str, top_k: int = 3) -> list[dict] | dict:
    """
    Search the knowledge base and keep hits at or above the relevance floor.

    Embeds the query via Voyage, queries Chroma for the top_k nearest documents,
    then drops any result whose score is below RELEVANCE_FLOOR. Returning an empty
    list is the signal the agent should refuse: no source cleared the floor.

    Args:
        query: Natural-language search query.
        top_k: Maximum number of documnets to pull from Chromadb before filtering.

    Returns:
        List of {id, title, text, score} dicts above the floor, or
        {error, detail} if the vector store call failed.
    """
    try:
        return [d for d in knowledge_store.search(query, top_k) if d["score"] >= RELEVANCE_FLOOR]
    except RuntimeError as e:
        return {"error": "search_failed", "detail": str(e)}


# tool 2
def check_sla_status(complaint_id: int) -> dict:
    """
    Compute SLA aging and breach flags for a single complaint.

    Looks up the complaint by id, computes days elapsed since opened_date, and
    compares against the acknowledgement window (ACK_WINDOW_DAYS) and the final
    response window (RESPONSE_WINDOW_DAYS). Also joins the customer to surface
    vulnerability, since vulnerable-customer SLAs are treated more strictly by
    handlers.

    Args:
        complaint_id: The complaint id to inspect.

    Returns a dict of response including the SLA compute or {error, detail} if the complaint id is unknown.
    """
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
def find_similar_complaints(
    product: str | None = None,
    theme: str | None = None,
    vulnerable_only: bool = False,
    limit: int = DEFAULT_SIMILAR_RESULTS,
) -> dict:
    """
    Return historic complaints matching product and/or a theme keyword.

    Used by the agent to drive outcome consistency: before recommending a next
    step on a new complaint, the model can look at how similar past cases were
    categorised and resolved. 
    At least one of product or theme must be given,otherwise the function refuses 
    rather than dumping the whole table. 
    Matching is exact on product (enum) and case-insensitive substring on summary for
    theme. Results are joined to the customer for the vulnerable flag, sorted
    by opened_date descending (most recent first), and truncated to limit.

    Args:
        product: ProductType value to filter by (e.g. 'mortgage'). Optional.
        theme: Case-insensitive keyword searched in the complaint summary. Optional.
        vulnerable_only: If true, keep only complaints whose customer is flagged vulnerable.
        limit: Maximum number of rows to return. Clamped to [1, MAX_SIMILAR_RESULTS].

    Returns:
        {count, results: [{id, customer_id, product, severity, status,
        opened_date, summary, vulnerable}, ...]}, or
        {error, detail} if neither product nor theme was provided, or the
        product value is not a valid ProductType.
    """
    if not product and not theme:
        return {
            "error": "missing_filter",
            "detail": "Provide at least one of 'product' or 'theme'.",
        }

    if product is not None:
        try:
            product_enum = ProductType(product)
        except ValueError:
            return {
                "error": "unknown_product",
                "detail": f"Unknown product '{product}'. Valid: {[p.value for p in ProductType]}",
            }
    else:
        product_enum = None

    limit = max(1, min(int(limit), MAX_SIMILAR_RESULTS))
    needle = theme.lower().strip() if theme else None

    matches = []
    for c in COMPLAINTS:
        if product_enum is not None and c["product"] != product_enum:
            continue
        if needle and needle not in c["summary"].lower():
            continue
        customer = get_customer(c["customer_id"])
        is_vulnerable = bool(customer and customer["vulnerability_flag"])
        if vulnerable_only and not is_vulnerable:
            continue
        matches.append({
            "id": c["id"],
            "customer_id": c["customer_id"],
            "product": c["product"].value,
            "severity": c["severity"].value,
            "status": c["status"].value,
            "opened_date": c["opened_date"],
            "summary": c["summary"],
            "vulnerable": is_vulnerable,
        })

    matches.sort(key=lambda r: r["opened_date"], reverse=True)
    results = matches[:limit]
    return {"count": len(results), "results": results}
