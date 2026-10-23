"""
Relevance gate — decides whether a retrieved chunk is good enough to reach the model.

A hit from Azure carries rerank_score (0–4, from the semantic reranker).
A hit from the local Chroma index carries only a cosine similarity in score (0–1).
A hit flagged exact_match always passes regardless of score (hybrid branch only).
"""

import settings


def is_usable(hit: dict) -> bool:
    if hit.get("exact_match", False):
        return True

    if hit.get("rerank_score") is not None:
        return hit["rerank_score"] >= settings.RERANK_FLOOR

    return hit["score"] >= settings.RELEVANCE_FLOOR
