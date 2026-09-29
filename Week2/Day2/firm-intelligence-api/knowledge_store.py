# embed_text is imported rather than rewritten
# embedding provider has not changed , only where the vectors get stored

import chromadb
from documents import DOCUMENTS
from knowledge import embed_texts

chroma = chromadb.PersistentClient(path="./chroma_store")
# HNSW (Hierarchical Navigable Small World) is a graph based index to perform approximate nearest neighbor (ANN) search.
collection = chroma.get_or_create_collection(
    name="firm_documents",
    configuration={"hnsw": {"space": "cosine"}},
)

def count()->int:
    return collection.count()

def build_index() -> int:
    """
    Embed every document and hand the vectors to chroma.
    """

    texts = [doc["body"] for doc in DOCUMENTS]
    vectors, tokens = embed_texts(texts, input_type="document")
    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        embeddings=vectors,
        documents=texts,
        metadatas=[{"title": doc["title"], "type": doc["type"]} for doc in DOCUMENTS],
    )
    return tokens


def search(question: str, top_k: int = 3) -> list:
    """
    Embed the question and let chroma do the storing.
    """
    if collection.count() == 0:
      raise RuntimeError("Index empty, build it via POST /knowledge/index")
    
    query_vector, _ = embed_texts(question, input_type="query")
    result = collection.query(query_embeddings=query_vector, n_results=top_k)
    return [
        {
            "id": doc_id,
            "title": metadata["title"],
            "text": text,
            # chroma will give us back the distance ... lower is closer
            # we will do 1 - distance in order to flip from return distance , to similarity
            "score": 1 - distance,
        }
        for doc_id, text, metadata, distance in zip(
            result["ids"][0],
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]

# things to note:
# embed_texts is imported not rewritten ... embedding provider has not changed only the storage has
# configuration=.... -> not optional , we are choosing something different from default 
# chroma returns distance, we return similarity
    # in chroma lower is better 
    # in our implementation higher is better
    # 1 - distance converts  it to similarity
# upsert instead of add -> add fails on an id that already exists, upsert overwrites
