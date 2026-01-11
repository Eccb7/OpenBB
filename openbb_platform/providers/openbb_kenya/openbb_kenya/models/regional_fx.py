"""Regional East African FX Pairs Model.

Provides forex data for regional East African currency pairs using
existing OpenBB providers (yfinance, fmp) with custom pair mappings.
"""

from datetime import datetime
from typing import Any, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_historical import (
    CurrencyHistoricalData,
    CurrencyHistoricalQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import field_validator

from openbb_kenya.utils import validate_fx_pair


class KenyaRegionalFXQueryParams(CurrencyHistoricalQueryParams):
    """Regional East African FX Query Parameters."""

    @field_validator("symbol", mode="before")
    @classmethod
    def validate_pair(cls, v: str) -> str:
        """Validate FX pair."""
        return validate_fx_pair(v)


class KenyaRegionalFXData(CurrencyHistoricalData):
    """Regional East African FX Data."""
    pass


class KenyaRegionalFXFetcher(
    Fetcher[
        KenyaRegionalFXQueryParams,
        list[KenyaRegionalFXData],
    ]
):
    """Regional East African FX Fetcher.

    Leverages existing providers (yfinance) for regional FX pairs.
    Supports: KES/USD, KES/EUR, KES/GBP, KES/UGX, KES/TZS
    """

    @staticmethod
    def transform_query(params: dict[str, Any]) -> KenyaRegionalFXQueryParams:
        """Transform query parameters."""
        transformed_params = params.copy()

        # Default date range
        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(months=6)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return KenyaRegionalFXQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: KenyaRegionalFXQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract regional FX data using yfinance.

        DEMO IMPLEMENTATION: Uses yfinance as data source.
        """
        # pylint: disable=import-outside-toplevel
        import yfinance as yf

        # Map KES pairs to Yahoo Finance symbols
        pair_mapping = {
            "KESUSD": "KES=X",
            "KESEUR": "KESEUR=X",
            "KESGBP": "KESGBP=X",
            "KESUGX": "KESUGX=X",
            "KESTZS": "KESTZS=X",
        }

        yf_symbol = pair_mapping.get(query.symbol)
        if not yf_symbol:
            # Try direct symbol
            yf_symbol = f"{query.symbol}=X"

        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(
                start=query.start_date,
                end=query.end_date,
                interval="1d",
            )

            if df.empty:
                return []

            df = df.reset_index()
            df.columns = df.columns.str.lower()
            df["symbol"] = query.symbol

            return df.to_dict("records")

        except Exception as e:
            print(f"Error fetching FX data for {query.symbol}: {str(e)}")
            return []

    @staticmethod
    def transform_data(
        query: KenyaRegionalFXQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[KenyaRegionalFXData]:
        """Transform regional FX data."""
        if not data:
            raise EmptyDataError(
                f"No regional FX data available for {query.symbol}. "
                "This pair may not be available from the data provider."
            )

        fx_data = [KenyaRegionalFXData.model_validate(d) for d in data]
        fx_data.sort(key=lambda x: x.date)

        return fx_data
