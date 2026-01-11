"""CBK Forex Rates Model.

Provides official Central Bank of Kenya foreign exchange rates.
"""

from datetime import datetime, date
from typing import Any, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_kenya.utils import validate_fx_pair


class KenyaCBKForexQueryParams(CurrencyHistoricalQueryParams):
    """CBK Forex Rates Query Parameters.

    Official CBK exchange rates for KES against major currencies.
    """

    __json_schema_extra__ = {
        "symbol": {
            "description": "FX pair with KES (e.g., KESUSD, KESEUR, KESGBP)",
        },
    }

    @field_validator("symbol", mode="before")
    @classmethod
    def validate_pair(cls, v: str) -> str:
        """Validate FX pair format."""
        return validate_fx_pair(v)


class KenyaCBKForexData(CurrencyHistoricalData):
    """CBK Forex Rates Data."""

    buying_rate: Optional[float] = Field(
        default=None,
        description="CBK buying rate",
    )
    selling_rate: Optional[float] = Field(
        default=None,
        description="CBK selling rate",
    )
    mean_rate: Optional[float] = Field(
        default=None,
        description="Mean rate (average of buying and selling)",
    )


class KenyaCBKForexFetcher(
    Fetcher[
        KenyaCBKForexQueryParams,
        list[KenyaCBKForexData],
    ]
):
    """CBK Forex Rates Fetcher.

    Fetches official CBK exchange rates.
    Source: https://www.centralbank.go.ke/rates/forex-exchange-rates/
    """

    # Supported currency pairs
    SUPPORTED_PAIRS = {
        "KESUSD": "USD",
        "KESEUR": "EUR",
        "KESGBP": "GBP",
        "KESJPY": "JPY",
        "KESAUD": "AUD",
        "KESCAD": "CAD",
        "KESCHF": "CHF",
        "KESUGX": "UGX",  # Ugandan Shilling
        "KESTZS": "TZS",  # Tanzanian Shilling
    }

    @staticmethod
    def transform_query(params: dict[str, Any]) -> KenyaCBKForexQueryParams:
        """Transform query parameters."""
        transformed_params = params.copy()

        # Default date range
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(months=3)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        # Validate pair
        if "symbol" in transformed_params:
            transformed_params["symbol"] = validate_fx_pair(transformed_params["symbol"])

        return KenyaCBKForexQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: KenyaCBKForexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract CBK forex rates data.

        TODO: Implement CBK forex scraping.
        The CBK publishes daily exchange rates on their website.
        """
        # Check if pair is supported
        if query.symbol not in KenyaCBKForexFetcher.SUPPORTED_PAIRS:
            raise EmptyDataError(
                f"Currency pair {query.symbol} not supported by CBK. "
                f"Supported pairs: {', '.join(KenyaCBKForexFetcher.SUPPORTED_PAIRS.keys())}"
            )

        raise EmptyDataError(
            f"CBK forex data fetching not yet implemented for {query.symbol}. "
            "This requires scraping the Central Bank of Kenya forex rates page."
        )

    @staticmethod
    def transform_data(
        query: KenyaCBKForexQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[KenyaCBKForexData]:
        """Transform CBK forex data."""
        if not data:
            raise EmptyDataError(f"No CBK forex data available for {query.symbol}")

        forex_data = [KenyaCBKForexData.model_validate(d) for d in data]
        forex_data.sort(key=lambda x: x.date)

        return forex_data
