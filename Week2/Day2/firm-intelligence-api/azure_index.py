"""
What a chunk looks like inside Azure AI Search - one place defines our index.
Fields:
    - chunk_key
    - chunk_id
    - doc_id
    - title
    - text
    - embedding

index_definition()
  │
  ├── Part 1 — Fields (the columns of your index)
  │   ├── chunk_key    → unique key Azure uses to identify each document (# replaced with _)
  │   ├── chunk_id     → original ID, kept for filtering (e.g. "doc-105#02")
  │   ├── doc_id       → lets you fetch all chunks belonging to one document
  │   ├── title        → full-text searchable
  │   ├── text         → full-text searchable (the actual chunk content)
  │   └── embedding    → 512 floats, used for vector/semantic similarity search
  │
  ├── Part 2 — VectorSearch (how HNSW algorithm runs over the embedding field)
  │
  └── Part 3 — SemanticSearch (re-ranks results using language understanding)

"""
# building blocks from pythons azure package
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)

import settings

DIMENTIONS = 512 #Voyage-3-lite produces 512 per text
VECTOR_PROFILE = "firm_vector_profile"
ALGORITHM = "firm_hnsw"

# key_for helper exists because Azure doesn't allow # in index keys, so doc-105#02 becomes doc-105_02
def key_for(chunk_id:str) -> str:
    # e.g. doc-105#02 --> doc-105_02
    return chunk_id.replace("#" , "_")

def index_definition(name: str) -> SearchIndex:
    # part1 : defining the columns
    fields =[
        SimpleField(name="chunk_key", type=SearchFieldDataType.String, key=True),       # doc-05_02
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, filterable=True), # doc-05#02
        SimpleField(name="doc_id", type=SearchFieldDataType.String, filterable=True),   # doc-05
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="text", type=SearchFieldDataType.String),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=DIMENTIONS,
            vector_search_profile_name=VECTOR_PROFILE,
        )
    ]
    # part2 -  VectorSearch (how HNSW algorithm runs over the embedding field)
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name=ALGORITHM, parameters=HnswParameters(metric="cosine"))],
        profiles=[VectorSearchProfile(name=VECTOR_PROFILE, algorithm_configuration_name=ALGORITHM)],
    )

    # part 3 - SemanticSearch (re-ranks results using language understanding)
    semantic_search = SemanticSearch(configurations=[SemanticConfiguration(
        name=settings.SEMANTIC_CONFIG,
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[SemanticField(field_name="text")],
        )
    )])

    return SearchIndex(name=name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)

