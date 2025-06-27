from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import math # isinf, isnan checks in calculated_ratios


# Company Profile

class CompanyProfileOut(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    name: str = Field(..., description="The full company name.")
    exchange: str = Field(..., description="The exchange where the stock is traded.")
    industry: Optional[str] = Field(None, description="The industry the company belongs to.")
    website: Optional[str] = Field(None, description="The official website of the company.")
    market_capitalization: float = Field(..., description="The total market value of the company's outstanding shares.")
    shares_outstanding: float = Field(..., description="The total number of shares outstanding for the company.")
    country: Optional[str] = None
    currency: Optional[str] = None
    ipo_date: Optional[str] = Field(None, description="The date of the company's Initial Public Offering.")
    logo_url: Optional[str] = Field(None, description="URL to the company's logo.")


# Financial Reports

# Model for a single financial line item
class FinancialItemOut(BaseModel):
    label: str = Field(..., description="A user-friendly label for the financial concept.")
    value: Optional[float] = Field(None, description="The numerical value of the financial concept.")
    unit: Optional[str] = Field(None, description="The unit of the value, e.g., 'usd'.")

# Model for a specific type of financial statement (e.g., Income Statement)
class IncomeStatementOut(BaseModel):
    revenue: Optional[FinancialItemOut] = None
    cost_of_revenue: Optional[FinancialItemOut] = None
    gross_profit: Optional[FinancialItemOut] = None
    operating_expenses: Optional[FinancialItemOut] = None
    operating_income: Optional[FinancialItemOut] = None
    net_income: Optional[FinancialItemOut] = None
    eps_basic: Optional[FinancialItemOut] = None

class BalanceSheetOut(BaseModel):
    cash_and_cash_equivalents: Optional[FinancialItemOut] = None
    marketable_securities: Optional[FinancialItemOut] = None
    accounts_receivable: Optional[FinancialItemOut] = None
    total_current_assets: Optional[FinancialItemOut] = None
    property_plant_equipment: Optional[FinancialItemOut] = None
    goodwill: Optional[FinancialItemOut] = None
    total_assets: Optional[FinancialItemOut] = None
    accounts_payable: Optional[FinancialItemOut] = None
    deferred_revenue: Optional[FinancialItemOut] = None
    total_current_liabilities: Optional[FinancialItemOut] = None
    long_term_debt: Optional[FinancialItemOut] = None
    total_liabilities: Optional[FinancialItemOut] = None
    total_equity: Optional[FinancialItemOut] = None

class CashFlowStatementOut(BaseModel):
    net_income: Optional[FinancialItemOut] = None # Net income from cash flow statement
    depreciation_amortization: Optional[FinancialItemOut] = None
    changes_in_working_capital: Optional[FinancialItemOut] = None
    cash_from_operating_activities: Optional[FinancialItemOut] = None
    capital_expenditures: Optional[FinancialItemOut] = None
    cash_from_investing_activities: Optional[FinancialItemOut] = None
    dividends_paid: Optional[FinancialItemOut] = None
    cash_from_financing_activities: Optional[FinancialItemOut] = None
    net_increase_decrease_in_cash: Optional[FinancialItemOut] = None

# Model for calculated ratios
class CalculatedRatiosOut(BaseModel):
    gross_margin: Optional[float] = Field(None, description="Gross Profit / Revenue.")
    operating_margin: Optional[float] = Field(None, description="Operating Income / Revenue.")
    net_profit_margin: Optional[float] = Field(None, description="Net Income / Revenue.")
    current_ratio: Optional[float] = Field(None, description="Current Assets / Current Liabilities.")
    debt_to_equity_ratio: Optional[float] = Field(None, description="Total Liabilities / Total Equity.")

# Model for a single comprehensive financial filing (e.g., latest 10-K)
class FinancialFilingOut(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")
    access_number: str = Field(..., description="SEC access number for the filing.")
    form_type: str = Field(..., description="Type of the SEC filing (e.g., 10-K, 10-Q).")
    year: int = Field(..., description="Fiscal year of the filing.")
    quarter: int = Field(..., description="Fiscal quarter of the filing (0 for annual).")
    start_date: Optional[str] = Field(None, description="Start date of the reporting period.")
    end_date: Optional[str] = Field(None, description="End date of the reporting period.")
    filed_date: Optional[str] = Field(None, description="Date the filing was submitted to SEC.")
    accepted_date: Optional[str] = Field(None, description="Date the filing was accepted by SEC.")

    # The structured statements
    income_statement: Optional[IncomeStatementOut] = None
    balance_sheet: Optional[BalanceSheetOut] = None
    cash_flow_statement: Optional[CashFlowStatementOut] = None

    # For the calculated ratios above
    calculated_ratios: Optional[CalculatedRatiosOut] = None

    # For Trends & Growth
    revenue_growth_yoy_percent: Optional[float] = Field(None, description="Year-over-Year Revenue Growth (%). Calculated for annual reports.")
    net_income_growth_yoy_percent: Optional[float] = Field(None, description="Year-over-Year Net Income Growth (%). Calculated for annual reports.")

    # Simplified Health Check Status
    financial_health_status: Optional[str] = Field(None, description="Overall qualitative assessment of financial health (e.g., 'Strong', 'Stable', 'Concerning').")

# Top-level model for returning a list of filings
class FinancialReportsOut(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol for which reports are provided.")
    filings: List[FinancialFilingOut] = Field(..., description="A list of financial filings.")


# Key Metrics

class KeyMetricsOut(BaseModel):
    symbol: str = Field(..., description="The stock ticker symbol.")

    # Valuation
    pe_ratio_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Price-to-Earnings Ratio.")
    ps_ratio_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Price-to-Sales Ratio.")
    pb_ratio: Optional[float] = Field(None, description="Latest Price-to-Book Ratio.")
    market_capitalization: Optional[float] = Field(None, description="Current Market Capitalization in millions USD.")

    # Profitability
    eps_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Earnings Per Share.")
    roe_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Return on Equity.")
    roa_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Return on Assets.")
    net_profit_margin_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Net Profit Margin.")
    gross_margin_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Gross Margin.")
    operating_margin_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Operating Margin.")

    # Liquidity & Solvency
    current_ratio_annual: Optional[float] = Field(None, description="Latest Annual Current Ratio.")
    quick_ratio_annual: Optional[float] = Field(None, description="Latest Annual Quick Ratio.")
    total_debt_to_equity_annual: Optional[float] = Field(None, description="Latest Annual Total Debt to Total Equity Ratio.")

    # Growth
    revenue_growth_ttm_yoy: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Year-over-Year Revenue Growth.")
    eps_growth_ttm_yoy: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Year-over-Year EPS Growth.")

    # Dividend
    dividend_per_share_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Dividend Per Share.")
    current_dividend_yield_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Current Dividend Yield.")

    # Price Info
    beta: Optional[float] = Field(None, description="Beta value, measuring volatility relative to the market.")
    fifty_two_week_high: Optional[float] = Field(None, alias="52_week_high", description="52-Week High Price.")
    fifty_two_week_low: Optional[float] = Field(None, alias="52_week_low", description="52-Week Low Price.")

    # Cash Flow
    cash_flow_per_share_ttm: Optional[float] = Field(None, description="Trailing Twelve Months (TTM) Cash Flow Per Share.")

    # Qualitative Assessments
    valuation_status: Optional[str] = Field(None, description="Qualitative assessment of current valuation (e.g., 'Undervalued', 'Fairly Valued', 'Overvalued').")
    profitability_assessment: Optional[str] = Field(None, description="Qualitative assessment of profitability (e.g., 'High', 'Moderate', 'Low', 'Unprofitable').")
    liquidity_assessment: Optional[str] = Field(None, description="Qualitative assessment of liquidity (e.g., 'Strong', 'Adequate', 'Weak').")
