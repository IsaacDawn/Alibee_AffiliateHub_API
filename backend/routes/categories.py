# backend/routes/categories.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/categories")
def list_categories():
    """List categories endpoint"""
    categories = [
        {"id": "", "name": "All Categories"},
        {"id": "100001", "name": "Electronics"},
        {"id": "100002", "name": "Watches & Jewelry"},
        {"id": "100003", "name": "Phone Accessories"},
        {"id": "100004", "name": "Home & Garden"},
        {"id": "100005", "name": "Beauty & Health"},
        {"id": "100006", "name": "Sports & Outdoors"},
        {"id": "100007", "name": "Automotive"},
        {"id": "100008", "name": "Toys & Games"},
        {"id": "100009", "name": "Fashion"},
        {"id": "100010", "name": "Tools & Hardware"},
    ]
    return {"categories": categories}