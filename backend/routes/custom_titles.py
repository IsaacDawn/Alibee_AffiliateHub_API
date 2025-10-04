# backend/routes/custom_titles.py
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel
from database.mysql_operations import mysql_ops
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CustomTitleRequest(BaseModel):
    """Request model for custom title operations"""
    product_id: str
    custom_title: str

class CustomTitleResponse(BaseModel):
    """Response model for custom title operations"""
    success: bool
    message: str
    product_id: str
    custom_title: Optional[str] = None

@router.get("/products/{product_id}/custom-title")
async def get_custom_title(product_id: str):
    """Get custom title for a specific product"""
    try:
        # Check if product exists in saved_products table
        is_liked = mysql_ops.is_product_liked(product_id)
        
        if not is_liked:
            return {
                "success": False,
                "message": "Product not found in saved_products table",
                "product_id": product_id,
                "custom_title": None
            }
        
        # Get custom title from database
        with mysql_ops.get_cursor() as (cursor, connection):
            cursor.execute(
                "SELECT custom_title FROM saved_products WHERE product_id = %s", 
                (product_id,)
            )
            result = cursor.fetchone()
            
            if result:
                custom_title = result[0] if result[0] else None
                return {
                    "success": True,
                    "message": f"Custom title found for product {product_id}",
                    "product_id": product_id,
                    "custom_title": custom_title
                }
            else:
                return {
                    "success": False,
                    "message": "Product not found",
                    "product_id": product_id,
                    "custom_title": None
                }
                
    except Exception as e:
        logger.error(f"Error in get_custom_title: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/products/{product_id}/custom-title")
async def update_custom_title(
    product_id: str, 
    custom_title: str = Query(..., description="Custom title for the product")
):
    """Update custom title for a specific product"""
    try:
        # Check if product exists in saved_products table
        is_liked = mysql_ops.is_product_liked(product_id)
        
        if not is_liked:
            return {
                "success": False,
                "message": "Product not found in saved_products table. Please save the product first.",
                "product_id": product_id,
                "custom_title": None
            }
        
        # Update custom title in database
        with mysql_ops.get_cursor() as (cursor, connection):
            cursor.execute(
                "UPDATE saved_products SET custom_title = %s, updated_at = CURRENT_TIMESTAMP WHERE product_id = %s",
                (custom_title, product_id)
            )
            connection.commit()
            
            if cursor.rowcount > 0:
                return {
                    "success": True,
                    "message": f"Custom title updated successfully for product {product_id}",
                    "product_id": product_id,
                    "custom_title": custom_title
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to update custom title",
                    "product_id": product_id,
                    "custom_title": None
                }
                
    except Exception as e:
        logger.error(f"Error in update_custom_title: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/products/{product_id}/custom-title")
async def delete_custom_title(product_id: str):
    """Delete custom title for a specific product (reset to original title)"""
    try:
        # Check if product exists in saved_products table
        is_liked = mysql_ops.is_product_liked(product_id)
        
        if not is_liked:
            return {
                "success": False,
                "message": "Product not found in saved_products table",
                "product_id": product_id,
                "custom_title": None
            }
        
        # Clear custom title in database
        with mysql_ops.get_cursor() as (cursor, connection):
            cursor.execute(
                "UPDATE saved_products SET custom_title = NULL, updated_at = CURRENT_TIMESTAMP WHERE product_id = %s",
                (product_id,)
            )
            connection.commit()
            
            if cursor.rowcount > 0:
                return {
                    "success": True,
                    "message": "Custom title deleted successfully",
                    "product_id": product_id,
                    "custom_title": None
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to delete custom title",
                    "product_id": product_id,
                    "custom_title": None
                }
                
    except Exception as e:
        logger.error(f"Error in delete_custom_title: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/products/custom-titles/batch")
async def get_batch_custom_titles(product_ids: str = Query(..., description="Comma-separated product IDs")):
    """Get custom titles for multiple products"""
    try:
        product_id_list = [pid.strip() for pid in product_ids.split(',') if pid.strip()]
        
        if not product_id_list:
            return {
                "success": False,
                "message": "No product IDs provided",
                "custom_titles": {}
            }
        
        # Get custom titles from database
        with mysql_ops.get_cursor() as (cursor, connection):
            placeholders = ','.join(['%s'] * len(product_id_list))
            query = f"""
                SELECT product_id, custom_title 
                FROM saved_products 
                WHERE product_id IN ({placeholders}) AND custom_title IS NOT NULL AND custom_title != ''
            """
            cursor.execute(query, product_id_list)
            rows = cursor.fetchall()
            
            custom_titles = {row[0]: row[1] for row in rows}
            
            return {
                "success": True,
                "message": f"Retrieved custom titles for {len(custom_titles)} products",
                "custom_titles": custom_titles,
                "total_requested": len(product_id_list),
                "total_found": len(custom_titles)
            }
                
    except Exception as e:
        logger.error(f"Error in get_batch_custom_titles: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
