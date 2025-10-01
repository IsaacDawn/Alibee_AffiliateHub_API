# backend/routes/exchange.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/exchange")
def get_exchange_rates():
    """Get currency exchange rates"""
    return {
        "rates": {
            "USD": 1.0,
            "EUR": 0.85,
            "ILS": 3.7
        },
        "last_updated": "2024-01-01T00:00:00Z"
    }