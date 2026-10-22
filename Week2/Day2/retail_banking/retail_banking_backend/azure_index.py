import settings
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


VECTOR_PROFILE = "retail_vector_profile"
ALGORITHM = "retail_hnsw"

# key_for helper exists because Azure doesn't allow # in index keys, so doc-105#02 becomes doc-105_02
def key_for(chunk_id: str) -> str:
    return chunk_id.replace("#", "_")

def index_definition(name: str) -> SearchIndex:
    fields = [
        SimpleField(name="chunk_key", type=SearchFieldDataType.String, key=True),       # doc-001_00
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, filterable=True), # doc-001#00
        SimpleField(name="doc_id", type=SearchFieldDataType.String, filterable=True),   # doc-001
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="text", type=SearchFieldDataType.String),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=settings.EMBEDDING_DIMENSIONS,
            vector_search_profile_name=VECTOR_PROFILE,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name=ALGORITHM, parameters=HnswParameters(metric="cosine"))],
        profiles=[VectorSearchProfile(name=VECTOR_PROFILE, algorithm_configuration_name=ALGORITHM)],
    )

    semantic_search = SemanticSearch(configurations=[SemanticConfiguration(
        name=settings.AZURE_SEMANTIC_CONFIG,
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[SemanticField(field_name="text")],
        ),
    )])

    return SearchIndex(name=name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)