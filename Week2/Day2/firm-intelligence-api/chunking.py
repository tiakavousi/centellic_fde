"""
Chunking startegies
Every startegy takes a document and returns a list of chunks.

A chunk is a dict:
    - id        "<doc_id> # <two-digit-number>" , kept stable for the same input
    - doc_id    the parent document, used for citations
    - title     the parent document title
    - text      exactly what gets embeded and what the model will read
"""

import re


def _chunk(doc:dict , number: int, text: str) -> dict:
    # since we later want to sort the ids , we add padding (02d) to number so : 2 -> 02
    # sort with padding : ['doc-105#01', 'doc-105#02', 'doc-105#10'] correct sorting
    # sort without padding : ['doc-105#1', 'doc-105#10', 'doc-105#2']  wrong sorting
    return {"id": f"{doc['id']}#{number:02d}", "doc_id":doc["id"], "title": doc["title"], "text": text }

def split_sentences(text:str) -> list[str]:
    """
    Sentences, with each '## Heading' line kept as of its own
    """
    units = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            units.append(line)
        else:
            units.extend(s for s in re.split(r"(?<=[.!?])\s+", line) if s)
    return units

def pack(units:list[str], max_words:int) -> list[str] :

    """
    Join whole units until adding the next one would pass max_words
    """
    # groups holds finished chunks, current is the chunk being build, count is its word total
    groups, current, count = [],[],0

    for unit in units:
        n = len(unit.split())
        if current and count + n > max_words:
            groups.append(" ".join(current))
            current, count = [], 0
        current.append(unit)
        count += n

    if current:
        groups.append(" ".join(current))

    return groups

# ------------------------------   CHUNKING STRATEGIES  -----------------------------------
# whole document
def whole_document(doc:dict) -> list[dict]:
    """
    Baseline .... what our project has done until now
    """
    return [_chunk(doc, 0, doc['body'].strip())]


# fixed_words (if overlap = 0 : fixed with no overlap / if overlap )
def fixed_words(doc:dict, size: int = 100 , overlap:int=0) -> list[dict]:
    """
    Every 'size' words , regardless of sentences or section. Cheap and blind
    """
    if not 0 <= overlap < size : # overlap and size must be grater than 0 and overlap must be a fraction of size
        raise ValueError("Overlap must be at least 0 and smaller than size")
    
    words = doc["body"].split()
    step = size - overlap
    chunks = []

    # range(0, 385, 75)
    for number, start in enumerate(range(0, len(words), step)):
        chunks.append(_chunk(doc, number, " ".join(words[start:start + size])))
        if start + size >= len(words):
            break
    return chunks

# sentenced_packed - Whole sentences only, packed up to max_words. Never cuts a sentence in half.
def sentence_packed(doc:dict, max_words: int = 100) -> list[dict]:
    """
    Whole sentences only, packed up to max_words. Never chop a sentnce.
        - doc:          a corpus document with id, title, body
        - max_words:    soft upper bound on words per chunk.
    """
    units = split_sentences(doc["body"])  # sentence + heading units from this doc's body
    groups = pack(units, max_words)       # joined groups of units each around ~max_words long
    return [_chunk(doc, i, text) for i, text in enumerate(groups)] # structuing chunks as a list of dict adding metadata

    # more pythonic way to do it:
    # return [_chunk(doc, n, text) for n, text in enumerate(pack(split_sentences(doc["body"]), max_words))]


def by_section(doc: dict, max_words: int = 100, contextual: bool = True) -> list[dict]:
    """
    One chunk per '##' section; long sections are packed by sentences.
    contextual=True prefixes each chunk with "<doc title> > <heading>" so a
    chunk that never names its subject still carries it into the embedding.
    """
    chunks, number = [], 0
    parts = re.split(r"(?m)^## ", doc["body"]) if "## " in doc["body"] else [doc["body"]]
    for part in parts:
        heading, _, text = part.partition("\n") if "## " in doc["body"] else ("", "", part)
        heading, text = heading.strip(), text.strip()
        if not text:
            continue
        for piece in pack(split_sentences(text), max_words):
            if contextual:
                prefix = f"{doc['title']} > {heading}\n" if heading else f"{doc['title']}\n"
                piece = prefix + piece
            chunks.append(_chunk(doc, number, piece))
            number += 1
    return chunks

STRATEGIES = {
    "whole_document": whole_document,
    "fixed_100": lambda d: fixed_words(d, size=100, overlap=0),
    "fixed_overlap_25": lambda d: fixed_words(d, size=100, overlap=25),
    "sentences_100": lambda d: sentence_packed(d, max_words=100),
    "sections_plain": lambda d: by_section(d, max_words=150, contextual=False),
    "sections_contextual": lambda d: by_section(d, max_words=150, contextual=True)
}

def chunk_corpus(docs: list[dict], startegy: str) -> list[dict]:
    return [chunk for doc in docs for chunk in STRATEGIES[startegy](doc)]

# Commands to run in REPL:
#   import chunking
#   from corpus import CORPUS_DOCUMENTS
#   from documents import DOCUMENTS
#   ALL_DOCS = DOCUMENTS + CORPUS_DOCUMENTS

#   for strategy in chunking.STRATEGIES:
#       chunks = chunking.chunk_corpus(ALL_DOCS, strategy)
#       print(f"{strategy:25s} → {len(chunks)} chunks")