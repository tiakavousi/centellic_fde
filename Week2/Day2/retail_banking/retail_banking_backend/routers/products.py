from fastapi import APIRouter,HTTPException,Depends
from data.products import PRODUCTS
from pydantic import BaseModel
from data.enums import ProductType

router = APIRouter(prefix="/products", tags = ["products"])

class Product(BaseModel):
    id: int
    type: ProductType
    active: bool = True

class ProductUpdate(BaseModel):
    active: bool

def get_product_or_404(product_id: int) -> dict:
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p
    raise HTTPException(404, f"product with id {product_id} does not exist")

@router.get("")
def list_products(include_inactive: bool = False) -> list[Product]:
    if include_inactive:
        return PRODUCTS
    return [p for p in PRODUCTS if p["active"]]

@router.get("/{product_id}")
def get_product(product: dict = Depends(get_product_or_404)) -> Product:
    return product

@router.put("/{product_id}", status_code=201)
def update_product(updated:ProductUpdate, product:dict = Depends(get_product_or_404)) -> Product:
    product["active"] = updated.active
    return product


@router.delete("/{product_id}", status_code=204)
def remove_product(product:dict = Depends(get_product_or_404)) -> None:
    # soft delete, only changing the active to false
    product["active"] = False
