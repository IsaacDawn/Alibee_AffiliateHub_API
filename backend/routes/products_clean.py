# backend/routes/products.py
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from services.aliexpress import AliExpressService
from services.currency_converter import currency_converter
from database.connection import db_ops
import mysql.connector
from config.settings import settings
import logging

router = APIRouter()

def get_custom_titles_for_products(products: List[Dict[str, Any]]) -> Dict[str, str]:
    """Get custom titles for products from saved_products table"""
    try:
        if not products:
            return {}
        
        # Extract product IDs and convert to string
        product_ids = [str(product.get("product_id")) for product in products if product.get("product_id")]
        
        if not product_ids:
            return {}
        
        # Get custom titles from database
        custom_titles = {}
        with db_ops.db.get_cursor() as (cursor, connection):
            placeholders = ','.join(['%s' for _ in product_ids])
            query = f"""
                SELECT product_id, custom_title 
                FROM saved_products 
                WHERE product_id IN ({placeholders}) AND custom_title IS NOT NULL AND custom_title != ''
            """
            cursor.execute(query, product_ids)
            rows = cursor.fetchall()
            
            for row in rows:
                custom_titles[row[0]] = row[1]
        
        logging.info(f"Retrieved {len(custom_titles)} custom titles for {len(product_ids)} products")
        return custom_titles
        
    except Exception as e:
        logging.error(f"Error getting custom titles: {e}")
        return {}

def add_custom_titles_to_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add custom titles to products"""
    try:
        if not products:
            return products
        
        # Get custom titles for all products
        custom_titles = get_custom_titles_for_products(products)
        
        # Add custom_title to each product
        for product in products:
            product_id = product.get("product_id")
            if product_id and str(product_id) in custom_titles:
                product["custom_title"] = custom_titles[str(product_id)]
            else:
                product["custom_title"] = None
        
        return products
        
    except Exception as e:
        logging.error(f"Error adding custom titles to products: {e}")
        return products

@router.get("/products/initial")
def get_initial_products(
    limit: int = Query(150, ge=1, le=200),
    use_api: str = Query("true"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """Get initial random products for homepage - Returns 10 products by default"""
    
    # Use AliExpress API if use_api=true
    if use_api.lower() == "true":
        try:
            aliexpress_service = AliExpressService()
            # Get popular/trending products for initial load
            result = aliexpress_service.search_products_with_filters(
                query="electronics",  # Popular category for initial load
                page=1,
                page_size=limit,
                sort="volume_desc",
                has_video=(only_with_video == 1)
            )
            
            if result and result.get("items"):
                # Transform AliExpress data to match frontend format
                transformed_items = []
                for item in result.get("items", []):
                    # Extract additional images from AliExpress response
                    additional_images = []
                    if item.get("product_small_image_urls"):
                        if isinstance(item.get("product_small_image_urls"), list):
                            additional_images = item.get("product_small_image_urls", [])
                        elif isinstance(item.get("product_small_image_urls"), dict) and "string" in item.get("product_small_image_urls", {}):
                            additional_images = item.get("product_small_image_urls", {}).get("string", [])
                    elif item.get("images_link"):
                        if isinstance(item.get("images_link"), list):
                            additional_images = item.get("images_link", [])
                        elif isinstance(item.get("images_link"), dict) and "string" in item.get("images_link", {}):
                            additional_images = item.get("images_link", {}).get("string", [])
                    
                    # Extract video link if available
                    video_link = item.get("video_link", "")
                    
                    transformed_item = {
                        "id": item.get("product_id", ""),
                        "title": item.get("product_title", ""),
                        "price": float(item.get("sale_price", 0)),
                        "originalPrice": float(item.get("original_price", 0)) if item.get("original_price") else None,
                        "currency": "USD",
                        "originalPriceCurrency": item.get("original_price_currency", "USD"),
                        "image": item.get("product_main_image_url", ""),
                        "images": additional_images,
                        "video": video_link if video_link else None,
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
                
                # Add custom titles to products
                transformed_items = add_custom_titles_to_products(transformed_items)
                
                return {
                    "success": True,
                    "data": transformed_items,
                    "page": 1,
                    "limit": limit,
                    "hasMore": result.get("hasMore", False),
                    "total": len(transformed_items),
                    "message": f"Found {len(transformed_items)} initial products"
                }
            else:
                print(f"AliExpress API failed for initial load: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"AliExpress API error for initial load: {str(e)}")
    
    # Demo products for initial load (fallback or when use_api=false)
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
            "discount": 40,
            "video": "https://example.com/video/headphones.mp4"
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
            "discount": 31,
            "video": ""  # No video for this product
        }
    ]
    
    # Return limited number of products
    limited_products = demo_products[:limit]
    
    # Add custom titles to demo products
    limited_products = add_custom_titles_to_products(limited_products)
    
    # Filter products with video if only_with_video=1
    if only_with_video == 1:
        limited_products = [product for product in limited_products if product.get("video") and product.get("video").strip()]
    
    return {
        "success": True,
        "data": limited_products,
        "page": 1,
        "limit": limit,
        "hasMore": True,  # Always true for demo
        "total": len(limited_products),
        "message": f"Loaded {len(limited_products)} initial products"
    }

@router.get("/products/search")
def search_products(
    query: str = Query("", description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(150, ge=1, le=200),  # Changed default to 150 for better performance
    minPrice: Optional[float] = Query(None, ge=0),
    maxPrice: Optional[float] = Query(None, ge=0),
    category: Optional[str] = Query(None),
    sortBy: Optional[str] = Query("price"),
    sortOrder: Optional[str] = Query("asc"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)"),
    target_currency: Optional[str] = Query(None, description="Target currency for price conversion"),
    use_api: str = Query("true")
):
    """Search products endpoint - Uses AliExpress API when use_api=true, otherwise demo products"""
    
    # Use AliExpress API if use_api=true and query is provided
    if use_api.lower() == "true" and query.strip():
        try:
            aliexpress_service = AliExpressService()
            
            # Use AliExpress API with video filter if needed
            result = aliexpress_service.search_products_with_filters(
                query=query.strip(),
                page=page,
                page_size=limit,
                sort="volume_desc",
                has_video=(only_with_video == 1)
            )
            
            if result and result.get("items"):
                # Transform AliExpress data to match frontend format
                transformed_items = []
                for item in result.get("items", []):
                    # Extract additional images from AliExpress response
                    additional_images = []
                    if item.get("product_small_image_urls"):
                        if isinstance(item.get("product_small_image_urls"), list):
                            additional_images = item.get("product_small_image_urls", [])
                        elif isinstance(item.get("product_small_image_urls"), dict) and "string" in item.get("product_small_image_urls", {}):
                            additional_images = item.get("product_small_image_urls", {}).get("string", [])
                    elif item.get("images_link"):
                        if isinstance(item.get("images_link"), list):
                            additional_images = item.get("images_link", [])
                        elif isinstance(item.get("images_link"), dict) and "string" in item.get("images_link", {}):
                            additional_images = item.get("images_link", {}).get("string", [])
                    
                    # Extract video link if available
                    video_link = item.get("video_link", "")
                    
                    transformed_item = {
                        "id": item.get("product_id", ""),
                        "title": item.get("product_title", ""),
                        "price": float(item.get("sale_price", 0)),
                        "originalPrice": float(item.get("original_price", 0)) if item.get("original_price") else None,
                        "currency": "USD",
                        "originalPriceCurrency": item.get("original_price_currency", "USD"),
                        "image": item.get("product_main_image_url", ""),
                        "images": additional_images,
                        "video": video_link,
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
                
                # Add custom titles to products
                transformed_items = add_custom_titles_to_products(transformed_items)
                
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
            "originalPriceCurrency": "USD",
            "rating": 4.5,
            "reviewCount": 1250,
            "image": "https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones",
            "images": ["https://via.placeholder.com/300x300/4F46E5/FFFFFF?text=Headphones"],
            "video": "https://example.com/video/headphones.mp4",
            "url": "https://example.com/product/1005010032093800",
            "category": "Electronics",
            "discount": 40,
            "is_saved": False
        },
        {
            "id": "1005010032093801",
            "title": "Smart Watch with Fitness Tracking",
            "price": 89.99,
            "originalPrice": 129.99,
            "currency": "USD",
            "originalPriceCurrency": "USD",
            "rating": 4.3,
            "reviewCount": 890,
            "image": "https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch",
            "images": ["https://via.placeholder.com/300x300/059669/FFFFFF?text=Smart+Watch"],
            "video": "",  # No video for this product
            "url": "https://example.com/product/1005010032093801",
            "category": "Watches",
            "discount": 31,
            "is_saved": False
        }
    ]
    
    # Filter by video if specified
    if only_with_video == 1:
        demo_products = [p for p in demo_products if p.get("video") and p.get("video").strip()]
    
    # Apply search filter
    if query.strip():
        filtered_products = [p for p in demo_products if query.lower() in p["title"].lower()]
    else:
        filtered_products = demo_products
    
    # Apply pagination
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_products = filtered_products[start_index:end_index]
    
    # Add custom titles to demo products
    paginated_products = add_custom_titles_to_products(paginated_products)
    
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
    pageSize: int = Query(150, ge=1, le=200),
    use_api: str = Query("true"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """List products endpoint - Uses AliExpress API when use_api=true, otherwise demo products"""
    
    # Demo products for list (fallback or when use_api=false)
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
                "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=300&h=300&fit=crop"
            ],
            "product_small_image_urls": [
                "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
                "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=300&h=300&fit=crop"
            ],
            "video_link": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
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
            "video_link": "",  # No video for this product
            "volume": 3200,
            "category": "Watches",
            "is_saved": False
        }
    ]
    
    # Filter by video if specified
    if only_with_video == 1:
        demo_products = [p for p in demo_products if p.get("video_link") and p.get("video_link").strip()]
    
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
    use_api: str = Query("true"),
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)")
):
    """Get product details by product ID"""
    
    # Use AliExpress API if use_api=true
    if use_api.lower() == "true":
        try:
            aliexpress_service = AliExpressService()
            result = aliexpress_service.get_product_by_id(product_id)
            
            if result and result.get("success") and result.get("items"):
                items = result.get("items", [])
                # Add custom titles to products
                items = add_custom_titles_to_products(items)
                
                # Filter products with video if only_with_video=1
                if only_with_video == 1:
                    items = [product for product in items if product.get("video_link") and product.get("video_link").strip()]
                
                return {
                    "success": True,
                    "product_id": product_id,
                    "items": items,
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
                    "error": result.get("error", "Product not found") if result else "API call failed",
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
        "video_link": "https://example.com/video/demo.mp4",
        "volume": 5000,
        "category": "Electronics",
        "is_saved": False
    }
    
    # Add custom titles to demo product
    demo_items = add_custom_titles_to_products([demo_product])
    
    # Filter products with video if only_with_video=1
    if only_with_video == 1:
        demo_items = [product for product in demo_items if product.get("video_link") and product.get("video_link").strip()]
    
    return {
        "success": True,
        "product_id": product_id,
        "items": demo_items,
        "total": 1,
        "method": "demo_product",
        "source": "demo_data",
        "message": f"Demo product {product_id} loaded successfully"
    }
