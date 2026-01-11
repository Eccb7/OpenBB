"""Data quality and market condition warnings for Kenya markets."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional


class MarketWarning:
    """Structured warning for market conditions."""

    def __init__(
        self,
        warning_type: str,
        message: str,
        severity: str = "info",  # info, warning, critical
        metadata: Optional[Dict] = None,
    ):
        self.type = warning_type
        self.message = message
        self.severity = severity
        self.metadata = metadata or {}

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "type": self.type,
            "message": self.message,
            "severity": self.severity,
            "metadata": self.metadata,
        }


def check_liquidity(
    symbol: str,
    volume: float,
    avg_volume: float | None = None,
    threshold: float = 0.2,
) -> Optional[MarketWarning]:
    """
    Check for thin liquidity warnings.

    Args:
        symbol: Stock symbol
        volume: Current trading volume
        avg_volume: Average daily volume (if available)
        threshold: Warning threshold as fraction of average (default 0.2 = 20%)

    Returns:
        MarketWarning if liquidity is low, else None
    """
    # Absolute low volume threshold (< 1000 shares)
    if volume < 1000:
        return MarketWarning(
            warning_type="low_liquidity",
            message=f"⚠️ Very low trading volume for {symbol}: {volume:,.0f} shares",
            severity="warning",
            metadata={"symbol": symbol, "volume": volume, "threshold": "absolute"},
        )

    # Relative threshold (if average available)
    if avg_volume and volume < (avg_volume * threshold):
        percentage = (volume / avg_volume) * 100
        return MarketWarning(
            warning_type="low_liquidity",
            message=f"⚠️ Low liquidity for {symbol}: {percentage:.1f}% of average volume",
            severity="warning",
            metadata={
                "symbol": symbol,
                "volume": volume,
                "avg_volume": avg_volume,
                "percentage": percentage,
            },
        )

    return None


def check_data_delay(
    timestamp: datetime,
    delay_threshold: int = 15,  # minutes
    timezone: str = "Africa/Nairobi",
) -> Optional[MarketWarning]:
    """
    Check if data is delayed.

    Args:
        timestamp: Data timestamp
        delay_threshold: Minutes of delay before warning (default 15)
        timezone: Market timezone

    Returns:
        MarketWarning if data is delayed, else None
    """
    now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
    delay = now - timestamp

    if delay > timedelta(minutes=delay_threshold):
        delay_minutes = int(delay.total_seconds() / 60)
        return MarketWarning(
            warning_type="data_delay",
            message=f"⏱️ Data delayed by {delay_minutes} minutes",
            severity="info",
            metadata={
                "delay_minutes": delay_minutes,
                "timestamp": timestamp.isoformat(),
                "threshold": delay_threshold,
            },
        )

    return None


def check_spread(
    symbol: str,
    bid: float,
    ask: float,
    spread_threshold: float = 0.05,  # 5%
) -> Optional[MarketWarning]:
    """
    Check for wide bid-ask spreads.

    Args:
        symbol: Stock symbol
        bid: Bid price
        ask: Ask price
        spread_threshold: Warning threshold as fraction (default 0.05 = 5%)

    Returns:
        MarketWarning if spread is wide, else None
    """
    if bid <= 0 or ask <= 0:
        return None

    spread = (ask - bid) / bid
    if spread > spread_threshold:
        spread_pct = spread * 100
        return MarketWarning(
            warning_type="wide_spread",
            message=f"⚠️ Wide bid-ask spread for {symbol}: {spread_pct:.2f}%",
            severity="warning",
            metadata={"symbol": symbol, "bid": bid, "ask": ask, "spread_pct": spread_pct},
        )

    return None


def check_suspension(
    symbol: str,
    suspended_symbols: List[str],
) -> Optional[MarketWarning]:
    """
    Check if stock is suspended from trading.

    Args:
        symbol: Stock symbol to check
        suspended_symbols: List of currently suspended symbols

    Returns:
        MarketWarning if suspended, else None
    """
    if symbol in suspended_symbols:
        return MarketWarning(
            warning_type="trading_suspension",
            message=f"🛑 Trading suspended for {symbol}",
            severity="critical",
            metadata={"symbol": symbol},
        )

    return None


def check_market_hours(
    timestamp: datetime,
    is_trading_day: bool,
    is_market_open: bool,
) -> Optional[MarketWarning]:
    """
    Check if data is from outside market hours.

    Args:
        timestamp: Data timestamp
        is_trading_day: Whether timestamp is on a trading day
        is_market_open: Whether market was open at timestamp

    Returns:
        MarketWarning if outside market hours, else None
    """
    if not is_trading_day:
        return MarketWarning(
            warning_type="non_trading_day",
            message="ℹ️ Market closed - non-trading day",
            severity="info",
            metadata={"timestamp": timestamp.isoformat()},
        )

    if not is_market_open:
        return MarketWarning(
            warning_type="outside_trading_hours",
            message="ℹ️ Outside regular trading hours (09:00-15:00 EAT)",
            severity="info",
            metadata={"timestamp": timestamp.isoformat()},
        )

    return None


def aggregate_warnings(warnings: List[Optional[MarketWarning]]) -> List[Dict]:
    """
    Aggregate and deduplicate warnings.

    Args:
        warnings: List of MarketWarning objects (may contain None)

    Returns:
        List of warning dictionaries (serialized)
    """
    unique_warnings = {}

    for warning in warnings:
        if warning is None:
            continue

        # Use type as key to deduplicate
        unique_warnings[warning.type] = warning

    return [w.to_dict() for w in unique_warnings.values()]


def create_metadata(
    source: str,
    last_updated: datetime,
    is_realtime: bool = False,
    warnings: Optional[List[MarketWarning]] = None,
) -> Dict:
    """
    Create standardized metadata dictionary for responses.

    Args:
        source: Data source name (e.g., "NSE", "CBK")
        last_updated: Timestamp of last data update
        is_realtime: Whether data is real-time or delayed
        warnings: List of warnings

    Returns:
        Metadata dictionary
    """
    return {
        "source": source,
        "last_updated": last_updated.isoformat(),
        "is_realtime": is_realtime,
        "warnings": aggregate_warnings(warnings or []),
    }
