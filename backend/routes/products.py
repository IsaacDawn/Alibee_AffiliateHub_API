# backend/routes/products.py
from fastapi import APIRouter, Query
from typing import Optional
from services.aliexpress import AliExpressService

router = APIRouter()

@router.get("/products/search")
def search_products(
    query: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    minPrice: Optional[float] = Query(None, ge=0),
    maxPrice: Optional[float] = Query(None, ge=0),
    category: Optional[str] = Query(None),
    sortBy: Optional[str] = Query("price"),
    sortOrder: Optional[str] = Query("asc"),
    use_api: str = Query("true")
):
    """Search products endpoint - Uses AliExpress API when use_api=true, otherwise demo products"""
    
    # Use AliExpress API if use_api=true and query is provided
    if use_api.lower() == "true" and query.strip():
        try:
            aliexpress_service = AliExpressService()
            result = aliexpress_service.search_products_with_filters(
                query=query.strip(),
                page=page,
                page_size=limit,
                sort="volume_desc"
            )
            
            if result and result.get("items"):
                # Transform AliExpress data to match frontend format
                transformed_items = []
                for item in result.get("items", []):
                    transformed_item = {
                        "id": item.get("product_id", ""),
                        "title": item.get("product_title", ""),
                        "price": float(item.get("sale_price", 0)),
                        "originalPrice": float(item.get("original_price", 0)) if item.get("original_price") else None,
                        "currency": "USD",
                        "image": item.get("product_main_image_url", ""),
                        "rating": float(item.get("rating", 0)),
                        "reviewCount": int(item.get("review_count", 0)),
                        "url": item.get("product_detail_url", ""),
                        "category": item.get("category", ""),
                        "discount": None
                    }
                    # Calculate discount if original price exists
                    if transformed_item["originalPrice"] and transformed_item["originalPrice"] > transformed_item["price"]:
                        discount = ((transformed_item["originalPrice"] - transformed_item["price"]) / transformed_item["originalPrice"]) * 100
                        transformed_item["discount"] = round(discount)
                    transformed_items.append(transformed_item)
                
                return {
                    "success": True,
                    "data": transformed_items,
                    "page": page,
                    "limit": limit,
                    "hasMore": result.get("hasMore", False),
                    "total": len(transformed_items),
                    "message": f"Found {len(transformed_items)} products for '{query}'"
                }
            else:
                print(f"AliExpress API failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"AliExpress API error: {str(e)}")
    
    # Demo products for search (fallback or when use_api=false)
    demo_products = [
        {
            "id": "1005010032093800",
            "title": "Wireless Bluetooth Headphones - Premium Quality",
            "price": 29.99,
            "originalPrice": 49.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
            "rating": 4.5,
            "reviewCount": 1250,
            "url": "https://example.com/product/1005010032093800",
            "category": "Electronics",
            "discount": 40
        },
        {
            "id": "1005010032093801",
            "title": "Smart Watch with Fitness Tracking",
            "price": 89.99,
            "originalPrice": 129.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
            "rating": 4.3,
            "reviewCount": 890,
            "url": "https://example.com/product/1005010032093801",
            "category": "Watches",
            "discount": 31
        },
        {
            "id": "1005010032093802",
            "title": "Portable Phone Charger 20000mAh",
            "price": 19.99,
            "originalPrice": 29.99,
            "currency": "USD",
            "image": "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
            "rating": 4.7,
            "reviewCount": 2100,
            "url": "https://example.com/product/1005010032093802",
            "category": "Phone Accessories",
            "discount": 33
        }
    ]
    
    # Filter by query if provided
    if query.strip():
        filtered_products = [p for p in demo_products if query.lower() in p["title"].lower()]
    else:
        filtered_products = demo_products
    
    # Calculate pagination
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_products = filtered_products[start_index:end_index]
    
    return {
        "success": True,
        "data": paginated_products,
        "page": page,
        "limit": limit,
        "hasMore": end_index < len(filtered_products),
        "total": len(filtered_products),
        "message": f"Found {len(paginated_products)} products for '{query}'" if query.strip() else "Demo products loaded"
    }

@router.get("/products")
def list_products(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    use_api: str = Query("true")
):
    """List products endpoint - Uses AliExpress API when use_api=true, otherwise demo products"""
    
    # Use AliExpress API if use_api=true
    if use_api.lower() == "true":
        try:
            aliexpress_service = AliExpressService()
            result = aliexpress_service.search_products_with_filters(
                query=None,  # No specific query for homepage
                page=page,
                page_size=pageSize,
                hot=True,  # Get hot/popular products for homepage
                sort="volume_desc"
            )
            
            if result and result.get("items"):
                return {
                    "items": result.get("items", []),
                    "page": page,
                    "pageSize": pageSize,
                    "hasMore": result.get("hasMore", False),
                    "total": len(result.get("items", [])),
                    "message": f"Found {len(result.get('items', []))} hot products from AliExpress API"
                }
            else:
                # Fallback to demo products if API fails
                print(f"AliExpress API failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"AliExpress API error: {str(e)}")
            # Fallback to demo products if API fails
    
    # Demo products for initial load (fallback or when use_api=false)
    demo_products = [
        {
            "product_id": "1005010032093800",
            "title": "Wireless Bluetooth Headphones - Premium Quality",
            "price": 29.99,
            "original_price": 49.99,
            "rating": 4.5,
            "review_count": 1250,
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
            "product_main_image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
            "images_link": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=300&h=300&fit=crop"
            ],
            "product_small_image_urls": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=300&h=300&fit=crop"
            ],
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
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
            "product_main_image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
            "images_link": [
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=300&h=300&fit=crop"
            ],
            "product_small_image_urls": [
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=300&h=300&fit=crop"
            ],
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
            "image_url": "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
            "product_main_image_url": "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
            "images_link": [
                "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop"
            ],
            "product_small_image_urls": [
                "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop"
            ],
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
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "product_main_image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
            "images_link": [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop"
            ],
            "product_small_image_urls": [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=300&fit=crop"
            ],
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
        }
    ]
    
    # Calculate pagination
    start_index = (page - 1) * pageSize
    end_index = start_index + pageSize
    paginated_products = demo_products[start_index:end_index]
    
    return {
        "items": paginated_products,
        "page": page,
        "pageSize": pageSize,
        "hasMore": end_index < len(demo_products),
        "total": len(demo_products),
        "message": "Demo products loaded successfully"
    }

@router.get("/product/{product_id}")
def get_product_by_id(
    product_id: str,
    use_api: str = Query("true")
):
    """Get product details by product ID"""
    
    # Use AliExpress API if use_api=true
    if use_api.lower() == "true":
        try:
            aliexpress_service = AliExpressService()
            result = aliexpress_service.get_product_by_id(product_id)
            
            if result and result.get("success") and result.get("items"):
                return {
                    "success": True,
                    "product_id": product_id,
                    "items": result.get("items", []),
                    "total": result.get("total", 0),
                    "method": result.get("method", "aliexpress.affiliate.productdetail.get"),
                    "source": result.get("source", "aliexpress_api"),
                    "message": f"Found product {product_id} from AliExpress API"
                }
            else:
                # Return error response
                return {
                    "success": False,
                    "product_id": product_id,
                    "items": [],
                    "total": 0,
                    "error": result.get("error", "Product not found") if result else "API request failed",
                    "method": "aliexpress.affiliate.productdetail.get",
                    "source": "aliexpress_api"
                }
        except Exception as e:
            print(f"AliExpress API error: {str(e)}")
            return {
                "success": False,
                "product_id": product_id,
                "items": [],
                "total": 0,
                "error": f"API error: {str(e)}",
                "method": "aliexpress.affiliate.productdetail.get",
                "source": "aliexpress_api"
            }
    
    # Demo product for fallback (when use_api=false)
    demo_product = {
        "product_id": product_id,
        "product_title": f"Demo Product {product_id}",
        "sale_price": 29.99,
        "original_price": 49.99,
        "rating": 4.5,
        "review_count": 1250,
        "image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Demo+Product",
        "product_main_image_url": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Demo+Product",
        "images_link": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Demo+Product"],
        "product_small_image_urls": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Demo+Product"],
        "volume": 5000,
        "category": "Electronics",
        "is_saved": False
    }
    
    return {
        "success": True,
        "product_id": product_id,
        "items": [demo_product],
        "total": 1,
        "method": "demo_product",
        "source": "demo_data",
        "message": f"Demo product {product_id} loaded successfully"
    }