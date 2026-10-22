"""
Central settings module. Reads all environment variables in one place.
"""

import os

import config  # noqa: F401 — loads .env.local

# --- Anthropic ---
ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
ANTHROPIC_MODEL: str = os.environ["ANTHROPIC_MODEL"]
MAX_TOKENS: int = int(os.environ["MAX_TOKENS"])
MAX_RETRIES: int = int(os.environ["MAX_RETRIES"])
MODEL_TIMEOUT: float = float(os.environ["MODEL_TIMEOUT"])

# --- Voyage AI ---
VOYAGEAI_API_KEY: str = os.environ["VOYAGEAI_API_KEY"]
VOYAGE_MODEL: str = os.environ["VOYAGE_MODEL"]
EMBEDDING_DIMENSIONS: int = 512  # voyage-3-lite produces 512 floats per text

# --- Chroma (eval pipeline only) ---
CHROMA_PATH: str = os.environ.get("CHROMA_PATH", "./chroma_store")
CHROMA_COLLECTION: str = os.environ.get("CHROMA_COLLECTION", "retail_banking_docs")

# --- Azure AI Search (live API) — auth via DefaultAzureCredential (az login) ---
AZURE_SEARCH_ENDPOINT: str = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_INDEX: str = os.environ.get("AZURE_SEARCH_INDEX", "retail-banking-chunks")
AZURE_SEMANTIC_CONFIG: str = os.environ.get("AZURE_SEMANTIC_CONFIG", "retail-banking-semantic")

# --- Retrieval ---
RELEVANCE_FLOOR: float = float(os.environ.get("RELEVANCE_FLOOR", "0.45"))
TOP_K: int = int(os.environ.get("TOP_K", "3"))

# --- SLA policy ---
ACK_WINDOW_DAYS: int = int(os.environ.get("ACK_WINDOW_DAYS", "3"))
RESPONSE_WINDOW_DAYS: int = int(os.environ.get("RESPONSE_WINDOW_DAYS", "56"))

# --- Refusal Sentence ---
REFUSAL_SENTENCE = "The provided documents do not answer that question."
