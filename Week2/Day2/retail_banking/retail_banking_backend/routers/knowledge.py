import os
from fastapi import APIRouter, HTTPException
from knowledge_store import build_index, count, search
from pydantic import BaseModel, Field
import llm
from prompts.prompts import build_grounded_user_prompt, GROUNDED_SYSTEM_PROMPT

TOP_K = int(os.environ["TOP_K"])
RELEVANCE_FLOOR = float(os.environ["RELEVANCE_FLOOR"])

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.post("/index")
def generate_indexes():
    tokens = build_index()
    return {
        "indexed": count(),
        "embedding_tokens_used": tokens
    }

@router.get("/search")
def search_quary(query: str, top_k: int = TOP_K):
    try:
        return {"hits": search(query, top_k), "top_k": top_k}
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.post("/ask")
def ask_question(query: str, top_k: int = TOP_K):
    try:
        hits = search(query, top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    usable = [hit for hit in hits if hit['score'] >= RELEVANCE_FLOOR]

    if not usable:
        return {
            "question": query,
            "answer": None,
            "refused": True,
            "reason": "No document in the corpus is relevant to the question",
            "sources": []
        }
    
    user_prompt = build_grounded_user_prompt(query, usable)
    result = llm.generate(GROUNDED_SYSTEM_PROMPT, user_prompt)

    return {
        "question": query,
        "answer": result["text"],
        "refused": False,
        "sources": [{"id": h["id"], "title": h["title"], "score": h["score"]} for h in usable],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
    }