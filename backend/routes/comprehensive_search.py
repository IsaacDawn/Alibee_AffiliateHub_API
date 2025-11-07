# backend/routes/comprehensive_search.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from services.aliexpress import AliExpressService
from services.online_currency_converter import OnlineCurrencyConverter
from database.connection import db_ops
import logging
import json

router = APIRouter()

def get_saved_product_info(product_id: str) -> Dict[str, Any]:
    """Get saved product info (custom_title and product_category) from database for a single product"""
    try:
        if not product_id:
            return {}
        
        with db_ops.db.get_cursor() as (cursor, connection):
            query = """
                SELECT product_id, custom_title, product_category 
                FROM saved_products 
                WHERE product_id = %s
            """
            cursor.execute(query, (str(product_id),))
            row = cursor.fetchone()
            
            if row:
                return {
                    'product_id': row[0],
                    'custom_title': row[1] if row[1] else None,
                    'product_category': row[2] if row[2] else 'other'
                }
        
        return {}
        
    except Exception as e:
        logging.error(f"Error getting saved product info for {product_id}: {e}")
        return {}

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
        print(f"🔍 [get_custom_titles] Searching for {len(product_ids)} products in database. First 5 IDs: {product_ids[:5]}")
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
            
            print(f"🔍 [get_custom_titles] Found {len(rows)} products in database")
            
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
                print(f"📦 [DATABASE] Product ID: {product_id_db} | product_category: {product_category} | custom_title: {custom_title[:50] if custom_title else 'None'}...")
                logging.info(f"Database lookup: Product {product_id_db}: custom_title={custom_title}, product_category={product_category} (raw={raw_category})")
        
        # Log summary to console
        print(f"📊 [DATABASE SUMMARY] Found {len(saved_products_info)} products in database out of {len(product_ids)} searched products")
        if saved_products_info:
            print("📋 Products with product_category from database:")
            for pid, info in saved_products_info.items():
                print(f"   - Product {pid}: product_category = '{info.get('product_category', 'other')}'")
        else:
            print(f"⚠️ [get_custom_titles] No products found in database! Searched IDs: {product_ids[:10]}")
        
        logging.info(f"Retrieved {len(saved_products_info)} saved products info for {len(product_ids)} products")
        return saved_products_info
        
    except Exception as e:
        logging.error(f"Error getting custom titles: {e}")
        return {}

def add_custom_titles_to_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add custom titles and product categories to products from database"""
    try:
        if not products:
            return products
        
        # Debug: Log function entry
        print(f"🔵 [add_custom_titles] ENTRY: Processing {len(products)} products")
        logging.info(f"add_custom_titles_to_products called with {len(products)} products")
        
        # Get custom titles and product categories for all products from database
        saved_products_info = get_custom_titles_for_products(products)
        logging.info(f"🔍 Found {len(saved_products_info)} products in database out of {len(products)} total products")
        print(f"🔍 [add_custom_titles] Found {len(saved_products_info)} products in database out of {len(products)} total products")
        if saved_products_info:
            print(f"🔍 [add_custom_titles] Products in database: {list(saved_products_info.keys())[:5]}")
        else:
            print(f"⚠️ [add_custom_titles] No products found in database! Check if products exist in saved_products table.")
        
        # For each product, check if it exists in database and apply saved info
        for product in products:
            # Convert product_id to string (database stores as varchar(255))
            product_id = str(product.get("product_id", ""))
            
            # Debug: Log product ID and whether it's in saved_products_info
            if product_id:
                is_in_db = product_id in saved_products_info
                has_custom_title = product.get("custom_title") is not None and product.get("custom_title") != ""
                
                print(f"🔍 [add_custom_titles] Product ID: {product_id} | In DB: {is_in_db} | Has custom_title: {has_custom_title} | Saved info keys: {list(saved_products_info.keys())[:5]}")
            
            # Find product in saved_products_info (product_id is already string)
            saved_info = saved_products_info.get(product_id) if product_id else None
            
            if saved_info:
                # Log original product_category from API before override
                original_api_category = product.get("product_category", "N/A")
                original_custom_title = product.get("custom_title", "N/A")
                print(f"🔄 [BEFORE OVERRIDE] Product ID: {product_id} | Original API product_category: {original_api_category} | Original custom_title: {original_custom_title[:50] if original_custom_title != 'N/A' else 'N/A'}...")
                
                # If product has custom_title in database, replace the title
                db_custom_title = saved_info.get("custom_title")
                if db_custom_title:
                    product["custom_title"] = db_custom_title
                    print(f"📝 [TITLE] Product {product_id}: Set custom_title from DB: {db_custom_title[:50]}...")
                else:
                    product["custom_title"] = None
                    print(f"📝 [TITLE] Product {product_id}: No custom_title in DB, set to None")
                
                # Always set product_category from database if product exists
                # Use the category from database, default to 'other' if null or empty
                # This will override the product_category from API with the one from database
                db_category = saved_info.get("product_category", "other")
                final_category = db_category if db_category else "other"
                
                # Override product_category with the one from database
                # This replaces whatever value came from AliExpress API
                product["product_category"] = final_category
                
                # Set a flag to indicate this product is in database (for frontend to use)
                product["is_saved_in_db"] = True
                
                # Log to console - show before and after
                print(f"✅ [APPLIED] Product ID: {product_id} | API category: {original_api_category} -> DB category: {final_category} | is_saved_in_db: {product.get('is_saved_in_db')} | custom_title from DB: {db_custom_title[:50] if db_custom_title else 'None'}...")
                logging.info(f"✅ Applied saved info to product {product_id}: custom_title={product.get('custom_title')}, product_category={original_api_category} -> {final_category}, is_saved_in_db={product.get('is_saved_in_db')}")
                
                # Verify the override worked
                if product.get("product_category") != final_category:
                    print(f"⚠️ [WARNING] Override failed! Product {product_id} still has product_category={product.get('product_category')} instead of {final_category}")
                    logging.warning(f"Override failed for product {product_id}: expected {final_category}, got {product.get('product_category')}")
                
                # Verify is_saved_in_db is set
                if not product.get("is_saved_in_db"):
                    print(f"⚠️ [WARNING] is_saved_in_db not set! Product {product_id} should have is_saved_in_db=True")
                    logging.warning(f"is_saved_in_db not set for product {product_id}")
            else:
                # Product not in database - explicitly set is_saved_in_db to False
                # If custom_title exists, it's from API, not from database
                # So we should clear it or keep it as is (depending on requirements)
                # For now, we keep custom_title from API if it exists, but set is_saved_in_db to False
                if not product.get("custom_title"):
                    product["custom_title"] = None
                product["is_saved_in_db"] = False
                # Don't set product_category if product not in database (keep original from API)
                if product.get("custom_title"):
                    print(f"⚠️ [add_custom_titles] Product {product_id} has custom_title but not in database - custom_title is from API, not DB")
                logging.debug(f"❌ Product {product_id} not found in database, is_saved_in_db set to False")
        
        # Debug: Log how many products have is_saved_in_db flag
        products_with_flag = [p for p in products if "is_saved_in_db" in p]
        products_with_flag_true = [p for p in products if p.get("is_saved_in_db") == True]
        products_with_custom_title = [p for p in products if p.get("custom_title")]
        print(f"🔍 [DEBUG] After add_custom_titles: {len(products_with_flag)} products have is_saved_in_db flag, {len(products_with_flag_true)} have is_saved_in_db=True, {len(products_with_custom_title)} have custom_title")
        logging.info(f"🔍 After add_custom_titles: {len(products_with_flag)} products have is_saved_in_db flag, {len(products_with_flag_true)} have is_saved_in_db=True, {len(products_with_custom_title)} have custom_title")
        
        # Debug: Check if any products have custom_title but not is_saved_in_db
        products_with_title_but_no_flag = [p for p in products if p.get("custom_title") and not p.get("is_saved_in_db")]
        if products_with_title_but_no_flag:
            print(f"⚠️ [WARNING] {len(products_with_title_but_no_flag)} products have custom_title but is_saved_in_db is not True. First product ID: {products_with_title_but_no_flag[0].get('product_id')}")
            logging.warning(f"{len(products_with_title_but_no_flag)} products have custom_title but is_saved_in_db is not True")
        
        print(f"🔵 [add_custom_titles] EXIT: Returning {len(products)} products")
        
        return products
        
    except Exception as e:
        logging.error(f"Error adding custom titles to products: {e}")
        print(f"❌ [add_custom_titles] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return products

def get_sort_price(product: Dict[str, Any]) -> float:
    """Get price for sorting (use sale_price_target if available, otherwise sale_price)"""
    if "sale_price_target" in product and product["sale_price_target"]:
        return float(product["sale_price_target"])
    elif "sale_price" in product and product["sale_price"]:
        return float(product["sale_price"])
    return 0.0

def get_discount_percentage(product: Dict[str, Any]) -> float:
    """Calculate discount percentage"""
    try:
        original_price = 0
        sale_price = 0
        
        # Use target prices if available, otherwise use original prices
        if "original_price_target" in product and product["original_price_target"]:
            original_price = float(product["original_price_target"])
        elif "original_price" in product and product["original_price"]:
            original_price = float(product["original_price"])
        
        if "sale_price_target" in product and product["sale_price_target"]:
            sale_price = float(product["sale_price_target"])
        elif "sale_price" in product and product["sale_price"]:
            sale_price = float(product["sale_price"])
        elif "price" in product and product["price"]:
            sale_price = float(product["price"])
        
        if original_price > 0 and sale_price > 0 and original_price > sale_price:
            return ((original_price - sale_price) / original_price) * 100
        return 0.0
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0

def get_volume(product: Dict[str, Any]) -> int:
    """Get volume for sorting"""
    volume_fields = ["latest_volume", "volume", "lastest_volume"]
    for field in volume_fields:
        if field in product and product[field]:
            try:
                if isinstance(product[field], str):
                    # Remove commas and convert to int
                    return int(product[field].replace(",", ""))
                return int(product[field])
            except (ValueError, TypeError):
                continue
    return 0

def get_product_score_stars(product: Dict[str, Any]) -> float:
    """Get product_score_stars for sorting - handles null/None values as 0"""
    try:
        score = product.get('product_score_stars')
        if score is not None and score != '' and str(score).lower() != 'null':
            return float(score)
        return 0.0
    except (ValueError, TypeError):
        return 0.0

@router.get("/search/comprehensive")
def comprehensive_search(
    # Basic search parameters
    q: str = Query("", description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    pageSize: int = Query(150, ge=1, le=200, description="Number of products per page"),
    
    # Currency conversion parameters
    target_currency: Optional[str] = Query("USD", description="Target currency for price conversion (USD, EUR, ILS)"),
    
    # Price filter parameters
    min_price: Optional[float] = Query(0, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(1000000, ge=0, description="Maximum price filter"),
    
    # Sorting parameters
    sort_by: Optional[str] = Query("volume_desc", description="Sort by: price_asc, price_desc, discount_desc, discount_asc, volume_desc, volume_asc, rating_desc, rating_asc"),
    
    # Video filter parameter
    only_with_video: int = Query(0, ge=0, le=1, description="Filter products with video only (1=yes, 0=no)"),
    
    # Category filter parameter
    category: Optional[str] = Query(None, description="Filter by category"),
    
    # API usage parameter
    use_api: str = Query("true", description="Use AliExpress API (true) or demo data (false)")
):
    """
    Comprehensive search endpoint with all available filters:
    
    - Basic search: q, page, pageSize
    - Currency conversion: target_currency
    - Price filtering: min_price, max_price
    - Sorting: sort_by (price_asc, price_desc, discount_desc, discount_asc, volume_desc, volume_asc, rating_desc, rating_asc)
    - Video filtering: only_with_video
    - Category filtering: category
    - API usage: use_api
    """
    
    # Use AliExpress API if use_api=true and query is provided
    if use_api.lower() == "true" and q and q.strip():
        try:
            aliexpress_service = AliExpressService()
            
            # Check if query is a product ID (only numbers)
            query_stripped = q.strip()
            # Check if query is a product ID (10-20 digits only)
            is_product_id = query_stripped.isdigit() and 10 <= len(query_stripped) <= 20
            
            if is_product_id:
                # Use get_product_by_id for product ID queries
                result = aliexpress_service.get_product_by_id(query_stripped)
                
                if result and result.get("success") and result.get("items"):
                    products = result.get("items", [])
                    
                    # Apply video filtering for product ID search
                    if only_with_video == 1:
                        products = [p for p in products if p.get("video_link") and p.get("video_link").strip()]
                    
                    # Apply currency conversion for product ID search
                    conversion_stats = {
                        "total_products": len(products),
                        "successful_conversions": 0,
                        "failed_conversions": 0,
                        "target_currency": target_currency,
                        "conversion_errors": []
                    }
                    
                    if target_currency:
                        try:
                            currency_converter = OnlineCurrencyConverter()
                            converted_products = []
                            
                            for product in products:
                                try:
                                    # Convert sale price
                                    if product.get("sale_price") and product.get("sale_price_currency"):
                                        converted_sale_price = currency_converter.convert_price(
                                            product["sale_price"],
                                            product["sale_price_currency"],
                                            target_currency.upper()
                                        )
                                        if converted_sale_price:
                                            product["sale_price_target"] = round(converted_sale_price, 2)
                                            product["sale_price_currency_target"] = target_currency.upper()
                                            conversion_stats["successful_conversions"] += 1
                                    
                                    # Convert original price
                                    if product.get("original_price") and product.get("original_price_currency"):
                                        converted_original_price = currency_converter.convert_price(
                                            product["original_price"],
                                            product["original_price_currency"],
                                            target_currency.upper()
                                        )
                                        if converted_original_price:
                                            product["original_price_target"] = round(converted_original_price, 2)
                                            product["original_price_currency_target"] = target_currency.upper()
                                            conversion_stats["successful_conversions"] += 1
                                    
                                    converted_products.append(product)
                                    
                                except Exception as e:
                                    conversion_stats["failed_conversions"] += 1
                                    conversion_stats["conversion_errors"].append(f"Error converting product {product.get('product_id')}: {str(e)}")
                                    converted_products.append(product)
                            
                            products = converted_products
                            
                        except Exception as e:
                            logging.error(f"Currency conversion error: {e}")
                            conversion_stats["conversion_errors"].append(f"Currency conversion service error: {str(e)}")
                    
                    # Add custom titles to products
                    products = add_custom_titles_to_products(products)
                    
                    # Debug: Log first product before returning
                    if products and len(products) > 0:
                        first_prod = products[0]
                        print(f"📤 [BEFORE RETURN] Product ID: {first_prod.get('product_id')} | is_saved_in_db: {first_prod.get('is_saved_in_db')} | product_category: {first_prod.get('product_category')} | custom_title: {first_prod.get('custom_title')}")
                        logging.info(f"📤 Before return - Product {first_prod.get('product_id')}: is_saved_in_db={first_prod.get('is_saved_in_db')}, product_category={first_prod.get('product_category')}")
                    
                    response_data = {
                        "success": True,
                        "page": page,
                        "pageSize": pageSize,
                        "hasMore": False,  # Single product, no pagination
                        "total": len(products),
                        "query": q,
                        "query_type": "product_id",
                        "filters": {
                            "target_currency": target_currency,
                            "min_price": min_price,
                            "max_price": max_price,
                            "sort_by": sort_by,
                            "only_with_video": only_with_video,
                            "category": category
                        },
                        "currency_conversion": conversion_stats,
                        "items": products,
                        "message": f"Found {len(products)} product(s) by ID {query_stripped}"
                    }
                    
                    # Final verification: Ensure all products have is_saved_in_db flag set (even if False)
                    for product in products:
                        if "is_saved_in_db" not in product:
                            product["is_saved_in_db"] = False
                            print(f"⚠️ [FINAL CHECK] Product {product.get('product_id')} missing is_saved_in_db flag, set to False")
                    
                    # Debug: Log JSON response for first product
                    if products and len(products) > 0:
                        first_item_json = json.dumps(response_data["items"][0], indent=2, default=str)
                        print(f"📤 [JSON RESPONSE] First product in response:\n{first_item_json}")
                        # Also log full response for debugging
                        full_response_json = json.dumps(response_data, indent=2, default=str)
                        print(f"📤 [FULL JSON RESPONSE] Complete response (first 2000 chars):\n{full_response_json[:2000]}...")
                        
                        # Final verification: Check if is_saved_in_db exists in JSON string
                        if 'is_saved_in_db' not in first_item_json:
                            print(f"⚠️ [FINAL CHECK] WARNING: is_saved_in_db not found in JSON string for first product!")
                        else:
                            print(f"✅ [FINAL CHECK] is_saved_in_db found in JSON string for first product")
                    
                    # Use JSONResponse to ensure proper serialization of boolean values
                    # Ensure response is fully ready before returning
                    return JSONResponse(content=response_data)
                else:
                    return {
                        "success": False,
                        "page": page,
                        "pageSize": pageSize,
                        "hasMore": False,
                        "total": 0,
                        "query": q,
                        "query_type": "product_id",
                        "filters": {
                            "target_currency": target_currency,
                            "min_price": min_price,
                            "max_price": max_price,
                            "sort_by": sort_by,
                            "only_with_video": only_with_video,
                            "category": category
                        },
                        "currency_conversion": {
                            "total_products": 0,
                            "successful_conversions": 0,
                            "failed_conversions": 0,
                            "target_currency": target_currency,
                            "conversion_errors": []
                        },
                        "items": [],
                        "error": result.get("error", "Product not found") if result else "API call failed",
                        "message": f"Product with ID {query_stripped} not found"
                    }
            else:
                # Use search_products_with_filters for text queries
                # Prepare search parameters for AliExpress API
                search_params = {
                    "query": query_stripped,
                    "page": page,
                    "page_size": pageSize
                    # Note: has_video filter removed - we'll filter after API call for accuracy
                }
            
            # Add sorting parameter
            if sort_by == "price_asc":
                search_params["sort"] = "price"
            elif sort_by == "price_desc":
                search_params["sort"] = "price_desc"
            elif sort_by == "discount_desc":
                search_params["sort"] = "discount_desc"
            elif sort_by == "discount_asc":
                search_params["sort"] = "discount_asc"
            elif sort_by == "volume_desc":
                search_params["sort"] = "volume_desc"
            elif sort_by == "volume_asc":
                search_params["sort"] = "volume_asc"
            elif sort_by == "rating_desc":
                search_params["sort"] = "rating_desc"
            elif sort_by == "rating_asc":
                search_params["sort"] = "rating_asc"
            else:
                search_params["sort"] = "volume_desc"  # Default
            
            # Call AliExpress API
            result = aliexpress_service.search_products_with_filters(**search_params)
            
            if result and result.get("items"):
                products = result.get("items", [])
                
                # Apply price filtering
                if min_price is not None or max_price is not None:
                    filtered_products = []
                    for product in products:
                        product_price = get_sort_price(product)
                        if min_price is not None and product_price < min_price:
                            continue
                        if max_price is not None and product_price > max_price:
                            continue
                        filtered_products.append(product)
                    products = filtered_products
                
                # Apply category filtering
                if category and category.strip():
                    products = [p for p in products if category.lower() in p.get("category", "").lower()]
                
                # Apply video filtering (after API call to ensure accuracy)
                if only_with_video == 1:
                    products = [p for p in products if p.get("video_link") and p.get("video_link").strip()]
                
                # Apply currency conversion
                conversion_stats = {
                    "total_products": len(products),
                    "successful_conversions": 0,
                    "failed_conversions": 0,
                    "target_currency": target_currency,
                    "conversion_errors": []
                }
                
                if target_currency:
                    try:
                        currency_converter = OnlineCurrencyConverter()
                        converted_products = []
                        
                        for product in products:
                            try:
                                # Convert sale price
                                if product.get("sale_price") and product.get("sale_price_currency"):
                                    converted_sale_price = currency_converter.convert_price(
                                        product["sale_price"],
                                        product["sale_price_currency"],
                                        target_currency.upper()
                                    )
                                    if converted_sale_price:
                                        product["sale_price_target"] = round(converted_sale_price, 2)
                                        product["sale_price_currency_target"] = target_currency.upper()
                                        conversion_stats["successful_conversions"] += 1
                                    else:
                                        conversion_stats["failed_conversions"] += 1
                                        conversion_stats["conversion_errors"].append(f"Failed to convert sale price for product {product.get('product_id')}")
                                
                                # Convert original price
                                if product.get("original_price") and product.get("original_price_currency"):
                                    converted_original_price = currency_converter.convert_price(
                                        product["original_price"],
                                        product["original_price_currency"],
                                        target_currency.upper()
                                    )
                                    if converted_original_price:
                                        product["original_price_target"] = round(converted_original_price, 2)
                                        product["original_price_currency_target"] = target_currency.upper()
                                        conversion_stats["successful_conversions"] += 1
                                    else:
                                        conversion_stats["failed_conversions"] += 1
                                        conversion_stats["conversion_errors"].append(f"Failed to convert original price for product {product.get('product_id')}")
                                
                                converted_products.append(product)
                                
                            except Exception as e:
                                conversion_stats["failed_conversions"] += 1
                                conversion_stats["conversion_errors"].append(f"Error converting product {product.get('product_id')}: {str(e)}")
                                converted_products.append(product)
                        
                        products = converted_products
                        
                    except Exception as e:
                        logging.error(f"Currency conversion error: {e}")
                        conversion_stats["conversion_errors"].append(f"Currency conversion service error: {str(e)}")
                
                # Apply sorting
                if sort_by == "price_asc":
                    products.sort(key=get_sort_price)
                elif sort_by == "price_desc":
                    products.sort(key=get_sort_price, reverse=True)
                elif sort_by == "discount_desc":
                    products.sort(key=get_discount_percentage, reverse=True)
                elif sort_by == "discount_asc":
                    products.sort(key=get_discount_percentage)
                elif sort_by == "volume_desc":
                    products.sort(key=get_volume, reverse=True)
                elif sort_by == "volume_asc":
                    products.sort(key=get_volume)
                elif sort_by == "rating_desc":
                    products.sort(key=get_product_score_stars, reverse=True)
                elif sort_by == "rating_asc":
                    products.sort(key=get_product_score_stars)
                
                # Add custom titles to products (this will override product_category from database)
                products = add_custom_titles_to_products(products)
                
                # Debug: Log first few products with product_category from database
                logging.info(f"📦 Total products after add_custom_titles: {len(products)}")
                for i, p in enumerate(products[:5]):
                    logging.info(f"📦 Product {p.get('product_id')}: product_category={p.get('product_category')}, custom_title={p.get('custom_title')}, is_saved_in_db={p.get('is_saved_in_db')}")
                    print(f"📦 [FINAL] Product {p.get('product_id')}: product_category={p.get('product_category')}, is_saved_in_db={p.get('is_saved_in_db')}")
                
                # Apply pagination
                start_index = (page - 1) * pageSize
                end_index = start_index + pageSize
                paginated_products = products[start_index:end_index]
                
                # Final verification: Check if any products in paginated results have is_saved_in_db=True
                # and verify their product_category is from database
                db_products_in_page = [p for p in paginated_products if p.get("is_saved_in_db") == True]
                if db_products_in_page:
                    print(f"📋 [FINAL CHECK] {len(db_products_in_page)} products in this page are from database:")
                    for p in db_products_in_page[:3]:
                        print(f"   - Product {p.get('product_id')}: product_category={p.get('product_category')}")
                
                # Debug: Log first product before returning
                if paginated_products and len(paginated_products) > 0:
                    first_prod = paginated_products[0]
                    print(f"📤 [BEFORE RETURN] Product ID: {first_prod.get('product_id')} | is_saved_in_db: {first_prod.get('is_saved_in_db')} | product_category: {first_prod.get('product_category')} | custom_title: {first_prod.get('custom_title')}")
                    logging.info(f"📤 Before return - Product {first_prod.get('product_id')}: is_saved_in_db={first_prod.get('is_saved_in_db')}, product_category={first_prod.get('product_category')}")
                
                response_data = {
                    "success": True,
                    "page": page,
                    "pageSize": pageSize,
                    "hasMore": end_index < len(products),
                    "total": len(products),
                    "query": q,
                    "query_type": "text_search",
                    "filters": {
                        "target_currency": target_currency,
                        "min_price": min_price,
                        "max_price": max_price,
                        "sort_by": sort_by,
                        "only_with_video": only_with_video,
                        "category": category
                    },
                    "currency_conversion": conversion_stats,
                    "items": paginated_products,
                    "message": f"Found {len(paginated_products)} products with comprehensive filters"
                }
                
                # Final verification: Ensure all products have is_saved_in_db flag set (even if False)
                for product in paginated_products:
                    if "is_saved_in_db" not in product:
                        product["is_saved_in_db"] = False
                        print(f"⚠️ [FINAL CHECK] Product {product.get('product_id')} missing is_saved_in_db flag, set to False")
                
                # Debug: Log JSON response for first product
                if paginated_products and len(paginated_products) > 0:
                    first_item_json = json.dumps(response_data["items"][0], indent=2, default=str)
                    print(f"📤 [JSON RESPONSE] First product in response:\n{first_item_json}")
                    # Also log full response for debugging
                    full_response_json = json.dumps(response_data, indent=2, default=str)
                    print(f"📤 [FULL JSON RESPONSE] Complete response (first 2000 chars):\n{full_response_json[:2000]}...")
                    
                    # Final verification: Check if is_saved_in_db exists in JSON string
                    if 'is_saved_in_db' not in first_item_json:
                        print(f"⚠️ [FINAL CHECK] WARNING: is_saved_in_db not found in JSON string for first product!")
                    else:
                        print(f"✅ [FINAL CHECK] is_saved_in_db found in JSON string for first product")
                
                # Use JSONResponse to ensure proper serialization of boolean values
                # Ensure response is fully ready before returning
                return JSONResponse(content=response_data)
            else:
                return {
                    "success": False,
                    "page": page,
                    "pageSize": pageSize,
                    "hasMore": False,
                    "total": 0,
                    "query": q,
                    "query_type": "text_search",
                    "filters": {
                        "target_currency": target_currency,
                        "min_price": min_price,
                        "max_price": max_price,
                        "sort_by": sort_by,
                        "only_with_video": only_with_video,
                        "category": category
                    },
                    "currency_conversion": {
                        "total_products": 0,
                        "successful_conversions": 0,
                        "failed_conversions": 0,
                        "target_currency": target_currency,
                        "conversion_errors": []
                    },
                    "items": [],
                    "error": result.get("error", "No products found") if result else "API call failed",
                    "message": f"No products found for query '{q}' with applied filters"
                }
                
        except Exception as e:
            logging.error(f"AliExpress API error: {e}")
            return {
                "success": False,
                "page": page,
                "pageSize": pageSize,
                "hasMore": False,
                "total": 0,
                "query": q,
                "query_type": "text_search" if not q.strip().isdigit() else "product_id",
                "filters": {
                    "target_currency": target_currency,
                    "min_price": min_price,
                    "max_price": max_price,
                    "sort_by": sort_by,
                    "only_with_video": only_with_video,
                    "category": category
                },
                "currency_conversion": {
                    "total_products": 0,
                    "successful_conversions": 0,
                    "failed_conversions": 0,
                    "target_currency": target_currency,
                    "conversion_errors": [f"API error: {str(e)}"]
                },
                "items": [],
                "error": f"API error: {str(e)}",
                "message": f"Search failed for query '{q}'"
            }
    
    # Demo products for fallback or when use_api=false
    demo_products = [
        {
            "product_id": "1005010032093800",
            "product_title": "Wireless Bluetooth Headphones - Premium Quality",
            "sale_price": 29.99,
            "sale_price_currency": "USD",
            "original_price": 49.99,
            "original_price_currency": "USD",
            "rating": 4.5,
            "review_count": 1250,
            "product_score_stars": 4.5,
            "product_main_image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop",
            "product_small_image_urls": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop"],
            "video_link": "https://example.com/video/headphones.mp4",
            "latest_volume": 5000,
            "category": "Electronics",
            "discount": 40
        },
        {
            "product_id": "1005010032093801",
            "product_title": "Smart Watch with Fitness Tracking",
            "sale_price": 89.99,
            "sale_price_currency": "USD",
            "original_price": 129.99,
            "original_price_currency": "USD",
            "rating": 4.3,
            "review_count": 890,
            "product_score_stars": 4.3,
            "product_main_image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop",
            "product_small_image_urls": ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop"],
            "video_link": "",  # No video for this product
            "latest_volume": 3200,
            "category": "Watches",
            "discount": 31
        },
        {
            "product_id": "1005010032093802",
            "product_title": "Portable Phone Charger 20000mAh",
            "sale_price": 19.99,
            "sale_price_currency": "USD",
            "original_price": 29.99,
            "original_price_currency": "USD",
            "rating": 4.7,
            "review_count": 2100,
            "product_score_stars": 4.7,
            "product_main_image_url": "https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop",
            "product_small_image_urls": ["https://images.unsplash.com/photo-1609592807909-0a1b0a4a0b0b?w=300&h=300&fit=crop"],
            "video_link": "https://example.com/video/charger.mp4",
            "latest_volume": 7500,
            "category": "Phone Accessories",
            "discount": 33
        }
    ]
    
    # Apply search filter
    if q and q.strip():
        demo_products = [p for p in demo_products if q.lower() in p["product_title"].lower()]
    
    # Apply video filter
    if only_with_video == 1:
        demo_products = [p for p in demo_products if p.get("video_link") and p.get("video_link").strip()]
    
    # Apply category filter
    if category and category.strip():
        demo_products = [p for p in demo_products if category.lower() in p.get("category", "").lower()]
    
    # Apply price filter
    if min_price is not None or max_price is not None:
        filtered_products = []
        for product in demo_products:
            product_price = get_sort_price(product)
            if min_price is not None and product_price < min_price:
                continue
            if max_price is not None and product_price > max_price:
                continue
            filtered_products.append(product)
        demo_products = filtered_products
    
    # Apply currency conversion to demo products
    conversion_stats = {
        "total_products": len(demo_products),
        "successful_conversions": 0,
        "failed_conversions": 0,
        "target_currency": target_currency,
        "conversion_errors": []
    }
    
    if target_currency:
        try:
            currency_converter = OnlineCurrencyConverter()
            for product in demo_products:
                try:
                    # Convert sale price
                    if product.get("sale_price") and product.get("sale_price_currency"):
                        converted_sale_price = currency_converter.convert_price(
                            product["sale_price"],
                            product["sale_price_currency"],
                            target_currency.upper()
                        )
                        if converted_sale_price:
                            product["sale_price_target"] = round(converted_sale_price, 2)
                            product["sale_price_currency_target"] = target_currency.upper()
                            conversion_stats["successful_conversions"] += 1
                    
                    # Convert original price
                    if product.get("original_price") and product.get("original_price_currency"):
                        converted_original_price = currency_converter.convert_price(
                            product["original_price"],
                            product["original_price_currency"],
                            target_currency.upper()
                        )
                        if converted_original_price:
                            product["original_price_target"] = round(converted_original_price, 2)
                            product["original_price_currency_target"] = target_currency.upper()
                            conversion_stats["successful_conversions"] += 1
                            
                except Exception as e:
                    conversion_stats["failed_conversions"] += 1
                    conversion_stats["conversion_errors"].append(f"Error converting product {product.get('product_id')}: {str(e)}")
        except Exception as e:
            logging.error(f"Currency conversion error: {e}")
            conversion_stats["conversion_errors"].append(f"Currency conversion service error: {str(e)}")
    
    # Apply sorting
    if sort_by == "price_asc":
        demo_products.sort(key=get_sort_price)
    elif sort_by == "price_desc":
        demo_products.sort(key=get_sort_price, reverse=True)
    elif sort_by == "discount_desc":
        demo_products.sort(key=get_discount_percentage, reverse=True)
    elif sort_by == "discount_asc":
        demo_products.sort(key=get_discount_percentage)
    elif sort_by == "volume_desc":
        demo_products.sort(key=get_volume, reverse=True)
    elif sort_by == "volume_asc":
        demo_products.sort(key=get_volume)
    elif sort_by == "rating_desc":
        demo_products.sort(key=get_product_score_stars, reverse=True)
    elif sort_by == "rating_asc":
        demo_products.sort(key=get_product_score_stars)
    
    # Add custom titles to demo products
    demo_products = add_custom_titles_to_products(demo_products)
    
    # Apply pagination
    start_index = (page - 1) * pageSize
    end_index = start_index + pageSize
    paginated_products = demo_products[start_index:end_index]
    
    return {
        "success": True,
        "page": page,
        "pageSize": pageSize,
        "hasMore": end_index < len(demo_products),
        "total": len(demo_products),
        "query": q,
        "query_type": "text_search" if not q.strip().isdigit() else "product_id",
        "filters": {
            "target_currency": target_currency,
            "min_price": min_price,
            "max_price": max_price,
            "sort_by": sort_by,
            "only_with_video": only_with_video,
            "category": category
        },
        "currency_conversion": conversion_stats,
        "items": paginated_products,
        "message": f"Found {len(paginated_products)} demo products with comprehensive filters"
    }
