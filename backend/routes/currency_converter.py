from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from services.currency_converter import currency_converter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class PriceConversionRequest(BaseModel):
    """Model for price conversion request"""
    price: float = Field(..., description="Price to convert")
    from_currency: str = Field(..., description="Source currency code")
    to_currency: str = Field(..., description="Target currency code")

class PriceConversionResponse(BaseModel):
    """Model for price conversion response"""
    original_price: float
    converted_price: float
    from_currency: str
    to_currency: str
    exchange_rate: float
    conversion_successful: bool

class BulkPriceConversionRequest(BaseModel):
    """Model for bulk price conversion request"""
    prices: List[float] = Field(..., description="List of prices to convert")
    from_currency: str = Field(..., description="Source currency code")
    to_currency: str = Field(..., description="Target currency code")

class BulkPriceConversionResponse(BaseModel):
    """Model for bulk price conversion response"""
    conversions: List[PriceConversionResponse]
    total_converted: int
    successful_conversions: int
    failed_conversions: int

@router.get("/test")
async def test_currency_route():
    """Test currency route"""
    return {"message": "Currency converter route is working"}

@router.post("/convert", response_model=PriceConversionResponse)
async def convert_price(request: PriceConversionRequest):
    """Convert a single price from one currency to another"""
    try:
        # Use USD base conversion strategy
        converted_price = currency_converter.convert_price(
            request.price,
            request.from_currency,
            request.to_currency
        )
        
        if converted_price is None:
            raise HTTPException(
                status_code=404, 
                detail=f"No conversion path found from {request.from_currency} to {request.to_currency}"
            )
        
        # Calculate effective exchange rate
        effective_rate = converted_price / request.price
        
        return PriceConversionResponse(
            original_price=request.price,
            converted_price=converted_price,
            from_currency=request.from_currency.upper(),
            to_currency=request.to_currency.upper(),
            exchange_rate=effective_rate,
            conversion_successful=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting price: {e}")
        raise HTTPException(status_code=500, detail="Failed to convert price")

@router.post("/convert/bulk", response_model=BulkPriceConversionResponse)
async def convert_prices_bulk(request: BulkPriceConversionRequest):
    """Convert multiple prices from one currency to another"""
    try:
        conversions = []
        successful_count = 0
        failed_count = 0
        
        # Get exchange rate once
        exchange_rate = currency_converter.get_exchange_rate(
            request.from_currency,
            request.to_currency
        )
        
        if exchange_rate is None:
            raise HTTPException(
                status_code=404,
                detail=f"No exchange rate found for {request.from_currency} to {request.to_currency}"
            )
        
        # Convert each price
        for price in request.prices:
            try:
                converted_price = currency_converter.convert_price(
                    price,
                    request.from_currency,
                    request.to_currency
                )
                
                if converted_price is not None:
                    conversions.append(PriceConversionResponse(
                        original_price=price,
                        converted_price=converted_price,
                        from_currency=request.from_currency.upper(),
                        to_currency=request.to_currency.upper(),
                        exchange_rate=exchange_rate,
                        conversion_successful=True
                    ))
                    successful_count += 1
                else:
                    conversions.append(PriceConversionResponse(
                        original_price=price,
                        converted_price=0.0,
                        from_currency=request.from_currency.upper(),
                        to_currency=request.to_currency.upper(),
                        exchange_rate=0.0,
                        conversion_successful=False
                    ))
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error converting price {price}: {e}")
                conversions.append(PriceConversionResponse(
                    original_price=price,
                    converted_price=0.0,
                    from_currency=request.from_currency.upper(),
                    to_currency=request.to_currency.upper(),
                    exchange_rate=0.0,
                    conversion_successful=False
                ))
                failed_count += 1
        
        return BulkPriceConversionResponse(
            conversions=conversions,
            total_converted=len(request.prices),
            successful_conversions=successful_count,
            failed_conversions=failed_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting prices in bulk: {e}")
        raise HTTPException(status_code=500, detail="Failed to convert prices")

@router.get("/rate/{from_currency}/{to_currency}")
async def get_exchange_rate(from_currency: str, to_currency: str):
    """Get exchange rate between two currencies"""
    try:
        rate = currency_converter.get_exchange_rate(from_currency, to_currency)
        
        if rate is None:
            raise HTTPException(
                status_code=404,
                detail=f"No exchange rate found for {from_currency} to {to_currency}"
            )
        
        return {
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "rate": rate,
            "message": f"1 {from_currency.upper()} = {rate} {to_currency.upper()}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exchange rate: {e}")
        raise HTTPException(status_code=500, detail="Failed to get exchange rate")

@router.post("/initialize-default-rates")
async def initialize_default_rates():
    """Initialize default exchange rates if none exist"""
    try:
        success = currency_converter.initialize_default_rates()
        
        if success:
            return {
                "message": "Default exchange rates initialized successfully",
                "success": True
            }
        else:
            return {
                "message": "Failed to initialize default exchange rates",
                "success": False
            }
            
    except Exception as e:
        logger.error(f"Error initializing default rates: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize default rates")
