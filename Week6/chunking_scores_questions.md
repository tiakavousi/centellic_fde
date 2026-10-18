Building indexes (free if nothing has changed)...
  whole_document          16 chunks  up to date       0 tokens
  fixed_100               46 chunks  up to date       0 tokens
  fixed_overlap_25        55 chunks  up to date       0 tokens
  sentences_100           49 chunks  up to date       0 tokens
  sections_plain          71 chunks  up to date       0 tokens
  sections_contextual     71 chunks  up to date       0 tokens

Embedded 32 questions once (382 tokens), reused for every strategy.

strategy                 R@1   R@3   R@5    MRR  ctx words  top ans  top unans
------------------------------------------------------------------------------
whole_document          0.69  1.00  1.00   0.84        862     0.56       0.43
fixed_100               0.48  0.79  0.90   0.61        273     0.60       0.49
fixed_overlap_25        0.52  0.93  0.97   0.67        277     0.61       0.50
sentences_100           0.41  0.76  0.90   0.57        262     0.60       0.50
sections_plain          0.31  0.86  0.93   0.54        186     0.61       0.52
sections_contextual     0.86  1.00  1.00   0.93        197     0.66       0.50

Missed at k=3:
  whole_document         none
  fixed_100              q02, q05, q08, q09, q22, q26
  fixed_overlap_25       q02, q09
  sentences_100          q02, q03, q04, q08, q09, q20, q22
  sections_plain         q02, q04, q09, q22
  sections_contextual    none


-----------------------------------------------------------------------------------

1. Is chunking worth it? Compare whole_document with your best chunked strategy on MRR and on ctx words. 

Yes. sections_contextual beats whole_document on MRR (0.93 vs 0.84) and R@1 (0.86 vs 0.69), while using ~4× less context (197 vs 862 words). Chunking buys you both better ranking and cheaper prompts.
-----
2. What did blind splitting cost? 
Splitting without preserving structure gutted R@1: sections_plain 0.31, sentences_100 0.41, fixed_100 0.48. Semantic context (the heading, the surrounding paragraph) gets stripped from each chunk, so the embedding of "the London office opened in September 2025" no longer knows which firm — the right chunk is still in the top 5, but ranked below distractors from other docs.
-----
3. What did the contextual prefix buy? sections_plain and sections_contextual split identically. Any difference between them is the prefix alone. Open retrieval.json and compare recall@3_by_kind for heading-dependent and title-dependent.
sections_plain and sections_contextual chunk identically — the only difference is the title/heading prefix. The by-kind recall@3 shows exactly what the prefix fixed:

┌───────────────────┬────────────────┬─────────────────────┐
│       kind        │ sections_plain │ sections_contextual │
├───────────────────┼────────────────┼─────────────────────┤
│ heading-dependent │ 0.50           │ 1.00                │
├───────────────────┼────────────────┼─────────────────────┤
│ title-dependent   │ 0.75           │ 1.00                │
├───────────────────┼────────────────┼─────────────────────┤
│ lookup            │ 0.78           │ 1.00                │
└───────────────────┴────────────────┴─────────────────────┘

The prefix turned the two kinds that require knowing which firm/section a chunk belongs to from coin-flips into perfect recall. It also lifted overall R@1 from 0.31 → 0.86 and MRR from 0.54 → 0.93 at
essentially no extra context cost (186 → 197 words).

-----
4. Which questions fail everywhere? A question missed by every strategy is not a chunking problem. Check its kind: negation and exact-id misses point at the embedding model, and that is next lesson's material, hybrid retrieval. The two score columns. Are unanswerable questions' best scores clearly below answerable ones? If they overlap, no single floor separates them cleanly.

Across all chunked strategies, q02 and q09 are the common misses (whole_document and sections_contextual hit everything). Looking at eval_set.py, these are the kinds that stress the embedding model, not the chunker — negation and exact-id/title-dependent phrasings where cosine similarity on dense vectors underperforms. That's the hybrid-retrieval (BM25 + dense) territory from next lesson.

Answerable vs unanswerable score gap:

┌─────────────────────┬─────────┬───────────┬──────┐
│      strategy       │ top ans │ top unans │ gap  │
├─────────────────────┼─────────┼───────────┼──────┤
│ sections_contextual │ 0.66    │ 0.50      │ 0.16 │
├─────────────────────┼─────────┼───────────┼──────┤
│ fixed_overlap_25    │ 0.61    │ 0.50      │ 0.11 │
├─────────────────────┼─────────┼───────────┼──────┤
│ sections_plain      │ 0.61    │ 0.52      │ 0.09 │
└─────────────────────┴─────────┴───────────┴──────┘

The gap is narrow everywhere — unanswerable top scores (~0.50) overlap with the lower end of answerable scores. No single similarity floor cleanly separates them, so a threshold-based "I don't know" gate
will misfire. You'll need LLM-based abstention or a reranker
-----
5. Choose a shortlist of your two best chunked strategies for Step 7, and keep whole_document as the baseline.
- sections_contextual — primary (highest MRR, perfect R@3, cheap context)
- fixed_overlap_25 — secondary (best structure-agnostic chunker; useful fallback for corpora without clean headings)
- whole_document — baseline