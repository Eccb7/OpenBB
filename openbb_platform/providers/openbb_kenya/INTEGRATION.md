# Kenya Provider - Integration Guide

## Quick Start

### 1. Installation

```bash
# Navigate to the Kenya provider directory
cd /home/ojwang/OpenBB/openbb_platform/providers/openbb_kenya

# Install in editable mode
pip install -e .

# Or install all OpenBB platform providers
cd /home/ojwang/OpenBB/openbb_platform
python dev_install.py -e
```

### 2. Verify Installation

```python
# Test provider import
from openbb_kenya import kenya_provider

print(f"Provider: {kenya_provider.name}")
print(f"Description: {kenya_provider.description}")
print(f"Available Fetchers: {list(kenya_provider.fetcher_dict.keys())}")
```

Expected output:
```
Provider: kenya
Description: Kenya and East African markets data provider for OpenBB Platform...
Available Fetchers: ['EquityHistorical', 'IndexHistorical', 'TreasuryRates', 'ConsumerPriceIndex', 'CurrencyHistorical']
```

## Usage Examples

### NSE Equity Data

```python
from openbb import obb

# Fetch Safaricom historical data
safaricom = obb.equity.price.historical(
    symbol="SCOM.NR",  # or just "SCOM"
    provider="kenya",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Convert to DataFrame
df = safaricom.to_dataframe()
print(df.tail())

# Access specific fields
print(f"Latest close: KES {df.iloc[-1]['close']:.2f}")
print(f"Average volume: {df['volume'].mean():,.0f}")
```

### NSE Indices

```python
# NSE 20 Index
nse20 = obb.index.price.historical(
    symbol="NSE20",
    provider="kenya",
    start_date="2024-01-01"
)

# NSE All Share Index
nseasi = obb.index.price.historical(
    symbol="NSEASI",
    provider="kenya"
)
```

### CBK Interest Rates

```python
# Central Bank Rate and T-Bill rates
rates = obb.fixedincome.government.treasury_rates(
    country="kenya",
    provider="kenya"
)

df_rates = rates.to_dataframe()
print(df_rates)
```

### CBK Inflation (CPI)

```python
# Consumer Price Index data
cpi = obb.economy.cpi(
    country="kenya",
    provider="kenya",
    start_date="2023-01-01"
)

df_cpi = cpi.to_dataframe()
print(f"Latest CPI: {df_cpi.iloc[-1]['headline_cpi']}")
print(f"YoY Inflation: {df_cpi.iloc[-1]['yoy_change']*100:.2f}%")
```

### Regional FX Pairs

```python
# KES/USD exchange rate
kesusd = obb.currency.price.historical(
    symbol="KESUSD",
    provider="kenya",
    start_date="2024-01-01"
)

# East African pairs
kesugx = obb.currency.price.historical(
    symbol="KESUGX",  # KES/UGX
    provider="kenya"
)

kestzs = obb.currency.price.historical(
    symbol="KESTZS",  # KES/TZS
    provider="kenya"
)
```

## Advanced Usage

### Market Calendar

```python
from openbb_kenya.utils import NSECalendar
from datetime import date, datetime

# Check if market is open today
today = date.today()
is_open = NSECalendar.is_trading_day(today)
print(f"Market open today: {is_open}")

# Get trading hours
start, end = NSECalendar.get_trading_hours()
print(f"Trading: {start} - {end} EAT")

# Check if market is currently open
now = datetime.now()
currently_open = NSECalendar.is_market_open(now)

# Calculate settlement date
trade_date = date.today()
settlement = NSECalendar.settlement_date(trade_date)
print(f"Trade on {trade_date} settles on {settlement}")
```

### Data Validation

```python
from openbb_kenya.utils import (
    validate_nse_symbol,
    validate_nse_index,
    validate_fx_pair,
    validate_date_range
)

# Validate and normalize symbols
symbols = ["SCOM", "kcb", "EQTY.NR"]
for sym in symbols:
    normalized = validate_nse_symbol(sym)
    print(f"{sym} → {normalized}")

# Validate FX pairs
pair = validate_fx_pair("KES/USD")  # Returns "KESUSD"

# Validate date ranges
from datetime import date, timedelta
start = date.today() - timedelta(days=365)
end = date.today()
validated_start, validated_end = validate_date_range(start, end)
```

### Data Quality Warnings

```python
from openbb_kenya.utils import (
    check_liquidity,
    check_data_delay,
    check_spread,
    check_market_hours
)
from datetime import datetime, timedelta

# Check for low liquidity
warning = check_liquidity(
    symbol="TEST.NR",
    volume=500,
    avg_volume=10000
)
if warning:
    print(warning.message)

# Check data freshness
old_data = datetime.now() - timedelta(minutes=30)
warning = check_data_delay(old_data)
if warning:
    print(f"⚠️ {warning.message}")

# Check bid-ask spread
warning = check_spread(
    symbol="TEST.NR",
    bid=25.0,
    ask=27.0,
    spread_threshold=0.05  # 5%
)
```

## Provider Architecture

### Fetcher Pattern

All data models follow the OpenBB Fetcher pattern:

```python
class SomeFetcher(Fetcher[QueryParams, list[DataModel]]):
    
    @staticmethod
    def transform_query(params: dict) -> QueryParams:
        """Validate and transform input parameters"""
        pass
    
    @staticmethod
    async def aextract_data(query: QueryParams, credentials: dict | None) -> list[dict]:
        """Fetch raw data from source"""
        pass
    
    @staticmethod
    def transform_data(query: QueryParams, data: list[dict]) -> list[DataModel]:
        """Transform raw data to validated models"""
        pass
```

### Adding New Fetchers

To extend the provider with new data sources:

1. **Create model file** in `openbb_kenya/models/`:

```python
# openbb_kenya/models/my_new_data.py
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.xyz import XYZData, XYZQueryParams

class KenyaMyNewDataFetcher(Fetcher[XYZQueryParams, list[XYZData]]):
    # Implement transform_query, aextract_data, transform_data
    pass
```

2. **Register in provider** (`openbb_kenya/__init__.py`):

```python
from openbb_kenya.models.my_new_data import KenyaMyNewDataFetcher

fetcher_dict = {
    ...
    "XYZ": KenyaMyNewDataFetcher,
}
```

3. **Add tests** in `tests/test_models/`:

```python
# tests/test_models/test_my_new_data.py
def test_query_validation():
    params = KenyaMyNewDataFetcher.transform_query({"symbol": "TEST"})
    assert params.symbol == "TEST"
```

## Troubleshooting

### Import Errors

```
ModuleNotFoundError: No module named 'openbb_core'
```

**Solution**: Install OpenBB Platform first:
```bash
cd /home/ojwang/OpenBB/openbb_platform
python dev_install.py -e
```

### Empty Data Errors

```
EmptyDataError: NSE index data fetching not yet implemented
```

**Solution**: Some fetchers are placeholders awaiting actual NSE/CBK integration. See [Implementation Status](#implementation-status).

### Symbol Format Errors

```
ValueError: Invalid NSE symbol: INVALID_SYMBOL_123
```

**Solution**: Use correct symbol format:
- Equities: 3-4 letter codes (e.g., `SCOM`, `KCB`, `EQTY`)
- Automatically normalized to `.NR` suffix
- Indices: `NSE20`, `NSEASI`, `NSE25`

## Implementation Status

### ✅ Fully Functional
- NSE equity historical (demo with yfinance fallback)
- Regional FX pairs (using yfinance)
- Market calendar and trading hours
- Symbol validation and normalization
- Data quality warnings

### ⚠️ Placeholder (Structure Ready)
- NSE indices (awaiting NSE API/scraping)
- CBK interest rates (awaiting CBK scraping)
- CBK inflation/CPI (awaiting CBK scraping)
- CBK forex rates (awaiting CBK scraping)

### 🔨 Next Steps
1. Implement actual NSE website scraping
2. Implement CBK statistics page scraping
3. Add corporate actions tracking
4. Add news integration
5. Performance optimization and caching

## Development

### Running Tests

```bash
cd /home/ojwang/OpenBB/openbb_platform/providers/openbb_kenya

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models/test_nse_equities.py -v

# Run with coverage
pytest tests/ --cov=openbb_kenya --cov-report=html
```

### Code Quality

```bash
# Format code
black openbb_kenya/

# Lint
ruff check openbb_kenya/

# Type checking
mypy openbb_kenya/
```

## Configuration

### No API Keys Required (Current)

The current implementation uses public data sources and requires no configuration. Future paid providers can be added:

```json
// ~/.openbb_platform/user_settings.json
{
  "credentials": {
    "kenya_api_key": "YOUR_KEY_HERE"
  }
}
```

## Support

- **Documentation**: See [README.md](file:///home/ojwang/OpenBB/openbb_platform/providers/openbb_kenya/README.md)
- **Issues**: OpenBB GitHub Issues
- **Examples**: [examples_usage.py](file:///home/ojwang/OpenBB/openbb_platform/providers/openbb_kenya/examples_usage.py)

## License

AGPLv3 - Same as OpenBB Platform
