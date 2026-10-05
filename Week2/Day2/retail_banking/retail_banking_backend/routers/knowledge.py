# TODO
#  Scope:
#   - POST /knowledge/index — calls knowledge_store.build_index(), returns {indexed: N, tokens_used: int}. Idempotent.
#   - GET /knowledge/search?q=...&top_k=4 — calls search(), returns raw hits with scores. No LLM.
#   - POST /knowledge/ask — the grounded answer with refusal. More below.
# 