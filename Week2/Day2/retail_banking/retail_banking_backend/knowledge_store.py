import os

import chromadb
import config
from data.documents import DOCUMENTS
from knowledge import embed_text

CHROMA_PATH = os.environ["CHROMA_PATH"]
CHROMA_COLLECTION = os.environ["CHROMA_COLLECTION"]
TOP_K = int(os.environ["TOP_K"])

chroma = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma.get_or_create_collection(
    name=CHROMA_COLLECTION,
    metadata={"hnsw:space": "cosine"},
)

def count() -> int:
    return collection.count()


def build_index()->int:
    """
    Embed every document and hand the vectors to chroma.
    """
    texts = [doc["body"] for doc in DOCUMENTS]
    vectors,tokens = embed_text(texts, input_type="document")
    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        embeddings=vectors,
        documents=texts,
        metadatas=[{"title": doc["title"], "type": doc["type"]} for doc in DOCUMENTS]
    )
    return tokens

def search(query: str, top_k:int = TOP_K) -> list[dict]:
    if collection.count() == 0:
        raise RuntimeError("Index empty, build it via POST /knowledge/index")

    vectors, _ = embed_text([query], input_type="query")
    result = collection.query(query_embeddings=vectors, n_results=top_k)
    return [
        {
            "id": doc_id,
            "title": metadata["title"],
            "body": body,
            "score": 1 - distance
        } 
        for doc_id, body, metadata, distance in zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]
    


    