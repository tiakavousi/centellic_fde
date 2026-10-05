import config
from fastapi import FastAPI
from routers.customers import router as customers_router
from routers.complaints import router as complaints_router
from routers.products import router as product_router
from routers.insights import router as insights_router


app = FastAPI(title="Retail Banking Backend")  

app.include_router(customers_router)
app.include_router(complaints_router)
app.include_router(product_router)
app.include_router(insights_router)

@app.get("/health")
def get_health():
    return {"status": "ok"}



