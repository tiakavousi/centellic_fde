"""Structured customer records. SYNTHETIC PLACEHOLDER DATA ONLY.

The customer is the "person" entity in this domain. Complaints reference
customers by id. The vulnerability_flag is indicative — handlers are still
expected to spot vulnerability signals in the complaint text itself.
"""

from typing import Any

from data.enums import CustomerSegment

# ustomers (segment, vulnerability-flag),
CUSTOMERS: list[dict[str, Any]] = [
    {
        "id": 1,
        "name": "Ada Owens",
        "segment": CustomerSegment.mass_market,
        "vulnerability_flag": False,
    },
    {
        "id": 2,
        "name": "Alan Whitfield",
        "segment": CustomerSegment.premier,
        "vulnerability_flag": False,
    },
    {
        "id": 3,
        "name": "Grace Ndlovu",
        "segment": CustomerSegment.mass_market,
        "vulnerability_flag": True,
    },
    {
        "id": 4,
        "name": "Dennis O'Rourke",
        "segment": CustomerSegment.business,
        "vulnerability_flag": False,
    },
    {
        "id": 5,
        "name": "Barbara Blackwood",
        "segment": CustomerSegment.mass_market,
        "vulnerability_flag": True,
    },
    {
        "id": 6,
        "name": "Geoffrey Pearl",
        "segment": CustomerSegment.premier,
        "vulnerability_flag": False,
    },
]
