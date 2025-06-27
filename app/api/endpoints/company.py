from fastapi import APIRouter, Depends
from app.services.finnhub_services import get_company_profile
from app.schemas.app_schemas import CompanyProfileOut
from app.core.config import get_api_key

router = APIRouter(tags=["Company"])

@router.get("/company/{symbol}/profile", response_model=CompanyProfileOut)
async def get_company_profile_endpoint(
    symbol: str,
    api_key: str = Depends(get_api_key)
):


    finnhub_data = await get_company_profile(symbol, api_key)

    # Transform Finnhub-specific data to your app's standardized output schema
    company_profile_out = CompanyProfileOut(
        symbol=finnhub_data.ticker,
        name=finnhub_data.name,
        exchange=finnhub_data.exchange,
        industry=finnhub_data.finnhubIndustry,
        website=finnhub_data.weburl,
        market_capitalization=finnhub_data.marketCapitalization,
        shares_outstanding=finnhub_data.shareOutstanding,
        country=finnhub_data.country,
        currency=finnhub_data.currency,
        ipo_date=finnhub_data.ipo,
        logo_url=finnhub_data.logo
    )

    return company_profile_out
