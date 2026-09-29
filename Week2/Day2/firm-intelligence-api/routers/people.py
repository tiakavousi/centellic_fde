from fastapi import APIRouter, HTTPException, Depends, Header
from data import PEOPLE
from pydantic import BaseModel, Field
from routers.firms import get_firm_or_404

router = APIRouter(prefix="/people", tags=["people"])

class newPerson(BaseModel):
    name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    firm_id: int = Field(gt=0)

def get_person_or_404(person_id: int) -> dict:
    for person in PEOPLE:
        if person["id"] == person_id:
            return person
    raise HTTPException(status_code=404, detail=f"Person {person_id} not found")    

@router.get("")
def list_people(firm_id: int | None = None):
    results = PEOPLE
    if firm_id is not None:
        results = [p for p in results if p["firm_id"] == firm_id]
    return results

@router.get("/{person_id}")
def get_person(person: dict = Depends(get_person_or_404)):
    return person

@router.post("")
def add_person(new_person:newPerson):
    get_firm_or_404(new_person.firm_id)
    new_id = max(person["id"] for person in PEOPLE) + 1
    person = {
        "id": new_id,
        "name": new_person.name,
        "role": new_person.role,
        "firm_id": new_person.firm_id
    }
    PEOPLE.append(person)
    return person




