"""Test configuration for Kenya provider."""

import pytest


@pytest.fixture(scope="session")
def credentials():
    """Return empty credentials for public data sources."""
    return {}


@pytest.fixture
def mock_nse_equity_response():
    """Mock NSE equity historical response."""
    return [
        {
            "date": "2024-01-02",
            "symbol": "SCOM.NR",
            "open": 25.50,
            "high": 26.00,
            "low": 25.20,
            "close": 25.80,
            "volume": 150000,
            "trades_count": 45,
            "turnover": 3870000.0,
        },
        {
            "date": "2024-01-03",
            "symbol": "SCOM.NR",
            "open": 25.80,
            "high": 26.50,
            "low": 25.60,
            "close": 26.20,
            "volume": 200000,
            "trades_count": 62,
            "turnover": 5240000.0,
        },
    ]
