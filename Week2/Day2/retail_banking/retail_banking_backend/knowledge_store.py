import chromadb

import settings
from data.documents import DOCUMENTS
from embedding import embed_texts

chroma = chromadb.PersistentClient(path=settings.CHROMA_PATH)

collection = chroma.get_or_create_collection(
    name=settings.CHROMA_COLLECTION,
    metadata={"hnsw:space": "cosine"},
)

def count() -> int:
    return collection.count()

def build_index()->int:
    """
    Embed every document and hand the vectors to chroma.
    """
    texts = [doc["body"] for doc in DOCUMENTS]
    vectors,tokens = embed_texts(texts, input_type="document")
    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        embeddings=vectors,
        documents=texts,
        metadatas=[{"title": doc["title"], "type": doc["type"]} for doc in DOCUMENTS]
    )
    return tokens

def search(query: str, top_k:int = settings.TOP_K) -> list[dict]:
    if collection.count() == 0:
        raise RuntimeError("Index empty, build it via POST /knowledge/index")

    vectors, _ = embed_texts([query], input_type="query")
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
    


    