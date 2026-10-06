# TODO
#  Scope:
#   - POST /knowledge/index — calls knowledge_store.build_index(), returns {indexed: N, tokens_used: int}. Idempotent.
#   - GET /knowledge/search?q=...&top_k=4 — calls search(), returns raw hits with scores. No LLM.
#   - POST /knowledge/ask — the grounded answer with refusal. More below.
#
import os
from fastapi import APIRouter, HTTPException
from knowledge_store import build_index, count, search
from pydantic import BaseModel, Field

TOP_K = os.environ["TOP_K"]

router = APIRouter(prefix="/knowledge", tags=["knwoledge"])

class Question(BaseModel):
    query: str = Field(min_length=3)
    top_k:int = Field(default=TOP_K)

@router.post("/index")
def generate_indexes():
    tokens = build_index()
    return {
        "indexed": count(),
        "embedding_tokens_used": tokens
    }

@router.get("/search")
def search_quary(question: Question) -> str:
    try:
        search(question.query, question.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
