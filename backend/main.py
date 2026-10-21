from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    customers_router,
    inventory_items_router,
    order_items_router,
    orders_router,
    payments_router,
    platform_brands_router,
    platform_settings_router,
    products_router,
    reports_router,
    storefront_router,
)

app = FastAPI(title="Ecommerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(inventory_items_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(order_items_router)
app.include_router(payments_router)
app.include_router(reports_router)
app.include_router(platform_settings_router)
app.include_router(platform_brands_router)
app.include_router(storefront_router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Monorepo Backend!"}
