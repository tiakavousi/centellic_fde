"""
Does the model miss the fact buried in the middle of a long context?
Cost: positions x trails model calls ... the defaults make 15 calls of roughly 6,000 input tokens 
"""
from dotenv import load_dotenv
load_dotenv(".env.local")

import argparse
import random
import re

import llm
from corpus import CORPUS_DOCUMENTS
from documents import DOCUMENTS

# the needle: fact that appears nowhere else and contradicts nothing in the corpus
NEEDLE = {
    "id": "doc-009",
    "title": "Okonwo Bell: Knowledge Team Update",
    "text": "The Okonwo Bell knowledge team catalouged 1,742 precedent document during its summer review."
}

QUESTION = "How many precedent docuemnts did the Okonwo Bell knowledge team catalouge in its summer review?"

POSITIONS = [0.0, 0.25, 0.5, 0.75, 1.0]

# distractors: builds the "haystack" material
def disractors() -> list[dict]:
    blocks = []
    for doc in DOCUMENTS + CORPUS_DOCUMENTS:
        body = doc["body"]
        has_headings = "## " in body
        sections = re.split(r"(?m)^## ", body) if has_headings else [body]
        for section in sections:
            if has_headings:
                heading, _, text = section.partition("\n")
            else:
                heading, text = "", section
            if text.strip():
                title = f"{doc['title']} / {heading.strip()}" if heading.strip() else doc["title"]
                blocks.append({"id": doc["id"], "title": title, "text": text.strip()})
    print("blocks: ", len(blocks))
    return blocks

# haystack : this will allow us to place our needle inside our haystack
def haystack(blocks: list[dict], position: float, seed: int) -> str:
    """
    Shuffle the distraction , then insert the needle at the requested position
    """
    items = blocks[:] # new list, same contents
    random.Random(seed).shuffle(items)
    items.insert(round(position * len(items)), NEEDLE)
    # when position is 0, index is 0 , result is (N = needle)    N 1 2 3 4 5
    # when position is 1.00, index is 5 , result is (N = needle) 3 2 1 5 4 N
    return "\n\n".join(f"[{b['id']}] {b['title']}\n{b['text']}" for b in items)

# found
def found(answer: str) -> bool:
    # match 1742 and 1,742
    return re.search(r"1,?742", answer) is not None

def main() -> None:
    blocks = disractors()
    for position in POSITIONS:
        answers = [llm.answer_from_context(QUESTION, haystack(blocks, position, seed=t))["answer"] for t in range(3)]
        print(position, sum(found(a) for a in answers), "/ 3")

if __name__ == "__main__":
    main()
