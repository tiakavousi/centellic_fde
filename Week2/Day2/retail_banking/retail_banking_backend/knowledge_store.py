import chunk_index
import embedding

CHUNK_STRATEGY = "sections_contextual"
SEARCH_BACKEND = "azure"  # "azure" | "chroma"


def count() -> int:
    if SEARCH_BACKEND == "azure":
        import azure_store
        return azure_store.count()
    return chunk_index.collection_for(CHUNK_STRATEGY).count()


def build_index() -> int:
    if SEARCH_BACKEND == "azure":
        raise RuntimeError("The app only reads the Azure index. Build it with python -m azure_build")
    return chunk_index.build(CHUNK_STRATEGY)["embedding_tokens"]


def search(question: str, top_k: int = 3) -> list:
    if SEARCH_BACKEND == "azure":
        import azure_store
        query_vectors, _ = embedding.embed_texts([question], input_type="query")
        return azure_store.search_with_vector(question, query_vectors[0], top_k)

    if count() == 0:
        raise RuntimeError("Index is empty, call POST /knowledge/index first")

    query_vectors, _ = embedding.embed_texts([question], input_type="query")
    return chunk_index.search_with_vectors(CHUNK_STRATEGY, query_vectors, k=top_k)[0]
