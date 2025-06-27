from fastapi import APIRouter, Depends, HTTPException
from app.services.finnhub_services import get_financials_reported
from app.schemas.app_schemas import (
    FinancialReportsOut, FinancialFilingOut, FinancialItemOut,
    IncomeStatementOut, BalanceSheetOut, CashFlowStatementOut,
    CalculatedRatiosOut
)
from app.schemas.finnhub_schemas import ReportItem, FinancialFilingData # Need FinancialFilingData for type hinting
from app.core.config import get_api_key
from typing import List, Dict, Optional
from collections import defaultdict # For organizing concepts by year
import math # For checking for NaN or infinity in calculations

router = APIRouter(tags=["Financials"])

def find_concept_value(report_items: Optional[List[ReportItem]], concept: str) -> Optional[FinancialItemOut]:
    """Helper function to find a specific concept in a list of ReportItem."""
    if report_items:
        for item in report_items:
            if item.concept == concept:
                # Ensure value is a float before returning, handle None
                val = item.value if isinstance(item.value, (int, float)) else None
                return FinancialItemOut(label=item.label, value=val, unit=item.unit)
    return None

def _calculate_growth_rate(current_value: Optional[float], previous_value: Optional[float]) -> Optional[float]:
    """Calculates Year-over-Year growth rate in percentage."""
    if current_value is None or previous_value is None:
        return None
    if previous_value == 0:
        # Handle division by zero: return inf/negative inf if current_value is positive/negative
        return float('inf') if current_value > 0 else (float('-inf') if current_value < 0 else 0.0)

    growth = ((current_value - previous_value) / previous_value) * 100
    return round(growth, 2) # Round for cleaner output

def _assess_financial_health(
    net_income: Optional[float],
    cash_from_operating_activities: Optional[float],
    current_ratio: Optional[float],
    debt_to_equity_ratio: Optional[float]
) -> Optional[str]:
    """Provides an overall qualitative assessment of financial health."""
    # Check if all inputs are None, if so, we can't assess
    # I like this functional way of doing it
    if all(x is None for x in [net_income, cash_from_operating_activities, current_ratio, debt_to_equity_ratio]):
        return None

    score = 0 # Simple scoring system
    num_factors_considered = 0

    if net_income is not None:
        num_factors_considered += 1
        if net_income > 0: score += 1

    if cash_from_operating_activities is not None:
        num_factors_considered += 1
        if cash_from_operating_activities > 0: score += 1

    if current_ratio is not None and not math.isinf(current_ratio) and not math.isnan(current_ratio):
        num_factors_considered += 1
        if current_ratio >= 1.5: score += 1 # Good liquidity
        elif current_ratio < 1.0: score -= 1 # Poor liquidity

    if debt_to_equity_ratio is not None and not math.isinf(debt_to_equity_ratio) and not math.isnan(debt_to_equity_ratio):
        num_factors_considered += 1
        if debt_to_equity_ratio <= 1.0: score += 1 # Low debt
        elif debt_to_equity_ratio > 2.0: score -= 1 # High debt

    if num_factors_considered == 0:
        return None # No meaningful data points to assess

    if score >= 2:
        return "Strong"
    elif score >= 0:
        return "Stable"
    else:
        return "Concerning"

@router.get("/company/{symbol}/financial-statements-summary", response_model=FinancialReportsOut)
async def get_company_financials_endpoint(
    symbol: str,
    api_key: str = Depends(get_api_key)
):

    # Fetch all available annual reports for growth calculations
    finnhub_data = await get_financials_reported(symbol, api_key, report_type="annual")

    if not finnhub_data or not finnhub_data.data:
        raise HTTPException(status_code=404, detail=f"No annual financial reports found for {symbol}. It might be an invalid symbol or data is not available.")

    # Filter for annual reports (quarter 0, form 10-K) and sort by end_date descending
    # This helps in calculating YoY growth as iteration is from latest to oldest
    # (I'm interested in learning functional programming, so this code)
    annual_filings = sorted(
        [f for f in finnhub_data.data if f.quarter == 0 and f.form == "10-K" and f.report],
        key=lambda x: x.endDate if x.endDate else "", # Use endDate for sorting fiscal years
        reverse=True
    )

    if not annual_filings:
        raise HTTPException(status_code=404, detail=f"No 10-K annual reports found for {symbol} after filtering.")

    filings_out: List[FinancialFilingOut] = []

    # Store key values from previous years for growth calculations
    previous_year_values: Dict[str, Optional[float]] = defaultdict(lambda: None)

    for i, filing in enumerate(annual_filings):

        income_statement = IncomeStatementOut()
        balance_sheet = BalanceSheetOut()
        cash_flow_statement = CashFlowStatementOut()
        calculated_ratios = CalculatedRatiosOut()

        # Temporary variables to hold current year's extracted values for calculations
        current_revenue = None
        current_net_income_ic = None # From income statement
        current_gross_profit = None
        current_operating_income = None
        current_total_current_assets = None
        current_total_current_liabilities = None
        current_total_liabilities = None
        current_total_equity = None
        current_cash_from_ops = None # From cash flow statement

        # Populate Statement Data & Extract values for calculations
        if filing.report.ic:
            inc_revenue = find_concept_value(filing.report.ic, "us-gaap_Revenues")
            if not inc_revenue:
                inc_revenue = find_concept_value(filing.report.ic, "us-gaap_SalesRevenueNet")
            income_statement.revenue = inc_revenue
            current_revenue = inc_revenue.value if inc_revenue else None

            inc_cost_of_revenue = find_concept_value(filing.report.ic, "us-gaap_CostOfRevenue")
            income_statement.cost_of_revenue = inc_cost_of_revenue

            inc_gross_profit = find_concept_value(filing.report.ic, "us-gaap_GrossProfit")
            income_statement.gross_profit = inc_gross_profit
            current_gross_profit = inc_gross_profit.value if inc_gross_profit else None

            inc_operating_income = find_concept_value(filing.report.ic, "us-gaap_OperatingIncomeLoss")
            income_statement.operating_income = inc_operating_income
            current_operating_income = inc_operating_income.value if inc_operating_income else None

            inc_net_income = find_concept_value(filing.report.ic, "us-gaap_NetIncomeLoss")
            income_statement.net_income = inc_net_income
            current_net_income_ic = inc_net_income.value if inc_net_income else None

            income_statement.eps_basic = find_concept_value(filing.report.ic, "us-gaap_EarningsPerShareBasic")

        if filing.report.bs:
            balance_sheet.cash_and_cash_equivalents = find_concept_value(filing.report.bs, "us-gaap_CashAndCashEquivalentsAtCarryingValue")
            balance_sheet.marketable_securities = find_concept_value(filing.report.bs, "us-gaap_MarketableSecuritiesCurrent")
            balance_sheet.accounts_receivable = find_concept_value(filing.report.bs, "us-gaap_AccountsReceivableNetCurrent")

            bs_total_current_assets = find_concept_value(filing.report.bs, "us-gaap_AssetsCurrent")
            balance_sheet.total_current_assets = bs_total_current_assets
            current_total_current_assets = bs_total_current_assets.value if bs_total_current_assets else None

            balance_sheet.property_plant_equipment = find_concept_value(filing.report.bs, "us-gaap_PropertyPlantAndEquipmentNet")
            balance_sheet.total_assets = find_concept_value(filing.report.bs, "us-gaap_Assets")

            balance_sheet.accounts_payable = find_concept_value(filing.report.bs, "us-gaap_AccountsPayableCurrent")
            balance_sheet.deferred_revenue = find_concept_value(filing.report.bs, "us-gaap_DeferredRevenueCurrent")

            bs_total_current_liabilities = find_concept_value(filing.report.bs, "us-gaap_LiabilitiesCurrent")
            balance_sheet.total_current_liabilities = bs_total_current_liabilities
            current_total_current_liabilities = bs_total_current_liabilities.value if bs_total_current_liabilities else None

            bs_long_term_debt = find_concept_value(filing.report.bs, "us-gaap_LongTermDebt")
            balance_sheet.long_term_debt = bs_long_term_debt

            bs_total_liabilities = find_concept_value(filing.report.bs, "us-gaap_Liabilities")
            balance_sheet.total_liabilities = bs_total_liabilities
            current_total_liabilities = bs_total_liabilities.value if bs_total_liabilities else None

            bs_total_equity = find_concept_value(filing.report.bs, "us-gaap_StockholdersEquity")
            balance_sheet.total_equity = bs_total_equity
            current_total_equity = bs_total_equity.value if bs_total_equity else None

        if filing.report.cf:
            cash_flow_statement.net_income = find_concept_value(filing.report.cf, "us-gaap_NetIncomeLoss") # Net Income often appears here too
            cash_flow_statement.depreciation_amortization = find_concept_value(filing.report.cf, "us-gaap_DepreciationDepletionAndAmortization")

            cf_cash_from_operating_activities = find_concept_value(filing.report.cf, "us-gaap_NetCashProvidedByUsedInOperatingActivities")
            cash_flow_statement.cash_from_operating_activities = cf_cash_from_operating_activities
            current_cash_from_ops = cf_cash_from_operating_activities.value if cf_cash_from_operating_activities else None

            cash_flow_statement.capital_expenditures = find_concept_value(filing.report.cf, "us-gaap_PaymentsToAcquireProductiveAssets")
            cash_flow_statement.cash_from_investing_activities = find_concept_value(filing.report.cf, "us-gaap_NetCashProvidedByUsedInInvestingActivities")
            cash_flow_statement.dividends_paid = find_concept_value(filing.report.cf, "us-gaap_PaymentsOfDividends")
            cash_flow_statement.cash_from_financing_activities = find_concept_value(filing.report.cf, "us-gaap_NetCashProvidedByUsedInFinancingActivities")
            cash_flow_statement.net_increase_decrease_in_cash = find_concept_value(filing.report.cf, "us-gaap_CashAndCashEquivalentsPeriodIncreaseDecrease")


        # Calculate Ratios
        # Gross Margin = Gross Profit / Revenue
        if current_gross_profit is not None and current_revenue is not None and current_revenue != 0:
            calculated_ratios.gross_margin = round(current_gross_profit / current_revenue, 4)

        # Operating Margin = Operating Income / Revenue
        if current_operating_income is not None and current_revenue is not None and current_revenue != 0:
            calculated_ratios.operating_margin = round(current_operating_income / current_revenue, 4)

        # Net Profit Margin = Net Income / Revenue (using IC net income)
        if current_net_income_ic is not None and current_revenue is not None and current_revenue != 0:
            calculated_ratios.net_profit_margin = round(current_net_income_ic / current_revenue, 4)

        # Current Ratio = Current Assets / Current Liabilities
        if current_total_current_assets is not None and current_total_current_liabilities is not None and current_total_current_liabilities != 0:
            calculated_ratios.current_ratio = round(current_total_current_assets / current_total_current_liabilities, 2)
        elif current_total_current_assets is not None and current_total_current_liabilities == 0: # Handle zero liabilities
            calculated_ratios.current_ratio = float('inf')

        # Debt to Equity Ratio = Total Liabilities / Total Equity
        if current_total_liabilities is not None and current_total_equity is not None and current_total_equity != 0:
            calculated_ratios.debt_to_equity_ratio = round(current_total_liabilities / current_total_equity, 2)
        elif current_total_liabilities is not None and current_total_equity == 0: # Handle zero equity
             calculated_ratios.debt_to_equity_ratio = float('inf')


        # Calculate Growth Rates (YoY)
        # These are calculated based on current vs previous annual filing.
        revenue_growth_yoy = _calculate_growth_rate(current_revenue, previous_year_values["revenue"])
        net_income_growth_yoy = _calculate_growth_rate(current_net_income_ic, previous_year_values["net_income_ic"])

        # Financial Health Assessment
        health_status = _assess_financial_health(
            current_net_income_ic,
            current_cash_from_ops,
            calculated_ratios.current_ratio,
            calculated_ratios.debt_to_equity_ratio
        )

        # Create a FinancialFilingOut instance for this filing
        filing_out = FinancialFilingOut(
            symbol=filing.symbol,
            access_number=filing.accessNumber,
            form_type=filing.form,
            year=filing.year,
            quarter=filing.quarter,
            start_date=filing.startDate,
            end_date=filing.endDate,
            filed_date=filing.filedDate,
            accepted_date=filing.acceptedDate,
            income_statement=income_statement if any(v is not None for v in income_statement.model_dump().values()) else None,
            balance_sheet=balance_sheet if any(v is not None for v in balance_sheet.model_dump().values()) else None,
            cash_flow_statement=cash_flow_statement if any(v is not None for v in cash_flow_statement.model_dump().values()) else None,
            # Only include calculated_ratios if it has valid values (not None, inf, or NaN)
            calculated_ratios=calculated_ratios if any(v is not None and not (isinstance(v, float) and (math.isinf(v) or math.isnan(v))) for v in calculated_ratios.model_dump().values()) else None,

            revenue_growth_yoy_percent=revenue_growth_yoy,
            net_income_growth_yoy_percent=net_income_growth_yoy,
            financial_health_status=health_status,
        )
        filings_out.append(filing_out)

        # Update previous year's data for the next iteration (which will be an older filing)
        previous_year_values["revenue"] = current_revenue
        previous_year_values["net_income_ic"] = current_net_income_ic


    # filings_out is already sorted from latest to oldest
    return FinancialReportsOut(symbol=symbol, filings=filings_out)
