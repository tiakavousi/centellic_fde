# Chunking decision

**Date:** 2026-10-13  **Decided by:** Tia  **Corpus:** documents.py + corpus.py (16 documents)
**Eval set:** eval_set.py (29 answerable, 3 unanswerable)  **Embedding model:** voyage-3-lite

## Decision
We serve `sections_contextual` with a relevance floor of `0.50`.

## Evidence
| Strategy          | R@1  | R@3  | MRR  | Context words@3 | Answer acc. | Refusal acc. |
|-------------------|------|------|------|-----------------|-------------|--------------|
| whole_document              | 0.69 | 1.00 | 0.84 | 862             | 0.72        | 1.00         |
| sections_contextual (best)  | 0.86 | 1.00 | 0.93 | 197             | 0.97        | 1.00         |
| fixed_overlap_25 (second)   | 0.52 | 0.93 | 0.67 | 277             | 0.59        | 1.00         |

All answer evals run at floor 0.50.

## Why this one
`sections_contextual` wins on every retrieval metric (R@1 0.86 vs 0.69 for whole_document, MRR 0.93
vs 0.84) while using ~4× fewer context words at k=3 (197 vs 862), which translates directly into
lower input-token cost per answer. Floor 0.50 was chosen over 0.30–0.45 because it holds the same
answer accuracy (0.97) and refusal accuracy (1.00) at the lowest avg input tokens (378 vs 422). The
one thing we give up is q24 ("What is matter LP-3307?"), a rare-id lookup that embeddings miss —
all floors below 0.50 miss it too, so we are not giving up anything that a lower floor would recover.

## Known weaknesses
- **q24 (exact-id, `LP-3307`)** is a false refusal: the matter reference is a rare token that voyage-3-lite
  does not latch onto. This is a retrieval failure, not a chunking one — **hybrid retrieval
  (BM25 or exact-id lookup fused with the vector score)** is the right fix, not a finer chunker.
- Unanswerable questions all pass (refusal_accuracy 1.00) at floor 0.50; the floor is doing the
  gate work for us.

## Revisit when
- A new document type lands that is not clearly sectioned (e.g. transcripts, chat logs, scanned PDFs
  without heading structure) — `sections_contextual` depends on headings and will degrade.
- The embedding model changes (e.g. moving off voyage-3-lite): similarity scales shift and the 0.50
  floor must be retuned with `tune_floor.py`.
- Documents get materially longer (sections > ~400 words): the 150-word section cap in
  `sections_contextual` will start cutting evidence spans in half, which is exactly what the
  evidence-span check in the eval set is designed to catch.
- Rare-id lookups (matter numbers, case citations) become common — add hybrid retrieval before
  re-tuning the floor.
