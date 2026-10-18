import os
import sys

os.environ.setdefault("RELEVANCE_FLOOR", "0.75")
os.environ.setdefault("ACK_WINDOW_DAYS", "3")
os.environ.setdefault("RESPONSE_WINDOW_DAYS", "56")
os.environ.setdefault("VOYAGEAI_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("VOYAGE_MODEL", "test-model")
os.environ.setdefault("CHROMA_PATH", "test-path")
os.environ.setdefault("CHROMA_COLLECTION", "test-collection")
os.environ.setdefault("TOP_K", "3")


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
