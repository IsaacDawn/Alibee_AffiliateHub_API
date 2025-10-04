# backend/routes/likes.py
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
from pydantic import BaseModel
from database.mysql_operations import mysql_ops
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class LikeRequest(BaseModel):
    """Request model for like/unlike operations"""
    product_id: str
    product_title: str
    promotion_link: str
    product_category: str = None
    custom_title: str = None
    has_video: bool = False

class LikeResponse(BaseModel):
    """Response model for like operations"""
    success: bool
    message: str
    is_liked: bool
    product_id: str

@router.post("/like", response_model=LikeResponse)
async def like_product(request: LikeRequest):
    """Like/save a product"""
    try:
        product_data = {
            'product_id': request.product_id,
            'product_title': request.product_title,
            'promotion_link': request.promotion_link,
            'product_category': request.product_category,
            'custom_title': request.custom_title,
            'has_video': request.has_video
        }
        
        success = mysql_ops.like_product(product_data)
        
        if success:
            return LikeResponse(
                success=True,
                message="Product liked successfully",
                is_liked=True,
                product_id=request.product_id
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to like product")
            
    except Exception as e:
        logger.error(f"Error in like_product: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/like/{product_id}", response_model=LikeResponse)
async def unlike_product(product_id: str):
    """Unlike/remove a product"""
    try:
        success = mysql_ops.unlike_product(product_id)
        
        if success:
            return LikeResponse(
                success=True,
                message="Product unliked successfully",
                is_liked=False,
                product_id=product_id
            )
        else:
            # Product might not exist, but that's still a successful operation
            return LikeResponse(
                success=True,
                message="Product was not liked",
                is_liked=False,
                product_id=product_id
            )
            
    except Exception as e:
        logger.error(f"Error in unlike_product: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/like/{product_id}/status")
async def get_like_status(product_id: str):
    """Get like status for a specific product"""
    try:
        is_liked = mysql_ops.is_product_liked(product_id)
        
        return {
            "success": True,
            "product_id": product_id,
            "is_liked": is_liked,
            "message": f"Product {product_id} is {'liked' if is_liked else 'not liked'}"
        }
        
    except Exception as e:
        logger.error(f"Error in get_like_status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/likes/batch-status")
async def get_batch_like_status(product_ids: List[str]):
    """Get like status for multiple products"""
    try:
        liked_status = mysql_ops.get_liked_products(product_ids)
        
        return {
            "success": True,
            "liked_products": liked_status,
            "total_checked": len(product_ids)
        }
        
    except Exception as e:
        logger.error(f"Error in get_batch_like_status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/likes/count")
async def get_liked_products_count():
    """Get total count of liked products"""
    try:
        count = mysql_ops.get_saved_products_count()
        
        return {
            "success": True,
            "total_liked_products": count
        }
        
    except Exception as e:
        logger.error(f"Error in get_liked_products_count: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
