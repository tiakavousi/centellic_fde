"""
Azure AI search... this is going to do the same jon as knowledge_store (count, build_index, search).
One search call does 3 things:
    1. keyword search (bm25) and vector search run together, and Azure fuses them with RRF
    2. the semantic reranker rereads the top results beside the question and scores each 0 to 4
    3. the hits come back best first , carrying that score for the relevance gate (gate.py)

User Query: "company annual earnings"
  │
  ├── 1. KEYWORD SEARCH
  │   Looks for exact/similar words in title & text fields
  │   Returns: [chunk-3, chunk-7, chunk-12, ...]
  │
  ├── 2. VECTOR SEARCH
  │   Embeds the query → 512 floats
  │   Finds chunks with similar embeddings (similar meaning)
  │   Returns: [chunk-7, chunk-15, chunk-2, ...]
  │
  ├── 3. FUSION (RRF)
  │   Merges both lists by rank
  │   Returns: [chunk-7, chunk-3, chunk-15, chunk-2, chunk-12, ...]
  │
  └── 4. SEMANTIC RERANKER
      Reads the query + each chunk together using a language model
      Re-scores based on actual meaning & relevance
      Returns: [chunk-15, chunk-7, chunk-2, chunk-3, chunk-12, ...]
                   ↑
          "annual earnings report" chunk — didn't contain exact words
          but reranker understood it was the most relevant

Each step narrows and improves the quality — by the end you get the most semantically relevant results at the top.
"""

import time
from functools import cache

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

import azure_index
import bm25
import chunk_index
import settings

# semantic ranker only ever reads the top 50 , so we'll ask for that many and trim to top_k afterwards
CANDIDATES = 50

# chunks per upload request
BATCH = 100

NOT_BUILT = "The Azure index is empty or missing. Build it with python -m azure_build"
# index creation is a one-time infrastructure setup, not application logic
# it should run once when you deploy, not every time your app starts.


# pt2 - signing in an the two clients
@cache  # similar to @lru_cache(maxsize=None)
def _credential() -> DefaultAzureCredential:
    """
    Signs in as you after 'az login' , or as a manged identity once depolyed
    """
    return DefaultAzureCredential()


def _endpoint() -> str:
    if not settings.AZURE_SEARCH_ENDPOINT:
        raise RuntimeError(
            "AZURE_SEARCH_ENDPOINT is not set. "
            "Example: export AZURE_SEARCH_ENDPOINT=https://<your-service>.search.windows.net"
        )
    return settings.AZURE_SEARCH_ENDPOINT


@cache
def search_client() -> SearchClient:
    return SearchClient(
        endpoint=_endpoint(),
        index_name=settings.AZURE_SEARCH_INDEX,
        credential=_credential(),
    )


@cache
def index_client() -> SearchIndexClient:
    return SearchIndexClient(
        endpoint=_endpoint(),
        credential=_credential(),
    )


def _identifiers(text: str) -> set[str]:
    """
    Tokens containing a digit (e.g. 3307), same as in hybrid.py
    """
    return {
        token for token in bm25.tokenize(text) if any(char.isdigit() for char in token)
    }


def count() -> int:
    """
    Number of chunks in Azure index, 0 if it does not exist
     - needs only the query permission.
    """
    try:
        return search_client().search(
            search_text="*", include_total_count=True, top=0
        ).get_count()
    except ResourceNotFoundError:
        return 0


# serahc with vector
# set every chunk from its voyage vector
# make new documents searchable
# drop and recreate index
def search_with_vector(
    question: str, query_vector: list[float], top_k: int = 3, semantic: bool = True
) -> list[dict]:
    # clean the question
    # What is  "LP-3307" ?
    # what is lp 3307
    search_text = " ".join(bm25.tokenize(question)) or "*"

    # build one query that will do 2 searches
    # keyword half and vector half
    options = {
        "search_text": search_text,  # keyword half
        "vector_queries": [  # vector half
            VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=CANDIDATES,
                fields="embedding",
            )
        ],
        "select": ["chunk_id", "doc_id", "title", "text"],
        "top": max(top_k, CANDIDATES),
    }

    # switch on the semantic reranker
    if semantic:
        options["query_type"] = "semantic"
        options["semantic_configuration_name"] = settings.SEMANTIC_CONFIG

    # run it, then trim it using the top_k , and if needed handle any missing index
    try:
        results = list(search_client().search(**options))[:top_k]
    except ResourceNotFoundError as error:  # index doesn't exist
        raise RuntimeError(NOT_BUILT) from error
    if not results:  #  index exists but is empty
        raise RuntimeError(NOT_BUILT)

    # trun each result into a hit
    wanted = _identifiers(question) if settings.EXACT_MATCH_RULE else set()
    hits = []
    for result in results:
        rerank = result.get("@search.reranker_score")
        fused = result["@search.score"]
        hits.append(
            {
                "id": result["doc_id"],
                "chunk_id": result["chunk_id"],
                "title": result["title"],
                "text": result["text"],
                "score": rerank if rerank is not None else fused,
                "rerank_score": rerank,
                "rrf": round(fused, 5),
                "exact_match": bool(wanted & set(bm25.tokenize(result["text"]))),
            }
        )
    return hits


def _local_chunks(startegy: str) -> list[dict]:
    """
    Every chunk woth its Voyage vector
    Reusing the vectors costs no embedding tokens (also means Azure has the exact same chunks and vectors as the local search)
    """
    chunk_index.build(startegy)  # free when up to date
    # stored is a dict of parallel lists
    # stored["ids"], stored["embedding"]...
    stored = chunk_index.collection_for(startegy).get(
        include=["embeddings", "documents", "metadatas"]
    )
    # walk all 4 lists together
    return [
        {
            "chunk_key": azure_index.key_for(chunk_id),
            "chunk_id": chunk_id,
            "doc_id": meta["doc_id"],
            "title": meta["title"],
            "text": text,
            "embedding": [float(number) for number in vector],
        }
        for chunk_id, vector, text, meta in zip(
            stored["ids"],
            stored["embeddings"],
            stored["documents"],
            stored["metadatas"],
        )
    ]


def _wait_until_counted(expected: int, seconds: int = 30) -> None:
    """
    New documents become searchable a moment after upload, so we wait for the count to catchup
    """
    deadline = time.time() + seconds
    while time.time() < deadline:
        if count() >= expected:
            return
        time.sleep(1)
    raise RuntimeError(
        f"Uploaded {expected} chunks, but the index reports {count()} after {seconds} seconds"
    )


def build_index(startegy: str) -> int:
    """
    Drop and recreate the Azure index... then load every chunk... return chunk count
    """
    docs = _local_chunks(startegy)
    keys = [doc["chunk_key"] for doc in docs]
    if len(set(keys)) != len(keys):
        raise RuntimeError(
            "Identical chunk ids trun into the same Azure key, so chunks would overwrite each other"
        )
        # the ids if doc-01#01 and doc-01_01 would both become doc-01_01

    # check the vector sizes
    bad = [doc for doc in docs if len(doc["embedding"]) != azure_index.DIMENTIONS]
    if bad:
        raise RuntimeError(
            f"{bad[0]['chunk_id']} has {len(bad[0]['embedding'])} numbers per vector, "
            f"but the index expects {azure_index.DIMENTIONS}. Did the embedding model change?"
        )
    
    name = settings.AZURE_SEARCH_INDEX

    try:
        index_client().delete_index(name)
    except ResourceNotFoundError:
        pass

    index_client().create_index(azure_index.index_definition(name))

    for start in range(0, len(docs), BATCH):
        results = search_client().upload_documents(documents=docs[start:start+BATCH])
        failed = [result for result in results if not result.succeeded]
        if failed:
            raise RuntimeError(f"Azure rejected {len(failed)} chunks, First: {failed[0].error_message}")

    # wait, then report
    _wait_until_counted(len(docs))

    return len(docs)