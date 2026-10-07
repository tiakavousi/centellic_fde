import re
from corpus import CORPUS_DOCUMENTS
from documents import DOCUMENTS

from eval_set import EVAL_SET, answerable
from eval_tools import contain_evidence, keywords_present, normalise
import collections
from grounding import REFUSAL_SENTENCE

ALL_DOCS = {d['id']:d for d in DOCUMENTS + CORPUS_DOCUMENTS}

def section_conaining(body:str, evidence:str) -> tuple[str, str]:
    """
    Return (heading, section, text) for the section holding the evidence.
    """
    for part in re.split(r"(?m)^##", body):
        heaing, _, text = part.partition("\n")
        if contain_evidence(text, evidence):
            return heaing.strip(), text
    raise AssertionError(f"evidence not found in any section: {evidence}")

# test ids are unique
def test_unique_ids():
    ids = [d["id"] for d in EVAL_SET]
    counter = collections.Counter(ids)
    duplicates = {id: count for id, count in counter.items() if count > 1}
    assert not duplicates, f"duplicate ids: {duplicates}"

# test every evidence span is in its documents
def test_every_evidence_span_is_in_documents():
    """
    Collects every eval item whose evidence can't be found in its doc.
    """
    missing_evidence_in_doc = []
    # answerable() returns only the eval items that have an evidence span to check
    for item in answerable():
        doc_id = item['doc_id'] # the doc this eval row says the evidence lives in
        evidence = item['evidence'] # the exact text snippet that should appear in that doc

        # Sanity check 1: the labelled doc_id must actually exist in the corpus
        if doc_id not in ALL_DOCS:
            missing_evidence_in_doc.append((item.get('id', '?'), doc_id, 'unknown doc_id'))
            continue

        # Pull the body of the labelled doc so we can search it.
        body = ALL_DOCS[doc_id]["body"]

        # Sanity check 2: the evidence snippet must actually appear in that body.
        if not contain_evidence(body, evidence):
            missing_evidence_in_doc.append((item.get("id", "?"), doc_id, evidence))

    # Fail the test ONLY if the collected list is non-empty.
    assert not missing_evidence_in_doc, f"evidence not found in its doc:{missing_evidence_in_doc}"

# test every evidence span appears exactly once in the whole corpus
def test_every_evidence_span_appears_once():
    """"
    Checks every evidence span in EVAL_SET appears in exactly one doc in the whole ALL_DOCS.
    Not zero (missing), not two or more (ambiguous).
    """
    failures = []
    for item in answerable():
        evidence = item["evidence"]
        hits = [doc_id for doc_id, doc in ALL_DOCS.items() if contain_evidence(doc['body'], evidence)]
        if len(hits) != 1:
            failures.append((item.get("id", "?"), evidence, hits))
    assert not failures, f"evidence not uniquely locatable: {failures}"

# test keyword matching in whole word and refusal aware
def test_keyword_matching_in_whole_word_and_refusal_aware():
    cases = [
          # whole-word match
          ("The firm operates in the UK.", ["UK"], True),
          # substring that is NOT a whole word — must fail
          ("They expanded into Ukraine.", ["UK"], False),
          # prefix wildcard
          ("strong litigation practice", ["litig*"], True),
          # multi-group AND — both hit
          ("offices in Lagos and Nairobi", ["Lagos", "Nairobi"], True),
          # multi-group AND — one missing
          ("offices in Lagos", ["Lagos", "Nairobi"], False),
          # alternatives within a group (OR)
          ("based in London", ["London|UK"], True),
          # refusal answer — must be False even if keyword appears
          (REFUSAL_SENTENCE, ["UK"], False),
          # None answer
          (None, ["UK"], False),
      ]
    failures = []
    for answer, keywords, expected in cases:
        got = keywords_present(answer, keywords)
        if got != expected:
            failures.append((answer, keywords, expected, got))
    assert not failures, f"keyword matching regressions: {failures}"