"""Structured product records. SYNTHETIC PLACEHOLDER DATA ONLY.

Each complaint references a product by id (complaints.product_id -> PRODUCTS.id).
terms_document_id links to the product's terms & conditions in the document
corpus, or None if no terms document exists in the corpus.
"""

from typing import Any


PRODUCTS: list[dict[str, Any]] = [
    {
        "id": 1,
        "type": "current_account",
        "terms_document_id": "doc-007",
    },
    {
        "id": 2,
        "type": "credit_card",
        "terms_document_id": None,
    },
    {
        "id": 3,
        "type": "mortgage",
        "terms_document_id": None,
    },
    {
        "id": 4,
        "type": "personal_loan",
        "terms_document_id": None,
    },
    {
        "id": 5,
        "type": "savings",
        "terms_document_id": None,
    },
]
