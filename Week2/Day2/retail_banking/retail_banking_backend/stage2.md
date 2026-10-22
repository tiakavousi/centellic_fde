# Stage 2 — Chunking, Eval & Azure AI

Mirror the firm-intelligence-api evaluation and Azure AI pipeline.

---

## Checklist

### Chunking
- [ ] `chunking.py` — 6 strategies: `whole_document`, `fixed_words`, `fixed_overlap_25`, `sentence_packed`, `by_section` (plain + contextual), `STRATEGIES` dict, `chunk_corpus()`
- [ ] `chunk_index.py` — one Chroma collection per strategy: `build()`, `embed_batched()`, `search_with_vectors()`, fingerprint-based rebuild

### Eval set
- [ ] `eval_set.py` — ~30 labelled questions (retail banking domain: complaints, SLA rules, FCA conduct duty, FOS decisions, vulnerability policy); each answerable entry has `doc_id`, `evidence` (verbatim span), `keywords`, `kind`; 3–5 unanswerable entries; `answerable()` and `unanswerable()` helpers

### Pure helpers (no network, no model)
- [ ] `grounding.py` — `normalise()`, `is_refusal()`, `split_sentences()`, `citations_in()`, `check_citations()`; set `REFUSAL_SENTENCE` to match the knowledge router refusal text
- [ ] `eval_tools.py` — `contains_evidence()`, `keywords_present()`, `_alternative_matches()`; depends on `grounding`

### Eval runners
- [ ] `eval_retrieval.py` — score all strategies: Recall@1/3/5, MRR, context words, score gap; writes `eval_results/retrieval.json`; run: `python -m eval_retrieval`
- [ ] `floor_preview.py` — print what each relevance floor refuses before the model is called; run: `python -m floor_preview`
- [ ] `eval_answers.py` — answer quality (calls model); `run(strategy, vectors, floor)`; writes `eval_results/answers.json`; run: `python -m eval_answers sections_contextual`
- [ ] `tune_floor.py` — sweep strategies × floors, pick best; writes `eval_results/floor_sweep.json`; run: `python -m tune_floor sections_contextual`

### Azure AI Search
- [ ] `azure_index.py` — index schema: `DIMENSIONS`, `key_for()`, `index_definition()` (keyword + vector + semantic config fields)
- [ ] `azure_store.py` — `count()`, `build_index(strategy)`, `search_with_vector()`; semantic reranker on by default, falls back to RRF score
- [ ] `azure_build.py` — CLI entry point: `python -m azure_build sections_contextual`

### Tests
- [ ] `tests/test_chunking.py` — `fixed_words` chunk count, overlap, `sentence_packed` never splits sentences, `by_section` contextual prefix
- [ ] `tests/test_grounding.py` — `is_refusal(None)`, refusal sentence match, `check_citations` valid/invalid/uncited
- [ ] `tests/test_eval_set.py` — every answerable evidence span present in named document; no duplicate `id` fields

### Config / env
- [ ] Add `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX`, `SEMANTIC_CONFIG`, `EXACT_MATCH_RULE` to `.env.local` and `config.py`
- [ ] Update `RELEVANCE_FLOOR` in `.env.local` after floor sweep

---

## Suggested order

```
chunking.py
chunk_index.py
eval_set.py
grounding.py
eval_tools.py
eval_retrieval.py        ← run it, inspect retrieval.json
floor_preview.py         ← pick candidate floors
eval_answers.py
tune_floor.py            ← pick best strategy + floor, update RELEVANCE_FLOOR
azure_index.py
azure_store.py
azure_build.py
tests/test_chunking.py
tests/test_grounding.py
tests/test_eval_set.py
```
