"""Kenya Markets Provider Registration.

Registers all Kenya data fetchers with the OpenBB Platform.
"""

from openbb_core.provider.abstract.provider import Provider
from openbb_kenya.models.nse_equities import KenyaNSEEquityFetcher
from openbb_kenya.models.nse_indices import KenyaNSEIndexFetcher
from openbb_kenya.models.cbk_rates import KenyaCBKRatesFetcher
from openbb_kenya.models.cbk_inflation import KenyaCBKInflationFetcher
from openbb_kenya.models.cbk_forex import KenyaCBKForexFetcher
from openbb_kenya.models.regional_fx import KenyaRegionalFXFetcher

__version__ = "1.0.0"

kenya_provider = Provider(
    name="kenya",
    website="https://www.nse.co.ke",
    description="""Kenya and East African markets data provider for OpenBB Platform.
    
Provides comprehensive coverage of Kenyan financial markets including:
- Nairobi Securities Exchange (NSE) equities and indices
- Central Bank of Kenya (CBK) rates and economic data
- Regional FX pairs and macroeconomic indicators

Data sources include NSE, CBK, and KNBS where available.
Market intelligence features include trading calendar, liquidity warnings,
and data quality labels.""",
    credentials=[],  # Public data sources, no API keys required initially
    fetcher_dict={
        # NSE Data
        "EquityHistorical": KenyaNSEEquityFetcher,
        "IndexHistorical": KenyaNSEIndexFetcher,
        
        # CBK Data
        "TreasuryRates": KenyaCBKRatesFetcher,
        "ConsumerPriceIndex": KenyaCBKInflationFetcher,
        
        # Forex
        "CurrencyHistorical": KenyaRegionalFXFetcher,  # Regional FX pairs
        # "CurrencyHistorical": KenyaCBKForexFetcher,  # Alternative: Official CBK rates
        
        # Future additions:
        # "CompanyNews": KenyaNSENewsFetcher,
        # "EconomicCalendar": KenyaEconomicCalendarFetcher,
        # "EquityProfile": KenyaNSEProfileFetcher,
    },
    repr_name="Kenya Markets (NSE/CBK)",
    # deprecated_credentials={},  # None yet
)

__all__ = ["kenya_provider"]
