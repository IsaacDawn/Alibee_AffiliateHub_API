from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.schemas import CurrencyRate, CurrencyRateUpdate, CurrencyRateResponse
from database.connection import db_ops
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/rates", response_model=List[CurrencyRateResponse])
async def get_all_currency_rates():
    """Get all currency exchange rates"""
    try:
        rates = db_ops.get_all_currency_rates()
        return [
            CurrencyRateResponse(
                from_currency=rate['from_currency'],
                to_currency=rate['to_currency'],
                rate=rate['rate'],
                updated_at=rate['updated_at']
            )
            for rate in rates
        ]
    except Exception as e:
        logger.error(f"Error getting currency rates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get currency rates")

@router.get("/rates/{from_currency}/{to_currency}")
async def get_currency_rate(from_currency: str, to_currency: str):
    """Get exchange rate between two specific currencies"""
    try:
        rate = db_ops.get_currency_rate(from_currency.upper(), to_currency.upper())
        if rate is None:
            raise HTTPException(status_code=404, detail="Currency rate not found")
        
        return {
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "rate": rate
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting currency rate: {e}")
        raise HTTPException(status_code=500, detail="Failed to get currency rate")

@router.post("/rates", response_model=CurrencyRateResponse)
async def set_currency_rate(rate_data: CurrencyRateUpdate):
    """Set or update a currency exchange rate"""
    try:
        success = db_ops.set_currency_rate(
            rate_data.from_currency.upper(),
            rate_data.to_currency.upper(),
            rate_data.rate
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set currency rate")
        
        # Get the updated rate to return
        updated_rate = db_ops.get_currency_rate(
            rate_data.from_currency.upper(),
            rate_data.to_currency.upper()
        )
        
        if updated_rate is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated rate")
        
        # Get the updated_at timestamp
        all_rates = db_ops.get_all_currency_rates()
        updated_at = None
        for rate in all_rates:
            if (rate['from_currency'] == rate_data.from_currency.upper() and 
                rate['to_currency'] == rate_data.to_currency.upper()):
                updated_at = rate['updated_at']
                break
        
        return CurrencyRateResponse(
            from_currency=rate_data.from_currency.upper(),
            to_currency=rate_data.to_currency.upper(),
            rate=updated_rate,
            updated_at=updated_at or "Unknown"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting currency rate: {e}")
        raise HTTPException(status_code=500, detail="Failed to set currency rate")

@router.delete("/rates/{from_currency}/{to_currency}")
async def delete_currency_rate(from_currency: str, to_currency: str):
    """Delete a currency exchange rate"""
    try:
        success = db_ops.delete_currency_rate(from_currency.upper(), to_currency.upper())
        if not success:
            raise HTTPException(status_code=404, detail="Currency rate not found")
        
        return {"message": "Currency rate deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting currency rate: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete currency rate")

@router.post("/rates/bulk")
async def set_multiple_currency_rates(rates_data: List[CurrencyRateUpdate]):
    """Set or update multiple currency exchange rates at once"""
    try:
        results = []
        errors = []
        
        for rate_data in rates_data:
            try:
                success = db_ops.set_currency_rate(
                    rate_data.from_currency.upper(),
                    rate_data.to_currency.upper(),
                    rate_data.rate
                )
                
                if success:
                    results.append({
                        "from_currency": rate_data.from_currency.upper(),
                        "to_currency": rate_data.to_currency.upper(),
                        "rate": rate_data.rate,
                        "status": "success"
                    })
                else:
                    errors.append({
                        "from_currency": rate_data.from_currency.upper(),
                        "to_currency": rate_data.to_currency.upper(),
                        "error": "Failed to set rate"
                    })
            except Exception as e:
                errors.append({
                    "from_currency": rate_data.from_currency.upper(),
                    "to_currency": rate_data.to_currency.upper(),
                    "error": str(e)
                })
        
        return {
            "successful_updates": results,
            "errors": errors,
            "total_processed": len(rates_data),
            "successful_count": len(results),
            "error_count": len(errors)
        }
    except Exception as e:
        logger.error(f"Error setting multiple currency rates: {e}")
        raise HTTPException(status_code=500, detail="Failed to set multiple currency rates")
