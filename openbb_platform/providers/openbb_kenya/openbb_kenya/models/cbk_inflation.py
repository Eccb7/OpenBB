"""CBK Inflation Data Model.

Provides Consumer Price Index (CPI) and inflation data from Central Bank of Kenya.
"""

from datetime import datetime, date
from typing import Any, Optional, Literal

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cpi import (
    ConsumerPriceIndexData,
    ConsumerPriceIndexQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class KenyaCBKInflationQueryParams(ConsumerPriceIndexQueryParams):
    """CBK Inflation Data Query Parameters."""

    cpi_type: Optional[Literal["headline", "food", "core", "all"]] = Field(
        default="headline",
        description="Type of CPI to fetch (headline, food, core, or all)",
    )


class KenyaCBKInflationData(ConsumerPriceIndexData):
    """CBK Inflation Data."""

    headline_cpi: Optional[float] = Field(
        default=None,
        description="Headline Consumer Price Index",
    )
    food_cpi: Optional[float] = Field(
        default=None,
        description="Food & Beverages CPI component",
    )
    core_cpi: Optional[float] = Field(
        default=None,
        description="Core CPI (excluding food and energy)",
    )
    yoy_change: Optional[float] = Field(
        default=None,
        description="Year-over-year inflation rate",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    mom_change: Optional[float] = Field(
        default=None,
        description="Month-over-month change",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class KenyaCBKInflationFetcher(
    Fetcher[
        KenyaCBKInflationQueryParams,
        list[KenyaCBKInflationData],
    ]
):
    """CBK Inflation Data Fetcher.

    TODO: Implement actual CBK website scraping for CPI data.
    Source: https://www.centralbank.go.ke/statistics/inflation-rates/
    """

    @staticmethod
    def transform_query(params: dict[str, Any]) -> KenyaCBKInflationQueryParams:
        """Transform query parameters."""
        transformed_params = params.copy()

        # Default to last 2 years of monthly data
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=2)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return KenyaCBKInflationQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: KenyaCBKInflationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract CBK inflation data.

        TODO: Implement CBK inflation scraping.
        The CBK publishes monthly CPI data on their statistics page.
        """
        raise EmptyDataError(
            "CBK inflation data fetching not yet implemented. "
            "This requires scraping the Central Bank of Kenya statistics page."
        )

    @staticmethod
    def transform_data(
        query: KenyaCBKInflationQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[KenyaCBKInflationData]:
        """Transform CBK inflation data."""
        if not data:
            raise EmptyDataError("No CBK inflation data available")

        inflation_data = [KenyaCBKInflationData.model_validate(d) for d in data]
        inflation_data.sort(key=lambda x: x.date)

        return inflation_data
