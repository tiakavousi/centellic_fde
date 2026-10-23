"""
This module checks on generated answers. Pure functions: no network, no model, no FastAPI.
Failure - ungrounded hallucination: sentences that carry no citation at all.
Failure - citation drift: citations that point at the wrong source, or at no source.
"""

import re

import settings

CITATION = re.compile(r"doc-\d{3}")

def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()

def is_refusal(answer: str | None) -> bool:
    return answer is None or normalise(settings.REFUSAL_SENTENCE) in normalise(answer)


def split_sentences(text: str) -> list[str]:
    """
    Split an answer into sentences, attaching trailing citations to their sentence.

    Handles two citation styles the model uses:
      "The bank has eight weeks [doc-001]."   — citation before full stop
      "The bank has eight weeks. [doc-001]"   — citation after full stop

    A citation-only fragment is only merged back if it is followed by \n or
    end-of-string (nothing else on the same line). A citation mid-sentence
    followed by more text is left as-is so ambiguous placements are visible.
    """
    # normalise: attach post-period citations that appear before a newline or end
    # "sentence. [doc-001]\n" → "sentence. [doc-001]\n"  (kept together)
    # "sentence. [doc-001] More text" → left alone (ambiguous)
    normalised = re.sub(
        r"([.!?])\s+(\[(?:doc-\d{3}[,\s]*)+\])(?=\s*\n|\s*$)",
        r"\1 \2",
        text,
    )

    pieces = []
    for line in normalised.splitlines():
        line = line.strip(" -*\t")
        if line:
            pieces.extend(p for p in re.split(r"(?<=[.!?])\s+", line) if p)

    sentences: list[str] = []
    for piece in pieces:
        if sentences and CITATION.sub("", piece).strip(" [].,") == "":
            sentences[-1] = f"{sentences[-1]} {piece}"
        else:
            sentences.append(piece)
    return sentences

def citations_in(text: str) -> list[str]:
    return CITATION.findall(text)

def check_citations(answer: str | None, source_ids: list[str]) -> dict:
    """
    cheap structral checks, Catches uncited claims and citations to sources we never gave
    """
    if is_refusal(answer):
        return {
            "refusal": True,
            "cited": [],
            "invalid": [],
            "uncited_sentences": [],
            "passed": True,
        }

    sentences = split_sentences(answer)
    cited = sorted(set(citations_in(answer)))
    invalid = [doc_id for doc_id in cited if doc_id not in source_ids]
    uncited = [
        s for s in sentences
        if not CITATION.search(s)
        and len(s.split()) >= 5
        and not re.fullmatch(r"\d+\.", s.strip())
        and not s.strip().endswith(":")
    ]

    return {
            "refusal": False,
            "cited": cited,
            "invalid": invalid,
            "uncited_sentences": uncited,
            "passed": not invalid and not uncited,
    }