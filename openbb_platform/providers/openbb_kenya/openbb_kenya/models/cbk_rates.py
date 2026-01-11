"""CBK Interest Rates Model.

Provides Central Bank of Kenya interest rates including CBR, T-Bill rates, and interbank rates.
"""

from datetime import datetime, date
from typing import Any, Optional, Literal

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.treasury_rates import (
    TreasuryRatesData,
    TreasuryRatesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class KenyaCBKRatesQueryParams(TreasuryRatesQueryParams):
    """CBK Interest Rates Query Parameters."""

    rate_type: Optional[Literal["cbr", "tbill_91", "tbill_182", "tbill_364", "interbank"]] = Field(
        default=None,
        description="Type of interest rate to fetch (None for all)",
    )


class KenyaCBKRatesData(TreasuryRatesData):
    """CBK Interest Rates Data."""

    rate_type: Optional[str] = Field(
        default=None,
        description="Type of rate (CBR, T-Bill 91, etc.)",
    )
    maturity_days: Optional[int] = Field(
        default=None,
        description="Maturity period in days (for T-Bills)",
    )


class KenyaCBKRatesFetcher(
    Fetcher[
        KenyaCBKRatesQueryParams,
        list[KenyaCBKRatesData],
    ]
):
    """CBK Interest Rates Fetcher.

    DEMO IMPLEMENTATION: Placeholder for CBK rates.
    TODO: Implement actual CBK website scraping.
    """

    @staticmethod
    def transform_query(params: dict[str, Any]) -> KenyaCBKRatesQueryParams:
        """Transform query parameters."""
        transformed_params = params.copy()

        # Default date range
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(months=6)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return KenyaCBKRatesQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: KenyaCBKRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract CBK rates data.

        TODO: Implement CBK website scraping.
        """
        raise EmptyDataError(
            "CBK rates fetching not yet implemented. "
            "This requires scraping the Central Bank of Kenya website."
        )

    @staticmethod
    def transform_data(
        query: KenyaCBKRatesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[KenyaCBKRatesData]:
        """Transform CBK rates data."""
        if not data:
            raise EmptyDataError("No CBK rates data available")

        rates_data = [KenyaCBKRatesData.model_validate(d) for d in data]
        rates_data.sort(key=lambda x: x.date)

        return rates_data
