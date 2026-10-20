# embed_text is imported rather than rewritten
# embedding provider has not changed , only where the vectors get stored
import knowledge
import chunk_index
import hybrid

# our chosen chunking startegy
CHUNK_STARTEGY = "sections_contextual"

SEARCH_MODE = "hybrid"

# set to local or azure
SEARCH_BACKEND = "azure"

def count()->int:
    if SEARCH_BACKEND == "azure":
        import azure_store
        return azure_store.count()

    return chunk_index.collection_for(CHUNK_STARTEGY).count()

def build_index() -> int:
    """
    Chunk and embed the corpus .... free if nothing has changed since the last build.
    """
    if SEARCH_BACKEND == "azure":
        raise RuntimeError("The app only reads the Azure index, Build it with python -m azure_build")
    
    return chunk_index.build(CHUNK_STARTEGY)["embedding_tokens"]

# applys only for local backend
def search(question: str, top_k: int = 3) -> list:
    """
    Embed the question and let chroma do the storing.
    """
    if SEARCH_BACKEND == "azure":
        import azure_store
        query_vectors, _ = knowledge.embed_texts([question], input_type="query")
        return azure_store.search_with_vector(question, query_vectors[0], top_k)

    if count() == 0:
      raise RuntimeError("Index is empty, call POST /knowledge/index first")

    query_vectors, _ = knowledge.embed_texts(question, input_type="query")

    if SEARCH_MODE == "hybrid":
        return hybrid.search_with_vector(CHUNK_STARTEGY, question, query_vectors[0], top_k)
    
    return chunk_index.search_with_vectors(CHUNK_STARTEGY, query_vectors, k=top_k)[0]

#