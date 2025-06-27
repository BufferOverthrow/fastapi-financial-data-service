import httpx # requests could be another option
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from app.schemas.finnhub_schemas import (
    FinnhubCompanyProfile2,
    FinnhubBasicFinancials,
    FinnhubFinancialsReport, FinancialFilingData, FinancialReportDetails, ReportItem
)


# Simple In-Memory Cache
# Cache Structure: { "endpoint_key": {"data": PydanticModelInstance, "timestamp": datetime_obj} }
_finnhub_cache: Dict[str, Dict[str, Any]] = {}
CACHE_EXPIRATION_SECONDS = 300 # 5 minutes

def _get_cache_key(endpoint: str, symbol: str, **kwargs) -> str:
    """Generates a unique cache key for a given request."""
    key_parts = [endpoint, symbol]
    for k, v in sorted(kwargs.items()): # Sort to ensure consistent key generation
        key_parts.append(f"{k}={v}")
    return "_".join(key_parts)

async def _fetch_from_finnhub(url: str, response_model: type) -> Any:
    """Generic function to fetch data from Finnhub and parse it into a Pydantic model."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses
        data = response.json()
        return response_model(**data)

# Service Functions

async def get_company_profile(symbol: str, api_key: str) -> Optional[FinnhubCompanyProfile2]:
    """
    Fetches the company profile data from Finnhub's /stock/profile2 endpoint.
    """

    cache_key = _get_cache_key("company_profile", symbol)

    # Check cache
    if cache_key in _finnhub_cache:
        cached_entry = _finnhub_cache[cache_key]
        if datetime.now() - cached_entry["timestamp"] < timedelta(seconds=CACHE_EXPIRATION_SECONDS):
            print(f"Cache hit for {cache_key}")
            return cached_entry["data"]
        else:
            print(f"Cache expired for {cache_key}")

    # Fetch fresh data
    url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}"
    try:
        profile = await _fetch_from_finnhub(url, FinnhubCompanyProfile2)
        _finnhub_cache[cache_key] = {"data": profile, "timestamp": datetime.now()}
        return profile
    except httpx.HTTPStatusError as e:
        # Handle specific Finnhub errors (e.g., symbol not found)
        if e.response.status_code == 400 and "Invalid symbol" in e.response.text:
            return None # Return None if symbol is invalid, (endpoint can raise 404)
        print(f"Finnhub API Error for {symbol} (company profile): {e}")
        raise # Re-raise for other HTTP errors (non-400)
    except httpx.RequestError as e:
        print(f"Network error fetching company profile for {symbol}: {e}")
        raise

async def get_basic_financials(symbol: str, api_key: str, metric_type: str = "all") -> Optional[FinnhubBasicFinancials]:
    """
    Fetches the company's basic financials from Finnhub's /stock/metric endpoint.
    """

    cache_key = _get_cache_key("basic_financials", symbol, metric=metric_type)

    if cache_key in _finnhub_cache:
        cached_entry = _finnhub_cache[cache_key]
        if datetime.now() - cached_entry["timestamp"] < timedelta(seconds=CACHE_EXPIRATION_SECONDS):
            print(f"Cache hit for {cache_key}")
            return cached_entry["data"]
        else:
            print(f"Cache expired for {cache_key}")

    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric={metric_type}&token={api_key}"
    try:
        financials = await _fetch_from_finnhub(url, FinnhubBasicFinancials)
        _finnhub_cache[cache_key] = {"data": financials, "timestamp": datetime.now()}
        return financials
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400 and "Invalid symbol" in e.response.text:
            return None
        print(f"Finnhub API Error for {symbol} (basic financials): {e}")
        raise
    except httpx.RequestError as e:
        print(f"Network error fetching basic financials for {symbol}: {e}")
        raise

async def get_financials_reported(symbol: str, api_key: str, report_type: str = "annual") -> Optional[FinnhubFinancialsReport]:
    """
    Fetches the company's reported financials from Finnhub's /stock/financials-reported endpoint.
    """

    # For reported financials, 'report_type' (annual/quarterly) is part of the cache key
    cache_key = _get_cache_key("financials_reported", symbol, type=report_type)

    if cache_key in _finnhub_cache:
        cached_entry = _finnhub_cache[cache_key]
        if datetime.now() - cached_entry["timestamp"] < timedelta(seconds=CACHE_EXPIRATION_SECONDS):
            print(f"Cache hit for {cache_key}")
            return cached_entry["data"]
        else:
            print(f"Cache expired for {cache_key}")

    url = f"https://finnhub.io/api/v1/stock/financials-reported?symbol={symbol}&type={report_type}&token={api_key}"
    try:
        financials_report = await _fetch_from_finnhub(url, FinnhubFinancialsReport)
        _finnhub_cache[cache_key] = {"data": financials_report, "timestamp": datetime.now()}
        return financials_report
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400 and "Invalid symbol" in e.response.text:
            return None
        print(f"Finnhub API Error for {symbol} (financials reported): {e}")
        raise
    except httpx.RequestError as e:
        print(f"Network error fetching financials reported for {symbol}: {e}")
        raise

