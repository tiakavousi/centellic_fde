"""
Reciprocal Rank Fusion: merge several ranked id lists into one.
"""

K = 60


def reciprocal_rank_fusion(ranked_lists: list[list], k: int = K) -> list[tuple]:
    scores: dict = {}
    for ids in ranked_lists:
        for rank, item_id in enumerate(ids):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
