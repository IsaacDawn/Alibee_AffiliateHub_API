# backend/routes/__init__.py
from fastapi import APIRouter
from .health import router as health_router
from .products import router as products_router
from .simple_search import router as simple_search_router
from .categories import router as categories_router
from .stats import router as stats_router
from .exchange import router as exchange_router
from .check import router as check_router
from .save import router as save_router
from .database import router as database_router
from .likes import router as likes_router
from .custom_titles import router as custom_titles_router
from .dictionary import router as dictionary_router
from .currency_rates import router as currency_rates_router
from .currency_converter import router as currency_converter_router
from .currency_detector import router as currency_detector_router
from .currency_products import router as currency_products_router
from .comprehensive_search import router as comprehensive_search_router

# Create main router
api_router = APIRouter()

# Include all route modules
api_router.include_router(health_router, tags=["health"])
api_router.include_router(products_router, tags=["products"])
api_router.include_router(simple_search_router, tags=["search"])
api_router.include_router(categories_router, tags=["categories"])
api_router.include_router(stats_router, tags=["stats"])
api_router.include_router(exchange_router, tags=["exchange"])
api_router.include_router(check_router, tags=["check"])
api_router.include_router(save_router, tags=["save"])
api_router.include_router(database_router, tags=["database"])
api_router.include_router(likes_router, tags=["likes"])
api_router.include_router(custom_titles_router, tags=["custom-titles"])
api_router.include_router(dictionary_router, tags=["dictionary"])
api_router.include_router(currency_rates_router, tags=["currency-rates"])
api_router.include_router(currency_converter_router, prefix="/currency", tags=["currency-converter"])
api_router.include_router(currency_detector_router, prefix="/currency", tags=["currency-detector"])
api_router.include_router(currency_products_router, tags=["currency-products"])
api_router.include_router(comprehensive_search_router, tags=["comprehensive-search"])

__all__ = ["api_router"]