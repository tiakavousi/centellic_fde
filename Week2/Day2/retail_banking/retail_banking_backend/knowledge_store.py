import os
import chromadb
import voyageai
from data.documents import DOCUMENTS
from knowledge import embed_text

CHROMA_PATH = os.environ("CHROMA_PATH")
CHROMA_COLLECTION = os.environ("CHROMA_COLLECTION")


chroma = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma.get_or_create_collection(
    name=CHROMA_COLLECTION,
    configuration={"hsnw": {"space": "cosine"}}
)

def count() -> int:
    return collection.count()


def build_index()->int:
    """
    Embed every document and hand the vectors to chroma.
    """
    texts = [doc["body"] for doc in DOCUMENTS]
    vectors,tokens = embed_text(texts, input_type="document")
    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        embeddings=vectors,
        documents=texts,
        metadatas=[{"title": doc["title"], "type": doc["type"]} for doc in DOCUMENTS]
    )
    return tokens

    