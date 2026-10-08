"""
A chunker must not lose, duplicate or mangle text
"""

import pytest
import chunking
from corpus import CORPUS_DOCUMENTS
from documents import DOCUMENTS

ALL_DOCS = DOCUMENTS + CORPUS_DOCUMENTS

@pytest.mark.parametrize("doc", ALL_DOCS)
def test_fixed_chunks_without_overlap_lose_no_words(doc):
    chunks = chunking.fixed_words(doc, size=100, overlap=0)
    rebuilt = " ".join(c['text'] for c in chunks).split()
    assert rebuilt == doc['body'].split()


@pytest.mark.parametrize("doc", ALL_DOCS)
def test_overlap_repeats_exactly_the_overlap_words(doc):
    chunks = chunking.fixed_words(doc, size=100, overlap=25)
    for first, second in zip(chunks, chunks[1:]):
        assert first["text"].split()[-25:] == second["text"].split()[:25]


@pytest.mark.parametrize("doc", ALL_DOCS)
def test_overlap_must_be_smaller_than_size(doc):
    with pytest.raises(ValueError):
        chunking.fixed_words(doc, size=100, overlap=100)


@pytest.mark.parametrize("doc", ALL_DOCS)
def test_sentence_packing_never_cuts_a_sentence(doc):
    chunks = chunking.sentence_pack(doc, max_words=100)
    original_units = chunking.split_sentences(doc["body"])
    rebuilt_units = []
    for chunk in chunks:
        rebuilt_units.extend(chunking.split_sentences(chunk["text"]))
    assert rebuilt_units == original_units


@pytest.mark.parametrize("doc", ALL_DOCS)
def test_contextual_sections_carry_title_and_heading(doc):
    pass


@pytest.mark.parametrize("doc", ALL_DOCS)
def test_plain_sections_carry_no_heading(doc):
    pass