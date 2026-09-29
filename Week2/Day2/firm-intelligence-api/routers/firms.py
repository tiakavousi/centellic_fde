from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from data import FIRMS


router = APIRouter(prefix="/firms", tags=["firms"])


_seen_keys: dict[str, dict] = {}

class NewFirm(BaseModel):
    name: str = Field(min_length=1)
    jurisdiction: str = Field(min_length=1, max_length=5)
    revenue_usd_m: float = Field(gt=0)
    lawyers: int = Field(gt=0)
    equity_partners: int = Field(gt=0)


def get_firm_or_404(firm_id: int) -> dict:
    for firm in FIRMS:
        if firm["id"] == firm_id:
            return firm
    raise HTTPException(status_code=404, detail=f"Firm {firm_id} not found")


@router.get("")
# add two optional parameters (not a path parametrs)
def list_firms(jurisdiction: str | None = None, min_revenue: float | None = None):
    results = FIRMS
    if jurisdiction is not None:
        results = [f for f in results if f["jurisdiction"] == jurisdiction]
    if min_revenue is not None:
        results = [f for f in results if f["revenue_usd_m"] >= min_revenue]
    return results


@router.get("/{firm_id}")
def get_firm(firm: dict = Depends(get_firm_or_404)):
    return firm


@router.get("/{firm_id}/benchmarks")
def get_firm_benchmarks(firm: dict = Depends(get_firm_or_404)):
    revenue = firm["revenue_usd_m"]
    return {
        "id": firm["id"],
        "name": firm["name"],
        "revenue_per_lawyer_usd": round(revenue * 1_000_000 / firm["lawyers"]),
        "profit_per_equity_partners": round(
            revenue * 1_000_000 * 0.35 / firm["equity_partners"]
        ),
    }


@router.post("", status_code=201)
def add_firm(new_firm: NewFirm, idempotency_key: str | None = Header(default=None)):
    if idempotency_key is not None and idempotency_key in _seen_keys:
        return _seen_keys[idempotency_key]
    new_id = max(firm["id"] for firm in FIRMS) + 1
    firm = (
        {
            "id": new_id,
            "name": new_firm.name,
            "jurisdiction": new_firm.jurisdiction,
            "revenue_usd_m": new_firm.revenue_usd_m,
            "lawyers": new_firm.lawyers,
            "equity_partners": new_firm.equity_partners,
        },
    )
    FIRMS.append(firm)
    if idempotency_key is not None:
        _seen_keys[idempotency_key] = firm
        
    return firm


@router.put("/{firm_id}")
def update_firm(updated_firm: NewFirm, firm: dict = Depends(get_firm_or_404)):
    firm["name"] = updated_firm.name
    firm["jurisdiction"] = updated_firm.jurisdiction
    firm["revenue_usd_m"] = updated_firm.revenue_usd_m
    firm["lawyers"] = updated_firm.lawyers
    firm["equity_partners"] = updated_firm.equity_partners
    return firm


@router.delete("/{firm_id}", status_code=204)
def delete_firm(firm: dict = Depends(get_firm_or_404)):
    FIRMS.remove(firm)
    return
