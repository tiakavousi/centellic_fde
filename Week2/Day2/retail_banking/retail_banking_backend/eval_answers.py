"""
Answer quality evaluation against the live Azure index.

For every answerable question in EVAL_SET:
  1. Retrieve top-k chunks via knowledge_store.search()
  2. Apply RELEVANCE_FLOOR — record refusal if no chunk passes
  3. Call llm.generate() with the grounded prompt
  4. Score with keywords_present() and check_citations()

Writes eval_results/answers.json and prints a summary table.

Run: python -m eval_answers
"""

import json
from pathlib import Path

import gate
import llm
import knowledge_store
import settings
from eval_set import EVAL_SET
from eval_tools import keywords_present
from grounding import check_citations
from prompts.prompts import GROUNDED_SYSTEM_PROMPT, build_grounded_user_prompt


def run() -> list[dict]:
    answerable = [q for q in EVAL_SET if q["doc_id"]]
    unanswerable = [q for q in EVAL_SET if not q["doc_id"]]
    results = []

    print(f"Running answer eval: {len(answerable)} answerable, {len(unanswerable)} unanswerable\n")

    for q in answerable:
        hits = knowledge_store.search(q["question"], top_k=settings.TOP_K)
        usable = [h for h in hits if gate.is_usable(h)]

        if not usable:
            results.append({
                "id": q["id"],
                "kind": q["kind"],
                "question": q["question"],
                "passed_floor": False,
                "refused": True,
                "keywords_ok": False,
                "citations_ok": False,
                "answer": None,
                "input_tokens": 0,
                "output_tokens": 0,
            })
            print(f"  {q['id']} REFUSED (floor)  {q['question'][:60]}")
            continue

        user_prompt = build_grounded_user_prompt(q["question"], usable)
        result = llm.generate(GROUNDED_SYSTEM_PROMPT, user_prompt)
        answer = result["text"]
        source_ids = [h["id"] for h in usable]

        kw_ok = keywords_present(answer, q["keywords"])
        cite = check_citations(answer, source_ids)
        cite_ok = cite["passed"]

        status = "OK  " if kw_ok and cite_ok else "FAIL"
        print(f"  {q['id']} {status}  kw={'Y' if kw_ok else 'N'}  cite={'Y' if cite_ok else 'N'}  {q['question'][:55]}")
        if not kw_ok:
            print(f"       keywords expected: {q['keywords']}")
        if cite["invalid"]:
            print(f"       invalid citations: {cite['invalid']}")
        if cite["uncited_sentences"]:
            print(f"       uncited sentences: {len(cite['uncited_sentences'])}")

        results.append({
            "id": q["id"],
            "kind": q["kind"],
            "question": q["question"],
            "passed_floor": True,
            "refused": False,
            "keywords_ok": kw_ok,
            "citations_ok": cite_ok,
            "invalid_citations": cite["invalid"],
            "uncited_sentences": cite["uncited_sentences"],
            "answer": answer,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
        })

    # unanswerable questions — correct behaviour is refusal
    print()
    for q in unanswerable:
        hits = knowledge_store.search(q["question"], top_k=settings.TOP_K)
        usable = [h for h in hits if gate.is_usable(h)]
        correctly_refused = len(usable) == 0
        status = "OK  " if correctly_refused else "FAIL (should refuse)"
        print(f"  {q['id']} {status}  {q['question'][:60]}")
        results.append({
            "id": q["id"],
            "kind": q["kind"],
            "question": q["question"],
            "passed_floor": len(usable) > 0,
            "refused": len(usable) == 0,
            "correctly_refused": correctly_refused,
            "keywords_ok": None,
            "citations_ok": None,
            "answer": None,
            "input_tokens": 0,
            "output_tokens": 0,
        })

    return results


def _summarise(results: list[dict]) -> None:
    answered = [r for r in results if r.get("kind") != "unanswerable" and not r["refused"]]
    refused_answerable = [r for r in results if r.get("kind") != "unanswerable" and r["refused"]]
    unanswerable = [r for r in results if r.get("kind") == "unanswerable"]

    kw_pass = [r for r in answered if r["keywords_ok"]]
    cite_pass = [r for r in answered if r["citations_ok"]]
    both_pass = [r for r in answered if r["keywords_ok"] and r["citations_ok"]]

    total_input = sum(r["input_tokens"] for r in results)
    total_output = sum(r["output_tokens"] for r in results)

    print("\n" + "=" * 60)
    print(f"  Answerable questions : {len(answered) + len(refused_answerable)}")
    print(f"  Answered (past floor): {len(answered)}")
    print(f"  Refused by floor     : {len(refused_answerable)}")
    print(f"  Keywords ok          : {len(kw_pass)}/{len(answered)}"
          f"  ({100*len(kw_pass)//len(answered) if answered else 0}%)")
    print(f"  Citations ok         : {len(cite_pass)}/{len(answered)}"
          f"  ({100*len(cite_pass)//len(answered) if answered else 0}%)")
    print(f"  Both ok              : {len(both_pass)}/{len(answered)}"
          f"  ({100*len(both_pass)//len(answered) if answered else 0}%)")
    print(f"  Unanswerable correct : {sum(r['correctly_refused'] for r in unanswerable)}/{len(unanswerable)}")
    print(f"  Total tokens used    : {total_input} in / {total_output} out")
    print("=" * 60)

    if refused_answerable:
        print(f"\nRefused answerable (floor={settings.RELEVANCE_FLOOR}):")
        for r in refused_answerable:
            print(f"  {r['id']}  {r['question'][:65]}")

    failed = [r for r in answered if not (r["keywords_ok"] and r["citations_ok"])]
    if failed:
        print("\nFailed questions:")
        for r in failed:
            print(f"  {r['id']}  kw={'Y' if r['keywords_ok'] else 'N'}  cite={'Y' if r['citations_ok'] else 'N'}  {r['question'][:55]}")


def main() -> None:
    results = run()
    _summarise(results)

    Path("eval_results").mkdir(exist_ok=True)
    out = Path("eval_results/answers.json")
    out.write_text(json.dumps(results, indent=2))
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
