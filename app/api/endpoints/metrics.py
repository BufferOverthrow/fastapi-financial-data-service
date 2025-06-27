from fastapi import APIRouter, Depends, HTTPException
from app.services.finnhub_services import get_basic_financials
from app.schemas.app_schemas import KeyMetricsOut
from app.core.config import get_api_key
from typing import Optional

router = APIRouter(tags=["Metrics"])

# Helper functions for qualitative assessments
def _assess_valuation(pe_ratio: Optional[float]) -> Optional[str]:
    """Provides a simple qualitative assessment of valuation based on P/E ratio."""
    if pe_ratio is None:
        return None
    if pe_ratio < 15:
        return "Potentially Undervalued"
    elif 15 <= pe_ratio <= 25:
        return "Fairly Valued"
    elif pe_ratio > 25:
        return "Potentially Overvalued"
    return None

def _assess_profitability(net_profit_margin: Optional[float]) -> Optional[str]:
    """Provides a simple qualitative assessment of profitability based on Net Profit Margin."""
    if net_profit_margin is None:
        return None
    # Assuming margins are provided as decimals (e.g., 0.25 for 25%)
    if net_profit_margin >= 0.20: # 20%
        return "High Profitability"
    elif 0.10 <= net_profit_margin < 0.20: # 10-20%
        return "Moderate Profitability"
    elif net_profit_margin < 0.10 and net_profit_margin >= 0: # 0-10%
        return "Low Profitability"
    elif net_profit_margin < 0:
        return "Unprofitable"
    return None

def _assess_liquidity(current_ratio: Optional[float]) -> Optional[str]:
    """Provides a simple qualitative assessment of liquidity based on Current Ratio."""
    if current_ratio is None:
        return None
    if current_ratio >= 2.0:
        return "Strong Liquidity"
    elif 1.0 <= current_ratio < 2.0:
        return "Adequate Liquidity"
    elif current_ratio < 1.0:
        return "Weak Liquidity"
    return None

@router.get("/company/{symbol}/key-metrics", response_model=KeyMetricsOut)
async def get_company_metrics_endpoint(
    symbol: str,
    api_key: str = Depends(get_api_key)
):

    finnhub_data = await get_basic_financials(symbol, api_key)

    if not finnhub_data or not finnhub_data.metric:
        raise HTTPException(status_code=404, detail=f"No key metrics found for {symbol}. It might be an invalid symbol or data is not available.")

    metrics = finnhub_data.metric

    # Ensure proper handling of `totalDebt/totalEquityAnnual` with its alias. (forward slash char)
    # The Pydantic model (`FinnhubMetricData`) uses `totalDebt_totalEquityAnnual` as the Python attribute.

    key_metrics_out = KeyMetricsOut(
        symbol=finnhub_data.symbol,

        pe_ratio_ttm=metrics.peTTM,
        ps_ratio_ttm=metrics.psTTM,
        pb_ratio=metrics.pb,
        market_capitalization=metrics.marketCapitalization,

        eps_ttm=metrics.epsTTM,
        roe_ttm=metrics.roeTTM,
        roa_ttm=metrics.roaTTM,
        net_profit_margin_ttm=metrics.netProfitMarginTTM,
        gross_margin_ttm=metrics.grossMarginTTM,
        operating_margin_ttm=metrics.operatingMarginTTM,

        current_ratio_annual=metrics.currentRatioAnnual,
        quick_ratio_annual=metrics.quickRatioQuarterly, # Using Quarterly as per Finnhub data
        total_debt_to_equity_annual=metrics.totalDebt_totalEquityAnnual,

        # Growth (converting to percentage)
        revenue_growth_ttm_yoy_percent=metrics.revenueGrowthTTMYoy * 100 if metrics.revenueGrowthTTMYoy is not None else None,
        eps_growth_ttm_yoy_percent=metrics.epsGrowthTTMYoy * 100 if metrics.epsGrowthTTMYoy is not None else None,

        dividend_per_share_ttm=metrics.dividendPerShareTTM,
        current_dividend_yield_ttm=metrics.currentDividendYieldTTM,

        beta=metrics.beta,
        fifty_two_week_high=metrics.fifty_two_week_high,
        fifty_two_week_low=metrics.fifty_two_week_low,

        cash_flow_per_share_ttm=metrics.cashFlowPerShareTTM,

        # Qualitative Assessments
        valuation_status=_assess_valuation(metrics.peTTM),
        profitability_assessment=_assess_profitability(metrics.netProfitMarginTTM),
        liquidity_assessment=_assess_liquidity(metrics.currentRatioAnnual)
    )

    return key_metrics_out
