# backend/routes/stats.py
from fastapi import APIRouter, HTTPException
from database.connection import db_ops
import time

router = APIRouter()

@router.get("/stats")
def get_stats():
    """Get application statistics from database"""
    try:
        # Get database statistics
        db_stats = db_ops.get_stats()
        
        # Calculate additional metrics
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "success": True,
            "data": {
                "totalProducts": db_stats.get('totalProducts', 1000),  # Demo value
                "totalCategories": 15,  # Demo value
                "lastUpdate": current_time
            },
            "timestamp": current_time,
            "savedProducts": db_stats.get('savedProducts', 0),
            "totalSearches": 0,  # This could be tracked in a separate table
            "activeUsers": 1,    # Single user system
            "affiliate_links": db_stats.get('savedProducts', 0),  # Each saved product has an affiliate link
            "recent_searches": 0,  # This could be tracked in a separate table
            "status": "active",
            "database_status": "connected"
        }
        
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": f"Failed to get statistics: {str(e)}",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "error"
            }
        )