import chromadb
import hashlib
import chunking
from data.documents import DOCUMENTS
from data.corpus import CORPUS_DOCUMENTS
import settings
import embedding

ALL_DOCUMENTS = DOCUMENTS + CORPUS_DOCUMENTS

BATCH_SIZE = 128

chroma = chromadb.PersistentClient(settings.CHROMA_PATH)

def collection_name(strategy:str) -> str:
    return f"chunk_{strategy}"

def collection_for(startegy:str):
    return chroma.get_or_create_collection(
        name=collection_name(startegy) , configuration={"hnsw": {"space": "cosine"}}
    )

def embed_batched(texts: list[str], input_type:str) -> tuple[list[list[float]], int]:
    vectors: list[list[float]] = []
    tokens = 0
    for start in range(0, len(texts), BATCH_SIZE):
        batch_vectors, batch_tokens = embedding.embed_texts(
            texts[start : start + BATCH_SIZE], input_type=input_type
        )
        vectors.extend(batch_vectors)
        tokens += batch_tokens

    return vectors, tokens

def fingerprint(chunks: list[dict]) -> str:
    """
    the fingerprint changes if the text, the model or the order changes ... and stays put if nothing does
    """
    digest = hashlib.sha256(settings.VOYAGE_MODEL.encode())
    for c in chunks:
        digest.update(f"{c['id']}\n{c['text']}\n".encode())
    return digest.hexdigest()[
        :16
    ]

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
    
    try:
        chroma.delete_collection(collection_name(startegy))
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
        "strategy": startegy,
        "chunks": len(chunks),
        "embedding_tokens": tokens,
        "rebuilt": True,
    }

def search_with_vectors(
    startegy: str, query_vectors: list[list[float]], k: int
) -> list[list[dict]]:
    """
    we embed the question once, then searches many strategies with the same vectors.
    """

    col = collection_for(startegy)
    if col.count() == 0:
        raise RuntimeError(f"Index for '{startegy}' is empty, build it first)")

    result = col.query(query_embeddings=query_vectors, n_results=min(k, col.count()))

    return [
        [
            {
                "id": meta["doc_id"],
                "chunk_id": chunk_id,
                "title": meta["title"],
                "text": text,
                "score": 1 - distance,
            }
            for chunk_id, text, meta, distance in zip(ids, docs, metas, dists)
        ]
        for ids, docs, metas, dists in zip(
            result["ids"],
            result["documents"],
            result["metadatas"],
            result["distances"],
        )
    ]



