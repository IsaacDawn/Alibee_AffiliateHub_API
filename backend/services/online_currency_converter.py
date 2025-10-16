from typing import Optional, Dict, Any, List
import requests
import logging
import time
from functools import lru_cache
import json

logger = logging.getLogger(__name__)

class OnlineCurrencyConverter:
    """Online currency conversion service using real-time exchange rates"""
    
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.fallback_url = "https://api.fixer.io/latest"
        self._rate_cache = {}
        self._cache_timestamp = 0
        self._cache_duration = 300  # 5 minutes cache
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Alibee-Affiliate/1.0'
        })
    
    def _load_rates_from_api(self, base_currency: str = "USD") -> Dict[str, float]:
        """Load exchange rates from online API"""
        try:
            url = f"{self.base_url}/{base_currency}"
            response = self._session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            logger.info(f"Loaded {len(rates)} exchange rates from API for base {base_currency}")
            return rates
            
        except Exception as e:
            logger.error(f"Error loading rates from API: {e}")
            return {}
    
    def _get_cached_rates(self, base_currency: str = "USD") -> Dict[str, float]:
        """Get cached rates or load from API"""
        current_time = time.time()
        cache_key = f"rates_{base_currency}"
        
        # Check if cache is valid
        if (current_time - self._cache_timestamp < self._cache_duration and 
            cache_key in self._rate_cache):
            return self._rate_cache[cache_key]
        
        # Load fresh rates
        rates = self._load_rates_from_api(base_currency)
        if rates:
            self._rate_cache[cache_key] = rates
            self._cache_timestamp = current_time
        
        return rates
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get exchange rate between two currencies"""
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            if from_currency == to_currency:
                return 1.0
            
            # Try to get rates with USD as base
            rates = self._get_cached_rates("USD")
            if not rates:
                return None
            
            # If from_currency is USD, directly get the rate
            if from_currency == "USD":
                return rates.get(to_currency)
            
            # If to_currency is USD, calculate inverse rate
            if to_currency == "USD":
                from_rate = rates.get(from_currency)
                return 1.0 / from_rate if from_rate else None
            
            # Convert via USD: from_currency -> USD -> to_currency
            from_rate = rates.get(from_currency)
            to_rate = rates.get(to_currency)
            
            if from_rate and to_rate:
                return to_rate / from_rate
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting exchange rate from {from_currency} to {to_currency}: {e}")
            return None
    
    def convert_price(self, price: float, from_currency: str, to_currency: str) -> Optional[float]:
        """Convert price from one currency to another"""
        try:
            from_currency = from_currency.upper()
            to_currency = to_currency.upper()
            
            if from_currency == to_currency:
                return price
            
            if to_currency not in ['USD', 'EUR', 'ILS']:
                logger.warning(f"Target currency {to_currency} not supported")
                return None
            
            rate = self.get_exchange_rate(from_currency, to_currency)
            if rate is not None:
                converted_price = price * rate
                logger.debug(f"Converted {price} {from_currency} to {converted_price} {to_currency} (rate: {rate})")
                return round(converted_price, 2)
            
            logger.warning(f"No exchange rate found from {from_currency} to {to_currency}")
            return None
            
        except Exception as e:
            logger.error(f"Error converting price from {from_currency} to {to_currency}: {e}")
            return None
    
    def batch_convert_prices(self, conversions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert multiple prices in batch"""
        # Load rates once for all conversions
        rates = self._get_cached_rates("USD")
        if not rates:
            logger.error("Failed to load exchange rates for batch conversion")
            return [{"original": conv, "converted_price": None, "success": False, "error": "Failed to load rates"} 
                   for conv in conversions]
        
        results = []
        for conversion in conversions:
            try:
                price = conversion['price']
                from_currency = conversion['from_currency'].upper()
                to_currency = conversion['to_currency'].upper()
                
                converted_price = self.convert_price(price, from_currency, to_currency)
                
                results.append({
                    'original': conversion,
                    'converted_price': converted_price,
                    'success': converted_price is not None
                })
                
            except Exception as e:
                logger.error(f"Error in batch conversion: {e}")
                results.append({
                    'original': conversion,
                    'converted_price': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        rates = self._get_cached_rates("USD")
        return list(rates.keys()) if rates else []
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        rates = self._get_cached_rates("USD")
        return {
            'cached_rates_count': len(rates) if rates else 0,
            'cache_age_seconds': time.time() - self._cache_timestamp,
            'supported_currencies': self.get_supported_currencies(),
            'api_source': 'ExchangeRate-API',
            'cache_duration_minutes': self._cache_duration / 60,
            'last_update': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self._cache_timestamp))
        }
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Test API connection and get sample rates"""
        try:
            rates = self._load_rates_from_api("USD")
            if rates:
                return {
                    'success': True,
                    'message': 'API connection successful',
                    'sample_rates': {
                        'USD_EUR': rates.get('EUR'),
                        'USD_ILS': rates.get('ILS'),
                        'USD_CNY': rates.get('CNY'),
                        'USD_INR': rates.get('INR')
                    },
                    'total_currencies': len(rates)
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to load rates from API'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'API connection failed: {str(e)}'
            }

# Create global online currency converter instance
online_currency_converter = OnlineCurrencyConverter()
