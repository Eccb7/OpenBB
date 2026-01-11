"""NSE Index Historical Price Model.

Provides historical data for NSE indices (NSE 20, NSE All Share, NSE 25).
"""

from datetime import datetime
from typing import Any, Optional, Literal

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_historical import (
    IndexHistoricalData,
    IndexHistoricalQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_kenya.utils import validate_nse_index


class KenyaNSEIndexQueryParams(IndexHistoricalQueryParams):
    """NSE Index Historical Query Parameters."""

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": False,
            "description": "NSE index symbol: NSE20, NSEASI (All Share), or NSE25",
        },
    }

    @field_validator("symbol", mode="before")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate NSE index symbol."""
        return validate_nse_index(v)


class KenyaNSEIndexData(IndexHistoricalData):
    """NSE Index Historical Data."""

    change: Optional[float] = Field(
        default=None,
        description="Index change from previous close",
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Index change from previous close as percentage",
        json_schema_extra={ "x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: Optional[int] = Field(
        default=None,
        description="Total volume traded in index constituents",
    )

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize percent values."""
        if v is None:
            return None
        if abs(v) > 1:
            return v / 100
        return v


class KenyaNSEIndexFetcher(
    Fetcher[
        KenyaNSEIndexQueryParams,
        list[KenyaNSEIndexData],
    ]
):
    """NSE Index Historical Fetcher.

    DEMO IMPLEMENTATION: Uses placeholder data.
    TODO: Implement actual NSE index data fetching.
    """

    # Mapping NSE index symbols to potential Yahoo Finance symbols
    SYMBOL_MAPPING = {
        "NSE20": "^NSE20",  # May not exist on Yahoo
        "NSEASI": "^NSEASI",
        "NSE25": "^NSE25",
    }

    @staticmethod
    def transform_query(params: dict[str, Any]) -> KenyaNSEIndexQueryParams:
        """Transform and validate query parameters."""
        transformed_params = params.copy()

        # Set default date range
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        # Validate symbol
        if "symbol" in transformed_params:
            transformed_params["symbol"] = validate_nse_index(transformed_params["symbol"])

        return KenyaNSEIndexQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: KenyaNSEIndexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract NSE index data.

        DEMO: Returns mock data for demonstration.
        """
        # In production, this would scrape NSE website or use official API
        # For now, return empty to demonstrate error handling
        raise EmptyDataError(
            f"NSE index data fetching not yet implemented for {query.symbol}. "
            "This is a placeholder implementation. "
            "To enable, implement actual NSE website scraping or API integration."
        )

    @staticmethod
    def transform_data(
        query: KenyaNSEIndexQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[KenyaNSEIndexData]:
        """Transform raw index data."""
        if not data:
            raise EmptyDataError(f"No index data available for {query.symbol}")

        index_data = [KenyaNSEIndexData.model_validate(d) for d in data]
        index_data.sort(key=lambda x: x.date)

        return index_data
