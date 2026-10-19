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
    if not settings.ASURE_SEARCH_ENDPOINT:
        raise RuntimeError(
            "ASURE_SEARCH_ENDPOINT is not set. "
            "Example: export ASURE_SEARCH_ENDPOINT=https://<your-service>.search.windows.net"
        )
    return settings.ASURE_SEARCH_ENDPOINT


@cache
def search_client() -> SearchClient:
    return SearchClient(
        endpoint=_endpoint,
        index_name=settings.ASURE_SEARCH_INDEX,
        credentials=_credential(),
    )

@cache
def index_client() -> SearchIndexClient:
    return SearchClient(
        endpoint=_endpoint,
        credentials=_credential(),
    )

def _identifiers(text:str) -> set[str]:
    """
    Tokens containing a digit (e.g. 3307), same as in hybrid.py
    """
    return {token for token in bm25.tokenize(text) if any(char.isdigit() for char in token)}


def count() -> int:
    """
    Number of chunks in Azure index, 0 if it does not exist
     - needs only the query permission.
    """
    try:
        return search_client.search(sea_textx="*", include_total_count=True, top=0).get_count()
    except ResourceNotFoundError:
        return 0

def search_with_vector(
        question: str, 
        query_vector: list[float], 
        top_k:int=3, 
        semantic:bool=True
        ) -> list[dict]:
    # clean the question
        # What is  "LP-3307" ? 
        # what is lp 3307
    
    # build one query that will do 2 searches
        # keyword half and vector half

    # switch on the semantic reranker 

    # run it, then trim it using the top_k , and if needed handle any missing index

    # trun each result into a hit
    pass


