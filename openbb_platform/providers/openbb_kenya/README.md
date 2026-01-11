# Kenya Markets Provider for OpenBB

[![OpenBB](https://img.shields.io/badge/OpenBB-Platform-blue)](https://openbb.co)

## Overview

The Kenya Markets Provider extends OpenBB Terminal with comprehensive coverage of Kenyan and East African financial markets. This provider delivers institutional-grade data for the Nairobi Securities Exchange (NSE), Central Bank of Kenya (CBK), and regional markets.

## Features

### Nairobi Securities Exchange (NSE)
- **Equities**: Historical and real-time price data for all NSE-listed stocks
- **Indices**: NSE 20, NSE All Share Index, NSE 25
- **Bonds**: Treasury and corporate bond data
- **Corporate Actions**: Dividends, splits, rights issues, suspensions

### Central Bank of Kenya (CBK)
- **Interest Rates**: Central Bank Rate (CBR), interbank rates, T-Bill rates
- **Inflation**: CPI data (headline, food, core)
- **Forex**: Official KES exchange rates (KES/USD, KES/EUR, KES/GBP)
- **Monetary Policy**: Policy statements and releases

### Regional Markets
- **East African FX**: KES/UGX, KES/TZS, KES/RWF pairs
- **Macroeconomic Data**: KNBS indicators where available

### Market Intelligence
- **Trading Calendar**: Kenya public holidays and NSE trading hours
- **Liquidity Warnings**: Alerts for thinly-traded securities
- **Data Quality Labels**: Clear indication of delayed vs. real-time data
- **Corporate Actions Tracking**: Upcoming dividends and corporate events

## Installation

```bash
# From the openbb_platform directory
cd openbb_platform/providers/openbb_kenya
pip install -e .
```

Or install directly:

```bash
pip install openbb-kenya
```

## Usage

```python
from openbb import obb

# NSE Equity Data
equity_data = obb.equity.price.historical(
    symbol="SCOM.NR",  # Safaricom
    provider="kenya",
    start_date="2023-01-01",
    end_date="2024-01-01"
)
df = equity_data.to_dataframe()

# NSE Index Data
nse20 = obb.index.price.historical(
    symbol="NSE20",
    provider="kenya"
)

# CBK Rates
cbr = obb.fixedincome.government.treasury_rates(
    country="kenya",
    provider="kenya"
)

# Forex Rates
forex = obb.currency.price.historical(
    pair="KESUSD",
    provider="kenya"
)
```

## Symbol Conventions

- **NSE Equities**: `{TICKER}.NR` (e.g., `SCOM.NR`, `EQTY.NR`, `KCB.NR`)
- **NSE Indices**: `NSE20`, `NSEASI`, `NSE25`
- **FX Pairs**: `KESUSD`, `KESEUR`, `KESUGX`
- **Bonds**: ISIN codes (e.g., `KE0001234567`)

## Market Hours

- **Trading**: Monday-Friday, 09:00-15:00 EAT (UTC+3)
- **Settlement**: T+3
- **Holidays**: Kenya public holidays (automatically handled)

## Data Sources

- **NSE Data**: Public NSE website (delayed 15+ minutes for free tier)
- **CBK Data**: Central Bank of Kenya official statistics
- **Regional FX**: Multiple sources including Yahoo Finance
- **Macro Data**: Kenya National Bureau of Statistics (KNBS)

## Disclaimers

⚠️ **Data Accuracy**: This provider uses publicly available data sources. No guarantees are made regarding data accuracy or completeness.

⚠️ **Delays**: Free-tier data may be delayed by 15+ minutes. Real-time data requires premium subscriptions.

⚠️ **Regulatory Compliance**: This tool is for informational purposes only. Investment recommendations require CMA licensing in Kenya.

⚠️ **Liquidity**: Many NSE securities have low trading volumes. Exercise caution with thinly-traded stocks.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
ruff check .
black .
mypy openbb_kenya/
```

## Contributing

Contributions welcome! Please see the [OpenBB Contributing Guide](https://docs.openbb.co/python/developer).

## License

AGPLv3 - Same as OpenBB Platform

## Support

- **Documentation**: [docs.openbb.co](https://docs.openbb.co)
- **Issues**: [GitHub Issues](https://github.com/OpenBB-finance/OpenBB/issues)
- **Discord**: [OpenBB Discord](https://openbb.co/discord)

## Roadmap

- [ ] NSE real-time data integration (pending API access)
- [ ] Bond market depth
- [ ] Options and derivatives (when NSE launches)
- [ ] Expanded KNBS macroeconomic data
- [ ] Tanzania and Uganda exchange integration
- [ ] AI-powered market commentary
