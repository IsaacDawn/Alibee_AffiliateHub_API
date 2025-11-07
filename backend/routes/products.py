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

def _safe_float(value):
    """Safely convert value to float, handling null/None/empty values as 0"""
    try:
        if value is None or value == '' or str(value).lower() in ['null', 'none']:
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def _calculate_discount_percentage(product):
    """Calculate discount percentage for a product"""
    try:
        original_price = product.get("originalPrice") or product.get("original_price")
        sale_price = product.get("price") or product.get("sale_price")
        
        if original_price and sale_price and original_price > 0 and sale_price < original_price:
            discount = ((original_price - sale_price) / original_price) * 100
            return round(discount, 2)
        return 0.0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0

def get_custom_titles_for_products(products: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Get custom titles and product categories for products from saved_products table"""
    try:
        if not products:
            return {}

        # Extract product IDs and convert to string (database stores as varchar(255))
        product_ids = [str(product.get("product_id")) for product in products if product.get("product_id")]

        if not product_ids:
            return {}

        # Debug: Log product IDs being searched
        print(f"🔍 [get_custom_titles - products.py] Searching for {len(product_ids)} products in database. First 5 IDs: {product_ids[:5]}")
        logging.info(f"Searching for {len(product_ids)} products in database")

        # Get custom titles and product categories from database
        saved_products_info = {}
        with db_ops.db.get_cursor() as (cursor, connection):
            placeholders = ','.join(['%s' for _ in product_ids])
            query = f"""
                SELECT product_id, custom_title, product_category
                FROM saved_products
                WHERE product_id IN ({placeholders})
            """
            cursor.execute(query, product_ids)
            rows = cursor.fetchall()

            print(f"🔍 [get_custom_titles - products.py] Found {len(rows)} products in database")

            for row in rows:
                # product_id in database is varchar(255), so convert to string
                product_id_db = str(row[0])

                custom_title = row[1] if row[1] else None
                # Get product_category from database, use 'other' if null or empty
                raw_category = row[2]
                product_category = 'other'
                if raw_category and str(raw_category).strip():
                    product_category = str(raw_category).strip()

                # Store with product_id as string (matching database varchar type)
                saved_products_info[product_id_db] = {
                    'custom_title': custom_title,
                    'product_category': product_category
                }

                # Log product_category from database to console
                print(f"📦 [DATABASE - products.py] Product ID: {product_id_db} | product_category: {product_category} | custom_title: {custom_title[:50] if custom_title else 'None'}...")
                logging.info(f"Database lookup: Product {product_id_db}: custom_title={custom_title}, product_category={product_category} (raw={raw_category})")

        # Log summary to console
        print(f"📊 [DATABASE SUMMARY - products.py] Found {len(saved_products_info)} products in database out of {len(product_ids)} searched products")
        if saved_products_info:
            print("📋 Products with product_category from database:")
            for pid, info in saved_products_info.items():
                print(f"   - Product {pid}: product_category = '{info.get('product_category', 'other')}'")
        else:
            print(f"⚠️ [get_custom_titles - products.py] No products found in database! Searched IDs: {product_ids[:10]}")

        logging.info(f"Retrieved {len(saved_products_info)} saved products info for {len(product_ids)} products")
        return saved_products_info

    except Exception as e:
        logging.error(f"Error getting custom titles: {e}")
        print(f"❌ [get_custom_titles - products.py] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {}

def add_custom_titles_to_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add custom titles and override product_category from database"""
    try:
        if not products:
            return products
        
        # Debug: Log function entry
        print(f"🔵 [add_custom_titles - products.py] ENTRY: Processing {len(products)} products")
        logging.info(f"add_custom_titles_to_products called with {len(products)} products")
        
        # Get custom titles and product categories for all products
        saved_products_info = get_custom_titles_for_products(products)
        logging.info(f"🔍 Found {len(saved_products_info)} products in database out of {len(products)} total products")
        print(f"🔍 [add_custom_titles - products.py] Found {len(saved_products_info)} products in database out of {len(products)} total products")
        if saved_products_info:
            print(f"🔍 [add_custom_titles - products.py] Products in database: {list(saved_products_info.keys())[:5]}")
        else:
            print(f"⚠️ [add_custom_titles - products.py] No products found in database! Check if products exist in saved_products table.")
        
        # Add custom_title and override product_category for each product
        for product in products:
            product_id = str(product.get("product_id", ""))
            product_id_int = int(product_id) if product_id.isdigit() else None
            
            # Debug: Log product ID and whether it's in saved_products_info
            if product_id:
                is_in_db = product_id in saved_products_info
                has_custom_title = product.get("custom_title") is not None and product.get("custom_title") != ""
                print(f"🔍 [add_custom_titles - products.py] Product ID: {product_id} | In DB: {is_in_db} | Has custom_title: {has_custom_title}")
            
            # Try to find product in saved_products_info using both string and integer keys
            saved_info = None
            if product_id and product_id in saved_products_info:
                saved_info = saved_products_info[product_id]
            elif product_id_int and str(product_id_int) in saved_products_info:
                saved_info = saved_products_info[str(product_id_int)]
            
            if saved_info:
                # Log original product_category from API before override
                original_api_category = product.get("product_category", "N/A")
                original_custom_title = product.get("custom_title", "N/A")
                print(f"🔄 [BEFORE OVERRIDE - products.py] Product ID: {product_id} | Original API product_category: {original_api_category} | Original custom_title: {original_custom_title[:50] if original_custom_title != 'N/A' else 'N/A'}...")
                
                # If product has custom_title in database, replace the title
                db_custom_title = saved_info.get("custom_title")
                if db_custom_title:
                    product["custom_title"] = db_custom_title
                    print(f"📝 [TITLE - products.py] Product {product_id}: Set custom_title from DB: {db_custom_title[:50]}...")
                else:
                    product["custom_title"] = None
                    print(f"📝 [TITLE - products.py] Product {product_id}: No custom_title in DB, set to None")
                
                # Override product_category with the one from database
                db_category = saved_info.get("product_category", "other")
                final_category = db_category if db_category else "other"
                product["product_category"] = final_category
                
                # Set a flag to indicate this product is in database (for frontend to use)
                product["is_saved_in_db"] = True
                
                # Log to console - show before and after
                print(f"✅ [APPLIED - products.py] Product ID: {product_id} | API category: {original_api_category} -> DB category: {final_category} | is_saved_in_db: {product.get('is_saved_in_db')} | custom_title from DB: {db_custom_title[:50] if db_custom_title else 'None'}...")
                logging.info(f"✅ Applied saved info to product {product_id}: custom_title={product.get('custom_title')}, product_category={original_api_category} -> {final_category}, is_saved_in_db={product.get('is_saved_in_db')}")
                
                # Verify the override worked
                if product.get("product_category") != final_category:
                    print(f"⚠️ [WARNING - products.py] Override failed! Product {product_id} still has product_category={product.get('product_category')} instead of {final_category}")
                    logging.warning(f"Override failed for product {product_id}: expected {final_category}, got {product.get('product_category')}")
                
                # Verify is_saved_in_db is set
                if not product.get("is_saved_in_db"):
                    print(f"⚠️ [WARNING - products.py] is_saved_in_db not set! Product {product_id} should have is_saved_in_db=True")
                    logging.warning(f"is_saved_in_db not set for product {product_id}")
            else:
                product["custom_title"] = None
                product["is_saved_in_db"] = False
                logging.debug(f"❌ Product {product_id} not found in database, is_saved_in_db set to False")
        
        # Debug: Log how many products have is_saved_in_db flag
        products_with_flag = [p for p in products if "is_saved_in_db" in p]
        products_with_flag_true = [p for p in products if p.get("is_saved_in_db") == True]
        products_with_custom_title = [p for p in products if p.get("custom_title")]
        print(f"🔍 [DEBUG - products.py] After add_custom_titles: {len(products_with_flag)} products have is_saved_in_db flag, {len(products_with_flag_true)} have is_saved_in_db=True, {len(products_with_custom_title)} have custom_title")
        logging.info(f"🔍 After add_custom_titles: {len(products_with_flag)} products have is_saved_in_db flag, {len(products_with_flag_true)} have is_saved_in_db=True, {len(products_with_custom_title)} have custom_title")
        
        print(f"🔵 [add_custom_titles - products.py] EXIT: Returning {len(products)} products")
        
        return products
        
    except Exception as e:
        logging.error(f"Error adding custom titles to products: {e}")
        print(f"❌ [add_custom_titles - products.py] ERROR: {e}")
        import traceback
        traceback.print_exc()
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
        "product_score_stars": 4.5,
            "product_score_stars": 4.5,
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
            "product_score_stars": 4.3,
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
            
            # Determine sort parameter for AliExpress API
            sort_param = "volume_desc"  # Default
            if sortBy == "price":
                sort_param = "price_asc" if sortOrder == "asc" else "price_desc"
            elif sortBy == "rating":
                sort_param = "rating_asc" if sortOrder == "asc" else "rating_desc"
            elif sortBy == "volume":
                sort_param = "volume_asc" if sortOrder == "asc" else "volume_desc"
            elif sortBy == "discount":
                sort_param = "discount_asc" if sortOrder == "asc" else "discount_desc"
            
            # Use AliExpress API with video filter if needed
            result = aliexpress_service.search_products_with_filters(
                query=query.strip(),
                page=page,
                page_size=limit,
                sort=sort_param,
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
        "product_score_stars": 4.5,
            "product_score_stars": 4.5,
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
            "product_score_stars": 4.3,
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
    
    # Apply sorting
    if sortBy == "price":
        if sortOrder == "asc":
            filtered_products.sort(key=lambda x: x.get("price", 0))
        else:  # desc
            filtered_products.sort(key=lambda x: x.get("price", 0), reverse=True)
    elif sortBy == "rating":
        if sortOrder == "asc":
            filtered_products.sort(key=lambda x: _safe_float(x.get("product_score_stars", 0)))
        else:  # desc
            filtered_products.sort(key=lambda x: _safe_float(x.get("product_score_stars", 0)), reverse=True)
    elif sortBy == "volume":
        if sortOrder == "asc":
            filtered_products.sort(key=lambda x: x.get("volume", 0))
        else:  # desc
            filtered_products.sort(key=lambda x: x.get("volume", 0), reverse=True)
    elif sortBy == "discount":
        if sortOrder == "asc":
            filtered_products.sort(key=lambda x: _calculate_discount_percentage(x))
        else:  # desc
            filtered_products.sort(key=lambda x: _calculate_discount_percentage(x), reverse=True)
    
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
        "product_score_stars": 4.5,
            "product_score_stars": 4.5,
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
            "product_score_stars": 4.3,
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
                
                # Debug: Log items before add_custom_titles_to_products
                if items and len(items) > 0:
                    first_item = items[0]
                    print(f"🔵 [BEFORE add_custom_titles] Product ID: {first_item.get('product_id')} | product_category: {first_item.get('product_category')} | custom_title: {first_item.get('custom_title')}")
                    logging.info(f"🔵 Before add_custom_titles: Product {first_item.get('product_id')}: product_category={first_item.get('product_category')}")
                
                # Add custom titles to products
                items = add_custom_titles_to_products(items)
                
                # Debug: Log items after add_custom_titles_to_products
                if items and len(items) > 0:
                    first_item = items[0]
                    print(f"🟢 [AFTER add_custom_titles] Product ID: {first_item.get('product_id')} | is_saved_in_db: {first_item.get('is_saved_in_db')} | product_category: {first_item.get('product_category')} | custom_title: {first_item.get('custom_title')}")
                    logging.info(f"🟢 After add_custom_titles: Product {first_item.get('product_id')}: is_saved_in_db={first_item.get('is_saved_in_db')}, product_category={first_item.get('product_category')}")
                
                # Debug: Log first product before returning
                if items and len(items) > 0:
                    first_prod = items[0]
                    print(f"📤 [GET_PRODUCT_BY_ID] Product ID: {first_prod.get('product_id')} | is_saved_in_db: {first_prod.get('is_saved_in_db')} | product_category: {first_prod.get('product_category')} | custom_title: {first_prod.get('custom_title')}")
                    logging.info(f"📤 [GET_PRODUCT_BY_ID] Product {first_prod.get('product_id')}: is_saved_in_db={first_prod.get('is_saved_in_db')}, product_category={first_prod.get('product_category')}")
                
                # Filter products with video if only_with_video=1
                if only_with_video == 1:
                    items = [product for product in items if product.get("video_link") and product.get("video_link").strip()]
                
                response_data = {
                    "success": True,
                    "product_id": product_id,
                    "items": items,
                    "total": result.get("total", 0),
                    "method": result.get("method", "aliexpress.affiliate.productdetail.get"),
                    "source": result.get("source", "aliexpress_api"),
                    "message": f"Found product {product_id} from AliExpress API"
                }
                
                # Debug: Log JSON response for first product
                if items and len(items) > 0:
                    import json
                    first_item_json = json.dumps(response_data["items"][0], indent=2, default=str)
                    print(f"📤 [JSON RESPONSE - GET_PRODUCT_BY_ID] First product in response:\n{first_item_json}")
                    # Also log full response for debugging
                    full_response_json = json.dumps(response_data, indent=2, default=str)
                    print(f"📤 [FULL JSON RESPONSE - GET_PRODUCT_BY_ID] Complete response (first 2000 chars):\n{full_response_json[:2000]}...")
                
                return response_data
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
        "product_score_stars": 4.5,
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

@router.post("/products/batch/custom-titles")
def get_batch_custom_titles(product_ids: List[str]):
    """Get custom titles for multiple products at once"""
    try:
        if not product_ids:
            return {"success": True, "custom_titles": {}}
        
        # Get custom titles from database
        custom_titles = {}
        cursor = db_ops.get_cursor()
        
        if cursor:
            try:
                # Create placeholders for the IN clause
                placeholders = ','.join(['%s'] * len(product_ids))
                query = f"SELECT product_id, custom_title FROM saved_products WHERE product_id IN ({placeholders})"
                
                cursor.execute(query, product_ids)
                results = cursor.fetchall()
                
                for row in results:
                    product_id, custom_title = row
                    if custom_title:  # Only include non-null custom titles
                        custom_titles[str(product_id)] = custom_title
                        
            except mysql.connector.Error as e:
                logging.error(f"Database error in get_batch_custom_titles: {e}")
            finally:
                db_ops.close_cursor(cursor)
        
        return {
            "success": True,
            "custom_titles": custom_titles,
            "total_requested": len(product_ids),
            "total_found": len(custom_titles)
        }
        
    except Exception as e:
        logging.error(f"Error in get_batch_custom_titles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get custom titles: {str(e)}")
