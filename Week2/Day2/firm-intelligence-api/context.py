"""
How retrievd hits become the text the model reads
Failure: lost in the model
"""

# hits
def order_for_context(hits: list[dict]) -> list[dict]:
    """
    Best hit first, second best last, weakest in the middle.
    Ranked [a, b, c, d, e] becomes [a, c, e, d, b]
    """
    ranked = sorted(hits, key=lambda h: h["score"], reverse=True)
    front = ranked[0::2]
    back = ranked[1::2]
    return front + back[::-1]

