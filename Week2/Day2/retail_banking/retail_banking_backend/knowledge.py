import config  # noqa: F401 — loads .env.local
import os
import voyageai


VOYAGEAI_API_KEY = os.environ["VOYAGEAI_API_KEY"]
VOYAGE_MODEL = os.environ["VOYAGE_MODEL"]


voyage = voyageai.Client(
    api_key=VOYAGEAI_API_KEY,
    max_retries=3,
    timeout=30
)

def embed_text(texts:list[str], input_type:str) -> tuple[list[list[float]], int]:
    result = voyage.embed(texts=texts, model=VOYAGE_MODEL, input_type=input_type)
    return result.embeddings, result.total_tokens