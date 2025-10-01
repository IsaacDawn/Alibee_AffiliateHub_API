# backend/routes/simple_search.py
from fastapi import APIRouter, Query
from typing import Optional
from services.aliexpress import AliExpressService

router = APIRouter()

@router.get("/search")
def search_products(
    q: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    sort: Optional[str] = Query("volume_desc"),
    minPrice: Optional[float] = Query(None),
    maxPrice: Optional[float] = Query(None),
    use_api: str = Query("true")
):
    """Search products endpoint - Uses AliExpress API when use_api=true, otherwise demo products"""
    
    # Use AliExpress API if use_api=true and query is provided
    if use_api.lower() == "true" and q and q.strip():
        try:
            aliexpress_service = AliExpressService()
            result = aliexpress_service.search_products_with_filters(
                query=q,
                page=page,
                page_size=pageSize,
                sort=sort,
                min_price=minPrice,
                max_price=maxPrice
            )
            
            if result and result.get("items"):
                return {
                    "items": result.get("items", []),
                    "page": page,
                    "pageSize": pageSize,
                    "hasMore": result.get("hasMore", False),
                    "total": result.get("total", 0),
                    "query": q,
                    "message": f"Found {len(result.get('items', []))} products from AliExpress API"
                }
            else:
                # Fallback to demo products if API fails
                print(f"AliExpress API failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"AliExpress API error: {str(e)}")
            # Fallback to demo products if API fails
    
    # Demo products for search (fallback or when use_api=false)
    demo_products = [
        {
            "product_id": "1005010032093800",
            "title": "Wireless Bluetooth Headphones - Premium Quality",
            "price": 29.99,
            "original_price": 49.99,
            "rating": 4.5,
            "review_count": 1250,
            "image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones",
            "product_main_image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones",
            "images_link": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones"],
            "volume": 5000,
            "category": "Electronics",
            "is_saved": False
        },
        {
            "product_id": "1005010032093801",
            "title": "Smart Watch with Fitness Tracking",
            "price": 89.99,
            "original_price": 129.99,
            "rating": 4.3,
            "review_count": 890,
            "image_url": "https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch",
            "product_main_image_url": "https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch",
            "images_link": ["https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch"],
            "volume": 3200,
            "category": "Watches",
            "is_saved": False
        },
        {
            "product_id": "1005010032093802",
            "title": "Portable Phone Charger 20000mAh",
            "price": 19.99,
            "original_price": 29.99,
            "rating": 4.7,
            "review_count": 2100,
            "image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank",
            "product_main_image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank",
            "images_link": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Power+Bank"],
            "volume": 7500,
            "category": "Phone Accessories",
            "is_saved": False
        },
        {
            "product_id": "1005010032093803",
            "title": "LED Desk Lamp with USB Charging Port",
            "price": 24.99,
            "original_price": 39.99,
            "rating": 4.4,
            "review_count": 680,
            "image_url": "https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp",
            "product_main_image_url": "https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp",
            "images_link": ["https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/7C3AED/FFFFFF?text=Desk+Lamp"],
            "volume": 1800,
            "category": "Home & Garden",
            "is_saved": False
        },
        {
            "product_id": "1005010032093804",
            "title": "Bluetooth Speaker Waterproof",
            "price": 34.99,
            "original_price": 59.99,
            "rating": 4.6,
            "review_count": 1450,
            "image_url": "https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker",
            "product_main_image_url": "https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker",
            "images_link": ["https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/EA580C/FFFFFF?text=Speaker"],
            "volume": 4200,
            "category": "Electronics",
            "is_saved": False
        },
        {
            "product_id": "1005010032093805",
            "title": "Wireless Mouse Ergonomic Design",
            "price": 15.99,
            "original_price": 25.99,
            "rating": 4.2,
            "review_count": 920,
            "image_url": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse",
            "product_main_image_url": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse",
            "images_link": ["https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Mouse"],
            "volume": 2800,
            "category": "Computer Accessories",
            "is_saved": False
        },
        {
            "product_id": "1005010032093806",
            "title": "Car Phone Mount Dashboard",
            "price": 12.99,
            "original_price": 19.99,
            "rating": 4.5,
            "review_count": 1650,
            "image_url": "https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount",
            "product_main_image_url": "https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount",
            "images_link": ["https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/16A34A/FFFFFF?text=Car+Mount"],
            "volume": 6200,
            "category": "Automotive",
            "is_saved": False
        },
        {
            "product_id": "1005010032093807",
            "title": "Kitchen Scale Digital Display",
            "price": 18.99,
            "original_price": 28.99,
            "rating": 4.3,
            "review_count": 750,
            "image_url": "https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale",
            "product_main_image_url": "https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale",
            "images_link": ["https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/9333EA/FFFFFF?text=Kitchen+Scale"],
            "volume": 2100,
            "category": "Home & Garden",
            "is_saved": False
        },
        {
            "product_id": "1005010032093808",
            "title": "Travel Backpack Waterproof",
            "price": 45.99,
            "original_price": 69.99,
            "rating": 4.4,
            "review_count": 1100,
            "image_url": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Backpack",
            "product_main_image_url": "https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Backpack",
            "images_link": ["https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Backpack"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/0891B2/FFFFFF?text=Backpack"],
            "volume": 3500,
            "category": "Travel",
            "is_saved": False
        },
        {
            "product_id": "1005010032093809",
            "title": "Running Shoes Lightweight",
            "price": 79.99,
            "original_price": 119.99,
            "rating": 4.6,
            "review_count": 2300,
            "image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Running+Shoes",
            "product_main_image_url": "https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Running+Shoes",
            "images_link": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Running+Shoes"],
            "product_small_image_urls": ["https://via.placeholder.com/300x300/DC2626/FFFFFF?text=Running+Shoes"],
            "volume": 4800,
            "category": "Sports",
            "is_saved": False
        }
    ]
    
    # Filter products based on search query
    filtered_products = demo_products
    if q and q.strip():
        query_lower = q.lower().strip()
        filtered_products = [
            product for product in demo_products
            if (query_lower in product["title"].lower() or 
                query_lower in product["category"].lower() or
                any(keyword in product["title"].lower() for keyword in query_lower.split()))
        ]
    
    # Apply price filters
    if minPrice is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= minPrice]
    if maxPrice is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= maxPrice]
    
    # Apply sorting
    if sort == "volume_desc":
        filtered_products.sort(key=lambda x: x["volume"], reverse=True)
    elif sort == "price_asc":
        filtered_products.sort(key=lambda x: x["price"])
    elif sort == "price_desc":
        filtered_products.sort(key=lambda x: x["price"], reverse=True)
    elif sort == "rating_desc":
        filtered_products.sort(key=lambda x: x["rating"], reverse=True)
    
    # Calculate pagination
    start_index = (page - 1) * pageSize
    end_index = start_index + pageSize
    paginated_products = filtered_products[start_index:end_index]
    
    return {
        "items": paginated_products,
        "page": page,
        "pageSize": pageSize,
        "hasMore": end_index < len(filtered_products),
        "total": len(filtered_products),
        "query": q,
        "message": f"Found {len(filtered_products)} products for '{q}'"
    }