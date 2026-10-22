import settings
import voyageai

voyage = voyageai.Client(
    api_key=settings.VOYAGEAI_API_KEY,
    max_retries=3,
    timeout=30
)

def embed_texts(texts:list[str], input_type:str) -> tuple[list[list[float]], int]:
    result = voyage.embed(texts=texts, model=settings.VOYAGE_MODEL, input_type=input_type)
    return result.embeddings, result.total_tokens