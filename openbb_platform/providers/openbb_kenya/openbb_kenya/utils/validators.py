"""Data validation utilities for Kenya markets."""

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import ValidationError


def validate_nse_symbol(symbol: str) -> str:
    """
    Validate and normalize NSE stock symbol.

    Args:
        symbol: Stock symbol (e.g., "SCOM", "SCOM.NR")

    Returns:
        Normalized symbol with .NR suffix

    Raises:
        ValueError: If symbol format is invalid
    """
    symbol = symbol.strip().upper()

    # Remove .NR suffix if present
    if symbol.endswith(".NR"):
        symbol = symbol[:-3]

    # Validate format (3-4 letter code)
    if not re.match(r"^[A-Z]{3,4}$", symbol):
        raise ValueError(
            f"Invalid NSE symbol: {symbol}. Expected 3-4 letter code (e.g., 'SCOM', 'KCB')"
        )

    # Add .NR suffix
    return f"{symbol}.NR"


def validate_nse_index(index_symbol: str) -> str:
    """
    Validate NSE index symbol.

    Args:
        index_symbol: Index symbol

    Returns:
        Normalized index symbol

    Raises:
        ValueError: If index symbol is invalid
    """
    index_symbol = index_symbol.strip().upper()

    valid_indices = ["NSE20", "NSEASI", "NSE25"]
    if index_symbol not in valid_indices:
        raise ValueError(
            f"Invalid NSE index: {index_symbol}. "
            f"Valid indices: {', '.join(valid_indices)}"
        )

    return index_symbol


def validate_date_range(
    start_date: Optional[date],
    end_date: Optional[date],
    max_years: int = 10,
) -> tuple[date, date]:
    """
    Validate and normalize date range.

    Args:
        start_date: Start date (None for default)
        end_date: End date (None for today)
        max_years: Maximum allowed range in years

    Returns:
        Tuple of (start_date, end_date)

    Raises:
        ValueError: If date range is invalid
    """
    from datetime import timedelta

    today = date.today()

    # Set defaults
    if end_date is None:
        end_date = today
    if start_date is None:
        start_date = end_date - timedelta(days=365)  # 1 year default

    # Validate order
    if start_date > end_date:
        raise ValueError(f"start_date ({start_date}) must be before end_date ({end_date})")

    # Validate future dates
    if end_date > today:
        raise ValueError(f"end_date ({end_date}) cannot be in the future")

    # Validate range
    days_diff = (end_date - start_date).days
    max_days = max_years * 365

    if days_diff > max_days:
        raise ValueError(
            f"Date range too large: {days_diff} days. Maximum allowed: {max_days} days ({max_years} years)"
        )

    return start_date, end_date


def validate_fx_pair(pair: str) -> str:
    """
    Validate and normalize FX pair symbol.

    Args:
        pair: FX pair (e.g., "KESUSD", "KES/USD", "USD/KES")

    Returns:
        Normalized pair in format "KESUSD"

    Raises:
        ValueError: If pair format is invalid
    """
    pair = pair.strip().upper().replace("/", "").replace("-", "")

    # Ensure KES is in the pair
    if "KES" not in pair:
        raise ValueError(f"Invalid FX pair: {pair}. Must include KES")

    # Validate 6-character format
    if len(pair) != 6:
        raise ValueError(f"Invalid FX pair: {pair}. Expected format: KESUSD, KESEUR, etc.")

    # Common valid pairs
    valid_pairs = ["KESUSD", "KESEUR", "KESGBP", "KESUGX", "KESTZS", "KESRWF"]

    if pair not in valid_pairs:
        # Allow it but warn in metadata
        pass

    return pair


def validate_price_data(data: Dict[str, Any]) -> bool:
    """
    Validate price data structure.

    Args:
        data: Dictionary containing price data

    Returns:
        True if valid

    Raises:
        ValueError: If data structure is invalid
    """
    required_fields = ["date", "open", "high", "low", "close", "volume"]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    # Validate OHLC relationship
    if not (data["low"] <= data["open"] <= data["high"]):
        raise ValueError(f"Invalid OHLC: open ({data['open']}) outside low-high range")

    if not (data["low"] <= data["close"] <= data["high"]):
        raise ValueError(f"Invalid OHLC: close ({data['close']}) outside low-high range")

    if data["low"] > data["high"]:
        raise ValueError(f"Invalid OHLC: low ({data['low']}) > high ({data['high']})")

    # Validate non-negative volume
    if data["volume"] < 0:
        raise ValueError(f"Invalid volume: {data['volume']} (must be non-negative)")

    return True


def clean_numeric_value(value: Any) -> Optional[float]:
    """
    Clean and convert numeric value from scraped data.

    Args:
        value: Value to clean (may be string with commas, etc.)

    Returns:
        Float value or None if invalid
    """
    if value is None or value == "":
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        # Remove commas, spaces, currency symbols
        cleaned = value.strip().replace(",", "").replace(" ", "")
        cleaned = re.sub(r"[^\d.-]", "", cleaned)

        try:
            return float(cleaned)
        except ValueError:
            return None

    return None


def clean_date_value(value: Any, fmt: str = "%Y-%m-%d") -> Optional[date]:
    """
    Clean and convert date value.

    Args:
        value: Date value (string or date object)
        fmt: Expected date format for strings

    Returns:
        date object or None if invalid
    """
    if value is None:
        return None

    if isinstance(value, date):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            # Try alternative formats
            for alt_fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(value.strip(), alt_fmt).date()
                except ValueError:
                    continue

    return None
