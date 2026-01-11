"""Kenya market calendar utilities.

Provides trading calendar, holiday detection, and market hours for NSE.
"""

from datetime import date, datetime, time
from typing import List

# Kenya public holidays (fixed dates)
FIXED_HOLIDAYS = {
    (1, 1): "New Year's Day",
    (5, 1): "Labour Day",
    (6, 1): "Madaraka Day",
    (10, 20): "Mashujaa Day",
    (12, 12): "Jamhuri Day",
    (12, 25): "Christmas Day",
    (12, 26): "Boxing Day",
}

# Moveable holidays (approximate - need actual dates each year)
# In production, these should be loaded from a configuration file or API
MOVEABLE_HOLIDAYS_2024 = [
    date(2024, 3, 29),  # Good Friday
    date(2024, 4, 1),   # Easter Monday
    date(2024, 4, 10),  # Eid al-Fitr
    date(2024, 6, 17),  # Eid al-Adha
]

MOVEABLE_HOLIDAYS_2025 = [
    date(2025, 4, 18),  # Good Friday
    date(2025, 4, 21),  # Easter Monday
    date(2025, 3, 31),  # Eid al-Fitr
    date(2025, 6, 7),   # Eid al-Adha
]

MOVEABLE_HOLIDAYS_2026 = [
    date(2026, 4, 3),   # Good Friday
    date(2026, 4, 6),   # Easter Monday
    date(2026, 3, 20),  # Eid al-Fitr
    date(2026, 5, 27),  # Eid al-Adha
]


class NSECalendar:
    """Nairobi Securities Exchange trading calendar."""

    TRADING_START = time(9, 0, 0)  # 09:00 EAT
    TRADING_END = time(15, 0, 0)   # 15:00 EAT
    TIMEZONE = "Africa/Nairobi"     # EAT (UTC+3)
    SETTLEMENT_DAYS = 3             # T+3

    @staticmethod
    def is_fixed_holiday(check_date: date) -> bool:
        """Check if date is a fixed public holiday."""
        return (check_date.month, check_date.day) in FIXED_HOLIDAYS

    @staticmethod
    def is_moveable_holiday(check_date: date) -> bool:
        """Check if date is a moveable holiday (Easter, Eid, etc.)."""
        year = check_date.year
        moveable_holidays = []

        if year == 2024:
            moveable_holidays = MOVEABLE_HOLIDAYS_2024
        elif year == 2025:
            moveable_holidays = MOVEABLE_HOLIDAYS_2025
        elif year == 2026:
            moveable_holidays = MOVEABLE_HOLIDAYS_2026
        # For other years, conservative approach: assume no moveable holidays known
        # In production, fetch from external calendar API

        return check_date in moveable_holidays

    @classmethod
    def is_holiday(cls, check_date: date) -> bool:
        """Check if date is a public holiday (fixed or moveable)."""
        return cls.is_fixed_holiday(check_date) or cls.is_moveable_holiday(check_date)

    @classmethod
    def is_weekend(cls, check_date: date) -> bool:
        """Check if date is a weekend (Saturday or Sunday)."""
        return check_date.weekday() >= 5  # 5=Saturday, 6=Sunday

    @classmethod
    def is_trading_day(cls, check_date: date) -> bool:
        """Check if date is a trading day (not weekend or holiday)."""
        return not (cls.is_weekend(check_date) or cls.is_holiday(check_date))

    @classmethod
    def get_trading_hours(cls) -> tuple[time, time]:
        """Return NSE trading hours as (start, end) tuple."""
        return (cls.TRADING_START, cls.TRADING_END)

    @classmethod
    def is_market_open(cls, check_datetime: datetime) -> bool:
        """Check if market is open at given datetime."""
        # Check if it's a trading day
        if not cls.is_trading_day(check_datetime.date()):
            return False

        # Check if within trading hours
        current_time = check_datetime.time()
        return cls.TRADING_START <= current_time <= cls.TRADING_END

    @classmethod
    def next_trading_day(cls, from_date: date) -> date:
        """Get next trading day after given date."""
        from datetime import timedelta

        next_day = from_date + timedelta(days=1)
        while not cls.is_trading_day(next_day):
            next_day += timedelta(days=1)
        return next_day

    @classmethod
    def settlement_date(cls, trade_date: date) -> date:
        """Calculate settlement date (T+3 trading days)."""
        current = trade_date
        for _ in range(cls.SETTLEMENT_DAYS):
            current = cls.next_trading_day(current)
        return current

    @classmethod
    def get_holiday_name(cls, check_date: date) -> str | None:
        """Get name of holiday if date is a holiday, else None."""
        # Check fixed holidays
        key = (check_date.month, check_date.day)
        if key in FIXED_HOLIDAYS:
            return FIXED_HOLIDAYS[key]

        # Check moveable holidays
        if cls.is_moveable_holiday(check_date):
            # For production: return actual holiday name from database
            return "Public Holiday"

        return None

    @classmethod
    def trading_days_in_range(cls, start_date: date, end_date: date) -> List[date]:
        """Get list of all trading days in date range (inclusive)."""
        from datetime import timedelta

        trading_days = []
        current = start_date

        while current <= end_date:
            if cls.is_trading_day(current):
                trading_days.append(current)
            current += timedelta(days=1)

        return trading_days
