from fastapi import APIRouter, Depends, HTTPException
from data.complaints import COMPLAINTS
from pydantic import BaseModel
from data.enums import ComplaintStatus, Severity, ProductType, Channel
from routers.customers import get_customer_or_404
from datetime import date

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

def get_complaint_or_404(complaint_id:int) -> Complaint:
    for complaint in COMPLAINTS:
        if complaint["id"] == complaint_id:
            return complaint
    raise HTTPException(404, f"complain with {complaint_id} id does not exists.")

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
def get_complaint(complaint:Complaint=Depends(get_complaint_or_404)):
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