"""Tests for NSE equity historical fetcher."""

import pytest
from datetime import date, datetime
from openbb_kenya.models.nse_equities import (
    KenyaNSEEquityFetcher,
    KenyaNSEEquityQueryParams,
    KenyaNSEEquityData,
)


class TestNSEEquityFetcher:
    """Test NSE equity historical data fetcher."""

    def test_query_params_validation(self):
        """Test query parameter validation and symbol normalization."""
        # Test symbol normalization
        params = KenyaNSEEquityFetcher.transform_query({"symbol": "SCOM"})
        assert params.symbol == "SCOM.NR"

        params = KenyaNSEEquityFetcher.transform_query({"symbol": "SCOM.NR"})
        assert params.symbol == "SCOM.NR"

    def test_query_params_invalid_symbol(self):
        """Test that invalid symbols raise ValueError."""
        with pytest.raises(ValueError, match="Invalid NSE symbol"):
            KenyaNSEEquityFetcher.transform_query({"symbol": "INVALID_SYMBOL_123"})

    def test_query_params_default_dates(self):
        """Test that default date range is set correctly."""
        params = KenyaNSEEquityFetcher.transform_query({"symbol": "SCOM"})

        assert params.start_date is not None
        assert params.end_date is not None
        assert params.start_date < params.end_date
        
        # Should default to ~1 year range
        days_diff = (params.end_date - params.start_date).days
        assert 350 < days_diff < 380  # Approximately 1 year

    def test_equity_data_model(self, mock_nse_equity_response):
        """Test equity data model validation."""
        record = mock_nse_equity_response[0]
        data = KenyaNSEEquityData.model_validate(record)

        assert data.open == 25.50
        assert data.high == 26.00
        assert data.low == 25.20
        assert data.close == 25.80
        assert data.volume == 150000
        assert data.trades_count == 45
        assert data.turnover == 3870000.0


    def test_equity_data_percent_normalization(self):
        """Test percentage normalization."""
        # Test percent already in decimal form
        data = KenyaNSEEquityData.model_validate({
            "date": "2024-01-02",
            "open": 25.0,
            "high": 26.0,
            "low": 24.0,
            "close": 25.5,
            "volume": 1000,
            "change_percent": 0.02,  # 2% in decimal
        })
        assert data.change_percent == 0.02

        # Test percent in percentage form (> 1)
        data = KenyaNSEEquityData.model_validate({
            "date": "2024-01-02",
            "open": 25.0,
            "high": 26.0,
            "low": 24.0,
            "close": 25.5,
            "volume": 1000,
            "change_percent": 2.0,  # 2% as percentage
        })
        assert data.change_percent == 0.02


class TestNSESymbolValidation:
    """Test NSE symbol validation utility."""

    def test_valid_symbols(self):
        """Test valid NSE symbols."""
        from openbb_kenya.utils import validate_nse_symbol

        assert validate_nse_symbol("SCOM") == "SCOM.NR"
        assert validate_nse_symbol("KCB") == "KCB.NR"
        assert validate_nse_symbol("EQTY") == "EQTY.NR"
        assert validate_nse_symbol("scom") == "SCOM.NR"  # lowercase
        assert validate_nse_symbol("SCOM.NR") == "SCOM.NR"  # already has suffix

    def test_invalid_symbols(self):
        """Test invalid NSE symbols."""
        from openbb_kenya.utils import validate_nse_symbol

        with pytest.raises(ValueError):
            validate_nse_symbol("A")  # Too short

        with pytest.raises(ValueError):
            validate_nse_symbol("ABCDE")  # Too long

        with pytest.raises(ValueError):
            validate_nse_symbol("123")  # Numbers

        with pytest.raises(ValueError):
            validate_nse_symbol("AB-CD")  # Special characters
