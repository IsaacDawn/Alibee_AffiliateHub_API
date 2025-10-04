from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from services.currency_detector import currency_detector
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class CurrencyDetectionRequest(BaseModel):
    """Model for currency detection request"""
    text: Optional[str] = Field(None, description="Text to analyze for currency detection")
    price_text: Optional[str] = Field(None, description="Price text to analyze")
    country_text: Optional[str] = Field(None, description="Country text to analyze")
    product_data: Optional[Dict[str, Any]] = Field(None, description="Full product data")

class CurrencyDetectionResponse(BaseModel):
    """Model for currency detection response"""
    detected_currency: Optional[str] = None
    confidence: str = Field(..., description="Confidence level: high, medium, low")
    detection_method: Optional[str] = None
    extracted_price: Optional[float] = None
    currency_info: Optional[Dict[str, str]] = None

@router.post("/detect", response_model=CurrencyDetectionResponse)
async def detect_currency(request: CurrencyDetectionRequest):
    """Detect currency from various input sources"""
    try:
        detected_currency = None
        detection_method = None
        confidence = "low"
        extracted_price = None
        
        # Method 1: Detect from simple text (frontend compatibility)
        if request.text:
            detected_currency = currency_detector.detect_currency_from_text(request.text)
            if detected_currency:
                detection_method = "text"
                confidence = "medium"
                extracted_price = currency_detector.extract_price_from_text(request.text)
        
        # Method 2: Detect from product data (highest priority)
        if not detected_currency and request.product_data:
            detected_currency = currency_detector.detect_currency_from_product(request.product_data)
            if detected_currency:
                detection_method = "product_data"
                confidence = "high"
        
        # Method 3: Detect from price text
        if not detected_currency and request.price_text:
            detected_currency = currency_detector.detect_currency_from_price(request.price_text)
            if detected_currency:
                detection_method = "price_text"
                confidence = "medium"
                extracted_price = currency_detector.extract_price_from_text(request.price_text)
        
        # Method 4: Detect from country text
        if not detected_currency and request.country_text:
            detected_currency = currency_detector.detect_currency_from_country(request.country_text)
            if detected_currency:
                detection_method = "country_text"
                confidence = "medium"
        
        # Get currency information
        currency_info = None
        if detected_currency:
            currency_info = currency_detector.get_currency_info(detected_currency)
        
        return CurrencyDetectionResponse(
            detected_currency=detected_currency,
            confidence=confidence,
            detection_method=detection_method,
            extracted_price=extracted_price,
            currency_info=currency_info
        )
        
    except Exception as e:
        logger.error(f"Error detecting currency: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect currency")

@router.post("/detect/price", response_model=CurrencyDetectionResponse)
async def detect_currency_from_price(price_text: str):
    """Detect currency from price text only"""
    try:
        detected_currency = currency_detector.detect_currency_from_price(price_text)
        extracted_price = currency_detector.extract_price_from_text(price_text)
        
        currency_info = None
        if detected_currency:
            currency_info = currency_detector.get_currency_info(detected_currency)
        
        return CurrencyDetectionResponse(
            detected_currency=detected_currency,
            confidence="medium" if detected_currency else "low",
            detection_method="price_text",
            extracted_price=extracted_price,
            currency_info=currency_info
        )
        
    except Exception as e:
        logger.error(f"Error detecting currency from price: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect currency from price")

@router.post("/detect/country", response_model=CurrencyDetectionResponse)
async def detect_currency_from_country(country_text: str):
    """Detect currency from country text only"""
    try:
        detected_currency = currency_detector.detect_currency_from_country(country_text)
        
        currency_info = None
        if detected_currency:
            currency_info = currency_detector.get_currency_info(detected_currency)
        
        return CurrencyDetectionResponse(
            detected_currency=detected_currency,
            confidence="medium" if detected_currency else "low",
            detection_method="country_text",
            extracted_price=None,
            currency_info=currency_info
        )
        
    except Exception as e:
        logger.error(f"Error detecting currency from country: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect currency from country")

@router.get("/supported-currencies")
async def get_supported_currencies():
    """Get list of all supported currencies"""
    try:
        currencies = []
        for currency_code in currency_detector.currency_patterns.keys():
            currency_info = currency_detector.get_currency_info(currency_code)
            currencies.append({
                'code': currency_code,
                'name': currency_info['name'],
                'symbol': currency_info['symbol'],
                'flag': currency_info['flag']
            })
        
        return {
            'currencies': currencies,
            'count': len(currencies)
        }
        
    except Exception as e:
        logger.error(f"Error getting supported currencies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported currencies")

@router.get("/country-mappings")
async def get_country_currency_mappings():
    """Get country to currency mappings"""
    try:
        return {
            'mappings': currency_detector.country_currency_map,
            'count': len(currency_detector.country_currency_map)
        }
        
    except Exception as e:
        logger.error(f"Error getting country mappings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get country mappings")
