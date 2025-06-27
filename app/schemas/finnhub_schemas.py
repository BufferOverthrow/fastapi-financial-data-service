from pydantic import BaseModel, Field, RootModel
from typing import Optional, List, Dict, Any

# For the Company Profile Data
class FinnhubCompanyProfile2(BaseModel):
    country: str
    currency: str
    exchange: str
    ipo: str
    marketCapitalization: float
    name: str
    phone: Optional[str] = None
    shareOutstanding: float
    ticker: str
    weburl: Optional[str] = None
    logo: Optional[str] = None
    finnhubIndustry: Optional[str] = None

# For the Financial Reports Data
class ReportItem(BaseModel):
    concept: str
    unit: str
    label: str
    value: Optional[float]

class FinancialStatementSection(RootModel[List[ReportItem]]):
    """
    Represents a section of a financial statement (e.g., income statement, balance sheet)
    which is a list of individual report items.
    """
    pass # Apparently, no fields are needed here in Pydantic V2, the list type is defined in RootModel[...]

class FinancialReportDetails(BaseModel):
    # I have to remember that if not all of these keys are always present,
    # I need to try doing Dict[str, List[ReportItem]]. Would work better if
    # bs, ic, and cf are dynamic.

    bs: Optional[List[ReportItem]] = None # Balance Sheet
    ic: Optional[List[ReportItem]] = None # Income Statement
    cf: Optional[List[ReportItem]] = None # Cash Flow

class FinancialFilingData(BaseModel):
    accessNumber: str
    symbol: str
    cik: str
    year: int
    quarter: int
    form: str
    startDate: str # Will change to datetime.date if parsing would be required later
    endDate: str   # Will change to datetime.date if parsing would be required later
    filedDate: str # Will change to datetime.date if parsing would be required later
    acceptedDate: str # Will change to datetime.date if parsing would be required later
    report: FinancialReportDetails

class FinnhubFinancialsReport(BaseModel):
    cik: str
    data: List[FinancialFilingData]
    symbol: str # This 'symbol' is the ticker for the whole report

# For the Metrics Data
class FinnhubMetricData(BaseModel):
    # Valuation Ratios
    peTTM: Optional[float] = None
    psTTM: Optional[float] = None
    pb: Optional[float] = None

    # Profitability Ratios
    epsTTM: Optional[float] = None
    roeTTM: Optional[float] = None
    roaTTM: Optional[float] = None
    netProfitMarginTTM: Optional[float] = None
    grossMarginTTM: Optional[float] = None
    operatingMarginTTM: Optional[float] = None

    # Liquidity & Solvency
    currentRatioAnnual: Optional[float] = None # Using Annual for consistency
    quickRatioAnnual: Optional[float] = None
    totalDebt_totalEquityAnnual: Optional[float] = Field(None, alias='totalDebt/totalEquityAnnual') # The alias for '/'

    # Growth Rates (TTM for latest, or 5Y for longer-term)
    revenueGrowthTTMYoy: Optional[float] = None
    epsGrowthTTMYoy: Optional[float] = None

    # Dividend Information
    dividendPerShareTTM: Optional[float] = None
    currentDividendYieldTTM: Optional[float] = None

    # Price & Volatility
    beta: Optional[float] = None
    marketCapitalization: Optional[float] = None
    fifty_two_week_high: Optional[float] = Field(None, alias='52WeekHigh')
    fifty_two_week_low: Optional[float] = Field(None, alias='52WeekLow')


    cashFlowPerShareTTM: Optional[float] = None

    # To allow extra fields not included (There are a huuge lot!)
    class Config:
        extra = "allow" # This allows Pydantic to ignore fields not explicitly defined
        populate_by_name = True # Allows using field names like '52WeekHigh' (with alias)
                                # or 'totalDebt_totalEquityAnnual' (with alias)


# The top-level response for /stock/metric
class FinnhubBasicFinancials(BaseModel):
    metric: Optional[FinnhubMetricData] = None
    metricType: str
    symbol: Optional[str] = None
    series: Optional[Dict[str, Any]] = None # Ignoring this for now, but include it to avoid Pydantic errors if present
