from datetime import date

from data.complaints import COMPLAINTS, get_complaint
from data.enums import Channel, ComplaintStatus, ProductType, Severity
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from routers.customers import get_customer_or_404

router = APIRouter(prefix="/complaints", tags=["complaints"])

class NewComplaint(BaseModel):
    customer_id: int
    product: ProductType
    channel: Channel
    severity: Severity
    status: ComplaintStatus
    opened_date: date
    summary: str

class Complaint(NewComplaint):
    id: int

class ComplaintUpdate(BaseModel):
    status: ComplaintStatus | None = None
    severity: Severity | None = None
    summary: str | None = None

def get_complaint_or_404(complaint_id: int) -> dict:
    """HTTP wrapper: 404 if not found"""
    complaint = get_complaint(complaint_id)
    if complaint is None:
        raise HTTPException(404, f"complaint with id {complaint_id} does not exist.")
    return complaint

@router.get("")
def list_complaints(
    status: ComplaintStatus | None = None, 
    product: ProductType | None = None, 
    severity: Severity | None = None
    ) -> list[Complaint]:

    results = COMPLAINTS
    if status is not None:
        results = [c for c in results if c["status"] == status]
    if product is not None:
        results = [c for c in results if c["product"] == product]
    if severity is not None:
        results = [c for c in results if c["severity"] == severity]

    return results

@router.get("/{complaint_id}")
def get_complaint_by_id(complaint:Complaint=Depends(get_complaint_or_404)):
    return complaint

@router.post("", status_code=201)
def add_complaint(new_complaint:NewComplaint):
    get_customer_or_404(new_complaint.customer_id)
    new_id = max(c["id"] for c in COMPLAINTS ) + 1
    complaint = {
        "id": new_id,
        **new_complaint.model_dump()
    }
    COMPLAINTS.append(complaint)
    return complaint

@router.put("/{complaint_id}")
def update_complaint(
    updated:ComplaintUpdate, 
    complaint:Complaint=Depends(get_complaint_or_404)
    ) -> Complaint:

    for key,value in updated.model_dump(exclude_unset = True).items():
        complaint[key] = value

    return complaint