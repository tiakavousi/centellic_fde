import os
import knowledge_store
from data.documents import DOCUMENTS
from data.customers import CUSTOMERS

RELEVANCE_FLOOR = float(os.environ["RELEVANCE_FLOOR"])
ACK_WINDOW_DAYS = int(os.environ.get("ACK_WINDOW_DAYS", "3"))
RESPONSE_WINDOW_DAYS = int(os.environ.get("RESPONSE_WINDOW_DAYS", "56"))

def search_knowledge(query: str, top_k: int = 3) -> list[dict] | dict:
    try:
        return [d for d in knowledge_store.search(query, top_k) if d["score"] >= RELEVANCE_FLOOR]
    except RuntimeError as e:
        return {"error": "search_failed", "detail": str(e)}


def check_sla_status(complaint_id: int) -> dict:
    pass

def find_similar_complaints():
    pass
