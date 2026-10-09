"""
One chroma collection per chunking strategy. so that strategies can be compaired side by side
If either changes , the collection will be rebuilt from the scratch.
"""

import chromadb
import hashlib
import chunking
import knowledge
from corpus import CORPUS_DOCUMENTS
from documents import DOCUMENTS

ALL_DOCUMENTS = DOCUMENTS + CORPUS_DOCUMENTS

BATCH_SIZE = (
    128  # Voyage's own guidance : bactch documents to stay well inside rate limits
)

chroma = chromadb.PersistentClient(path="./chroma_store")


def collection_name(startegy: str) -> str:
    return f"chunk_{startegy}"


def collection_for(startegy: str):
    return chroma.get_or_create_collection(
        name=collection_name(startegy), configuration={"hnsw": {"space": "cosine"}}
    )


def embed_batched(texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    """
    embed every number of texts in batches, return all vectors and total token count .
    """
    vectors = list[list[float]] = []
    tokens = 0

    for start in range(0, len(texts), BATCH_SIZE):
        batch_vectors, batch_tokens = knowledge.embed_texts(
            texts[start : start + BATCH_SIZE], input_type=input_type
        )
        vectors.extend(batch_vectors)
        tokens += batch_tokens

    return vectors, tokens


def fingerprint(chunks: list[dict]) -> str:
    """
    the fingerprint changes if the text, the model or the order changes ... and stays put if nothing does
    """
    # SHA-256 : a recipe that turns any text into a fixed-length code (64 char)
    digest = hashlib.sha256(knowledge.EMBED_MODEL.encode())
    for c in chunks:
        digest.update(f"{c['id']}\n{c['text']}\n".encode())
    return digest.hexdigest()[
        :16
    ]  # hexdigest gives us the entire code , we are grabing the first 16 char from the code (magic number)


def build(startegy: str, force: bool = False) -> dict:
    """
    Makes sure the strategy's collection matches the current corpus, chunker, model
    ANSWERS ONE QUESTION : is the index I already have still correct?
    """
    # part 1 : check
    chunks = chunking.chunk_corpus(ALL_DOCUMENTS, startegy)
    fp = fingerprint(chunks)
    col = collection_for(startegy)
    stored = col.get(limit=1, include=["metadatas"])["metadatas"]

    if (
        not force
        and col.count() == len(chunks)
        and stored
        and stored[0].get("fingerprint") == fp
    ):
        return {
            "strategy": startegy,
            "chunks": len(chunks),
            "embedding_tokens": 0,
            "rebuilt": False,
        }

    # part 2 : rebuild
    #   Upsert would be fine only if you could guarantee chunk IDs are stable and the set never shrinks — 
    # which isn't true when the chunking strategy, chunk size, or source corpus can change.
    # se we need to delete the collection 
    # Drop the whole collection instead of upserting: chunk IDs/counts can change
    # across rebuilds (new corpus, different chunker), and upsert would leave
    # orphaned chunks from the previous build behind.
    try:
        chroma.delete_collection(collection_name)
    except Exception:
        pass

    col = collection_for(startegy)
    vectors, tokens = embed_batched([c["text"] for c in chunks], input_type="document")
    col.upsert(
        ids=[c["id"] for c in chunks],
        embeddings=vectors,
        documents=[c["text"] for c in chunks],
        metadatas=[
            {"doc_id": c["doc_id"], "title": c["title"], "fingerprint": fp}
            for c in chunks
        ],
    )
    return {
        "startegy": startegy,
        "chunks": len(chunks),
        "tokens": tokens,
        "rebuild": True,
    }
