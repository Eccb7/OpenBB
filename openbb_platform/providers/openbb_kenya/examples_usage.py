"""Example usage of Kenya provider for OpenBB Platform.

This script demonstrates how to use the Kenya markets provider
to fetch NSE and CBK data.
"""

from datetime import date, datetime, timedelta


def example_nse_equity():
    """Example: Fetch NSE equity historical data."""
    from openbb import obb

    # Fetch Safaricom historical data
    print("\\n=== NSE Equity: Safaricom (SCOM.NR) ===")
    
    result = obb.equity.price.historical(
        symbol="SCOM.NR",  # Can also use just "SCOM"
        provider="kenya",
        start_date=date.today() - timedelta(days=365),
        end_date=date.today(),
    )
    
    df = result.to_dataframe()
    print(df.tail())
    print(f"\\nTotal records: {len(df)}")
    print(f"Average volume: {df['volume'].mean():,.0f}")


def example_nse_index():
    """Example: Fetch NSE 20 Index data."""
    from openbb import obb

    print("\\n=== NSE 20 Index ===")
    
    result = obb.index.price.historical(
        symbol="NSE20",
        provider="kenya",
        start_date=date.today() - timedelta(days=90),
    )
    
    df = result.to_dataframe()
    print(df.tail())


def example_cbk_rates():
    """Example: Fetch CBK interest rates."""
    from openbb import obb

    print("\\n=== CBK Interest Rates ===")
    
    result = obb.fixedincome.government.treasury_rates(
        country="kenya",
        provider="kenya",
    )
    
    df = result.to_dataframe()
    print(df.tail())


def example_multiple_symbols():
    """Example: Compare multiple NSE stocks."""
    from openbb import obb
    import matplotlib.pyplot as plt

    print("\\n=== Comparing Multiple Stocks ===")
    
    symbols = ["SCOM", "KCB", "EQTY"]
    start = date.today() - timedelta(days=180)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for symbol in symbols:
        result = obb.equity.price.historical(
            symbol=symbol,
            provider="kenya",
            start_date=start,
        )
        df = result.to_dataframe()
        
        # Normalize to starting price (index to 100)
        normalized = (df['close'] / df['close'].iloc[0]) * 100
        ax.plot(df['date'], normalized, label=symbol)
    
    ax.set_title("NSE Stock Performance (Indexed to 100)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Indexed Price")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("nse_comparison.png")
    print("Chart saved to nse_comparison.png")


def example_calendar_usage():
    """Example: Using Kenya market calendar."""
    from openbb_kenya.utils import NSECalendar
    
    print("\\n=== Kenya Market Calendar ===")
    
    today = date.today()
    
    # Check if today is a trading day
    is_trading = NSECalendar.is_trading_day(today)
    print(f"Today ({today}) is a trading day: {is_trading}")
    
    # Get trading hours
    start, end = NSECalendar.get_trading_hours()
    print(f"Trading hours: {start} - {end} EAT")
    
    # Next trading day
    next_day = NSECalendar.next_trading_day(today)
    print(f"Next trading day: {next_day}")
    
    # Settlement date for today's trade
    settlement = NSECalendar.settlement_date(today)
    print(f"Settlement date (T+3): {settlement}")


def example_data_validation():
    """Example: Using data validators."""
    from openbb_kenya.utils import (
        validate_nse_symbol,
        validate_nse_index,
        validate_date_range,
    )
    
    print("\\n=== Data Validation Examples ===")
    
    # Symbol validation
    symbols = ["SCOM", "kcb", "EQTY.NR", "invalid123"]
    
    for sym in symbols:
        try:
            normalized = validate_nse_symbol(sym)
            print(f"✓ {sym:15} → {normalized}")
        except ValueError as e:
            print(f"✗ {sym:15} → Invalid: {e}")
    
    # Index validation
    indices = ["NSE20", "NSEASI", "INVALID"]
    
    for idx in indices:
        try:
            normalized = validate_nse_index(idx)
            print(f"✓ {idx:15} → {normalized}")
        except ValueError as e:
            print(f"✗ {idx:15} → Invalid: {e}")


def example_warnings():
    """Example: Data quality warnings."""
    from openbb_kenya.utils import (
        check_liquidity,
        check_data_delay,
        check_spread,
    )
    
    print("\\n=== Data Quality Warnings ===")
    
    # Low liquidity warning
    warning = check_liquidity("TEST.NR", volume=500, avg_volume=10000)
    if warning:
        print(f"⚠️  {warning.message}")
    
    # Data delay warning
    old_timestamp = datetime.now() - timedelta(minutes=30)
    warning = check_data_delay(old_timestamp)
    if warning:
        print(f"⏱️  {warning.message}")
    
    # Wide spread warning
    warning = check_spread("TEST.NR", bid=25.0, ask=27.0)
    if warning:
        print(f"⚠️  {warning.message}")


if __name__ == "__main__":
    print("=" * 60)
    print("Kenya Markets Provider - Usage Examples")
    print("=" * 60)
    
    # Note: These examples require OpenBB Platform to be installed
    # and the Kenya provider to be registered
    
    # Uncomment the examples you want to run:
    
    # example_nse_equity()
    # example_nse_index()
    # example_cbk_rates()
    # example_multiple_symbols()
    
    example_calendar_usage()
    example_data_validation()
    example_warnings()
    
    print("\\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)
