from dataclasses import dataclass

@dataclass(frozen=True)
class SeriesSpec:
    key: str
    provider: str
    provider_id: str
    description: str
    frequency: str

MACRO_SERIES = (
    SeriesSpec("us_2y", "fred", "DGS2", "US Treasury 2-Year", "daily"),
    SeriesSpec("us_10y", "fred", "DGS10", "US Treasury 10-Year", "daily"),
    SeriesSpec("real_10y", "fred", "DFII10", "10-Year Real Treasury Yield", "daily"),
    SeriesSpec("vix", "fred", "VIXCLS", "CBOE VIX", "daily"),
    SeriesSpec("dollar_broad", "fred", "DTWEXBGS", "Broad US Dollar Index", "daily"),
    SeriesSpec("fed_funds", "fred", "DFF", "Effective Federal Funds Rate", "daily"),
    SeriesSpec("cpi", "fred", "CPIAUCSL", "Consumer Price Index", "monthly"),
    SeriesSpec("core_cpi", "fred", "CPILFESL", "Core CPI", "monthly"),
    SeriesSpec("pce", "fred", "PCEPI", "PCE Price Index", "monthly"),
    SeriesSpec("core_pce", "fred", "PCEPILFE", "Core PCE Price Index", "monthly"),
    SeriesSpec("unemployment", "fred", "UNRATE", "US Unemployment Rate", "monthly"),
    SeriesSpec("payrolls", "fred", "PAYEMS", "Total Nonfarm Payrolls", "monthly"),
)

COT_MARKETS = {
    "NASDAQ_100": {"market_code": "209742", "family": "financial_futures"},
    "GOLD": {"market_code": "088691", "family": "disaggregated"},
}
