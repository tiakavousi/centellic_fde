from data.complaints import COMPLAINTS
from data.customers import CUSTOMERS
from data.enums import CustomerSegment
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/customers", tags=["customers"])

class NewCustomer(BaseModel):
    name: str = Field(min_length=3)
    segment: CustomerSegment
    vulnerability_flag: bool

class Customer(NewCustomer):
    id:int

class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3)
    segment : CustomerSegment | None = None
    vulnerability_flag: bool | None = None

def get_customer_or_404(customer_id:int) -> dict:
    for customer in CUSTOMERS:
        if customer["id"] == customer_id:
            return customer
    raise HTTPException(404, f"customer with id {customer_id} does not exist.")

@router.get("")
def list_customers(segment:CustomerSegment | None = None, vulnerability_flag: bool | None = None):
    results = CUSTOMERS
    if segment is not None:
        results = [c for c in results if c["segment"] == segment]
    if vulnerability_flag is not None:
        results = [c for c in results if c["vulnerability_flag"] == vulnerability_flag]
    return results

@router.get("/{customer_id}")
def get_customer(customer:dict = Depends(get_customer_or_404)):
    return customer

# All complaints for one specific customer
@router.get("/{customer_id}/complaints")
def list_customer_complaints(
    customer: dict = Depends(get_customer_or_404),
  ) -> list[dict]:
    return [c for c in COMPLAINTS if c["customer_id"] == customer["id"]]

@router.post("", status_code=201)
def add_customer(new_customer:NewCustomer) -> dict:
    new_id = max(customer["id"] for customer in CUSTOMERS) + 1
    customer = {"id": new_id, **new_customer.model_dump()}
    CUSTOMERS.append(customer)
    return customer

@router.delete("/{customer_id}", status_code=204)
def remove_customer(customer:Customer= Depends(get_customer_or_404)): 
    CUSTOMERS.remove(customer)

@router.put("/{customer_id}")
def update_customer(
    updated: CustomerUpdate, customer: Customer=Depends(get_customer_or_404)
    ) -> Customer:
    for key, value in updated.model_dump(exclude_unset= True).items():
        customer[key] = value
    return customer
