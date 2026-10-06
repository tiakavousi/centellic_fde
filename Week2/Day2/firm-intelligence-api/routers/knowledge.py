from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import knowledge_store as knowledge
from anthropic import APIStatusError,APITimeoutError,RateLimitError
import grounding
import llm


# Relevance floor
# below this we treat the retrived context as not relevance
RELEVANCE_FLOOR = 0.35

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

class Question(BaseModel):
    question:str = Field(min_length=3)
    top_k:int = Field(default=3, gt=0, lt=8)

@router.post("/index")
def rebuild_index():
    """
    embed the corpus, costs tokens so it is a deliberate POST rather than embeded in the application
    """
    tokens = knowledge.build_index()
    return {"indexed": knowledge.count(), "embeddings_tokens": tokens}

@router.post("/search")
def search_query(query: Question):
    try:
        return knowledge.search(query.question, query.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))


# function behaviour...
    # the refusal happens before the model is called, not after
    # why 200 and not a 404 for a refusal???
        # the request was valid... service handled it correctly and "we have no relevant document" is a real answer
    # sources...
        # this makes our answer checkable.... without it a client has an answer/para that they HAVE to trust.... with it they can open doc-004 and verify the claim themselves
    # same error mapping as before
        # 504, 429, 502.... never a bare 500
@router.post("/ask")
def ask(q:Question):
    "Retieve, then answer using only what was retrieved ... or refuse"
    # 1. Retrieve
    # same call as /knowledge/search
    try:
        hits = knowledge.search(q.question, q.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    # 2. Filter, and decide whether to make a call to the model at all
    # (compare against the RELEVANCE_FLOOR)
    usable = [hit for hit in hits if hit["score"] >= RELEVANCE_FLOOR]

    if not usable:
        return {
            "question": q.question,
            "answer": None,
            "refused": True,
            "reason": "No documnet in the corpus is relevant to the question.",
            "sources": []
        }
    # 3. Build context and generate the answer
    context = "\n\n".join( f"{ hit['id']}, {hit['title']}\n{hit['text']}" for hit in usable)
    # 4. Return the successful answer 
    try:
        result = llm.answer_from_context(q.question, context)

    except APITimeoutError as e:
        print("Anthropic timeout:", repr(e))
        raise HTTPException(
            status_code=504,
            detail="Answer provider timed out" 
        )

    except RateLimitError as e:
        print("Anthropic rate limit:", repr(e))
        raise HTTPException(
            status_code=429,
            detail="Answer provider rate limit exceeded"
        )

    except APIStatusError as e:
        print("Anthropic API status error:", repr(e))
        raise HTTPException(
            status_code=502,
            detail=str(e)
        )

    return {
        "question": q.question,
        "answer": result["answer"],
        "refused": False,
        "sources": [{"id":hit["id"], "title":hit["title"], "score":hit["score"]} for hit in usable],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "stop_reason": result["stop_reason"],
        "grounding": grounding.check_citations(result["answer"], [h["id"] for h in usable])
    }
