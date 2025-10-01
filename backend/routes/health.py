# backend/routes/health.py
from fastapi import APIRouter, HTTPException
from database.connection import db_ops
from config.settings import settings
import time

router = APIRouter()

@router.get("/health")
def health_check():
    """Health check endpoint with database connectivity check"""
    try:
        # Test database connection
        db_status = "healthy"
        db_message = "Database connection successful"
        
        try:
            # Test database connection by getting stats
            stats = db_ops.get_stats()
            db_status = "healthy"
            db_message = f"Database connected - {stats.get('savedProducts', 0)} saved products"
        except Exception as db_error:
            db_status = "unhealthy"
            db_message = f"Database connection failed: {str(db_error)}"
        
        # Check AliExpress API configuration
        aliexpress_status = "configured" if settings.is_aliexpress_configured() else "not_configured"
        
        overall_status = "healthy" if db_status == "healthy" else "unhealthy"
        
        return {
            "status": overall_status,
            "message": "API is running",
            "version": "2.0.0",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "database": {
                "status": db_status,
                "message": db_message
            },
            "aliexpress_api": {
                "status": aliexpress_status,
                "configured": settings.is_aliexpress_configured()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "version": "2.0.0",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        )