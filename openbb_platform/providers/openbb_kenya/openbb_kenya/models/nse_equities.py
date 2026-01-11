"""NSE Equity Historical Price Model.

Provides historical OHLCV data for equities listed on the Nairobi Securities Exchange.
"""

from datetime import datetime
from typing import Any, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_kenya.utils import validate_nse_symbol, validate_date_range, NSECalendar
from openbb_kenya.utils.warnings import check_liquidity, check_data_delay, create_metadata


class KenyaNSEEquityQueryParams(EquityHistoricalQueryParams):
    """NSE Equity Historical Price Query Parameters.

    Extended from standard EquityHistoricalQueryParams with NSE-specific validation.
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": False,
            "description": "NSE stock symbol (e.g., 'SCOM.NR', 'KCB.NR')",
        },
    }

    @field_validator("symbol", mode="before")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate and normalize NSE symbol."""
        return validate_nse_symbol(v)


class KenyaNSEEquityData(EquityHistoricalData):
    """NSE Equity Historical Price Data.

    Extends standard EquityHistoricalData with NSE-specific fields.
    """

    trades_count: Optional[int] = Field(
        default=None,
        description="Number of trades executed during the period",
    )
    turnover: Optional[float] = Field(
        default=None,
        description="Total turnover (value traded) in KES",
    )
    change: Optional[float] = Field(
        default=None,
        description="Price change from previous close",
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Price change from previous close as percentage",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent values."""
        if v is None:
            return None
        # If value is already in decimal form (0.05 for 5%), return as-is
        # If value is in percentage form (5.0 for 5%), convert to decimal
        # Heuristic: values > 1 are likely percentages
        if abs(v) > 1:
            return v / 100
        return v


class KenyaNSEEquityFetcher(
    Fetcher[
        KenyaNSEEquityQueryParams,
        list[KenyaNSEEquityData],
    ]
):
    """NSE Equity Historical Price Fetcher.

    Note: This is currently a DEMO implementation using yfinance as fallback.
    For production, this should be replaced with actual NSE API or approved scraping.
    """

    @staticmethod
    def transform_query(params: dict[str, Any]) -> KenyaNSEEquityQueryParams:
        """Transform and validate query parameters."""
        transformed_params = params.copy()

        # Set default date range if not provided (1 year)
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        # Validate symbol format
        if "symbol" in transformed_params:
            transformed_params["symbol"] = validate_nse_symbol(transformed_params["symbol"])

        return KenyaNSEEquityQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: KenyaNSEEquityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract raw data from NSE source.

        DEMO IMPLEMENTATION: Uses yfinance as placeholder.
        TODO: Replace with actual NSE API/scraping when available.
        """
        # pylint: disable=import-outside-toplevel
        import yfinance as yf
        import pandas as pd

        # Convert NSE symbol to format yfinance might understand
        # NSE stocks on Yahoo might be listed as SYMBOL.NR
        symbol = query.symbol

        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=query.start_date,
                end=query.end_date,
                interval=getattr(query, "interval", "1d"),
            )

            if df.empty:
                # Try without .NR suffix
                base_symbol = symbol.replace(".NR", "")
                ticker = yf.Ticker(f"{base_symbol}.NR")
                df = ticker.history(
                    start=query.start_date,
                    end=query.end_date,
                    interval=getattr(query, "interval", "1d"),
                )

            if df.empty:
                # Return empty list - will be caught in transform_data
                return []

            # Convert to list of dictionaries
            df = df.reset_index()
            df["symbol"] = query.symbol
            df.columns = df.columns.str.lower()

            # Rename yfinance columns to our schema
            df = df.rename(
                columns={
                    "date": "date",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "volume": "volume",
                }
            )

            # Add NSE-specific mock data (in production, this comes from NSE)
            df["trades_count"] = None
            df["turnover"] = df["volume"] * df["close"]  # Approximate turnover
            df["change"] = df["close"].diff()
            df["change_percent"] = df["close"].pct_change()

            # Convert to dict
            data = df.to_dict("records")

            return data

        except Exception as e:
            # Log error and return empty (will trigger EmptyDataError)
            print(f"Error fetching data for {symbol}: {str(e)}")
            return []

    @staticmethod
    def transform_data(
        query: KenyaNSEEquityQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[KenyaNSEEquityData]:
        """Transform raw data into NSE equity data model.

        Also performs data quality checks and adds warnings.
        """
        if not data:
            raise EmptyDataError(
                f"No data available for {query.symbol} "
                f"from {query.start_date} to {query.end_date}. "
                "This symbol may not be available or the date range may be invalid."
            )

        # Transform to KenyaNSEEquityData objects
        equity_data = []

        for record in data:
            # Convert date if necessary
            if isinstance(record.get("date"), str):
                record["date"] = datetime.fromisoformat(record["date"]).date()
            elif hasattr(record.get("date"), "date"):
                record["date"] = record["date"].date()

            # Validate and create data object
            try:
                equity_data.append(KenyaNSEEquityData.model_validate(record))
            except Exception as e:
                # Skip invalid records
                print(f"Warning: Skipping invalid record: {str(e)}")
                continue

        # Sort by date
        equity_data.sort(key=lambda x: x.date)

        # Add metadata warnings (if supported by OpenBB - this is a demo)
        # In production, warnings would be attached to the response metadata
        if equity_data:
            # Check for low liquidity
            avg_volume = sum(d.volume for d in equity_data if d.volume) / len(equity_data)
            for data_point in equity_data:
                if data_point.volume and data_point.volume < avg_volume * 0.2:
                    # Low liquidity warning
                    pass

        return equity_data
