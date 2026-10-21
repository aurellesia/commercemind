from .customers import router as customers_router
from .inventory_items import router as inventory_items_router
from .order_items import router as order_items_router
from .orders import router as orders_router
from .payments import router as payments_router
from .products import router as products_router
from .reports import router as reports_router
from .settings import platform_brands_router, platform_settings_router, storefront_router

__all__ = [
    "customers_router",
    "inventory_items_router",
    "order_items_router",
    "orders_router",
    "payments_router",
    "products_router",
    "reports_router",
    "platform_settings_router",
    "platform_brands_router",
    "storefront_router",
]
