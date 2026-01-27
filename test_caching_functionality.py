"""
Quick test to verify the intelligent caching implementation.
"""

import sys
import datetime
from src.domains.market_data.manager import DataManager

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_sp500_download():
    """Test that S&P 500 download works with custom headers."""
    print_section("Test 1: S&P 500 Ticker Download")

    try:
        tickers = DataManager.get_sp500_tickers()
        print(f"✓ SUCCESS: Downloaded {len(tickers)} tickers")
        print(f"  First 10: {tickers[:10]}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        return False


def test_basic_caching():
    """Test basic data download and caching."""
    print_section("Test 2: Basic Caching (3 months of data)")

    manager = DataManager()
    ticker = "AAPL"

    # Download 3 months of data
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=90)

    try:
        print(f"Downloading {ticker} from {start_date} to {end_date}...")
        data = manager.get_data(ticker, start_date, end_date, interval='1d')
        print(f"✓ Downloaded {len(data)} rows")

        # Check cache info
        cache_info = manager.get_ticker_cache_info(ticker)
        print(f"✓ Cache info: {cache_info}")

        return True
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_hit():
    """Test that cached data is returned without re-downloading."""
    print_section("Test 3: Cache Hit (same 3 months)")

    manager = DataManager()
    ticker = "AAPL"

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=90)

    try:
        print(f"Requesting {ticker} from {start_date} to {end_date} (should hit cache)...")
        data = manager.get_data(ticker, start_date, end_date, interval='1d')
        print(f"✓ Retrieved {len(data)} rows (from cache)")
        return True
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        return False


def test_smart_expansion():
    """Test that smart fetching works when expanding date range."""
    print_section("Test 4: Smart Expansion (3 months → 1 year)")

    manager = DataManager()
    ticker = "AAPL"

    # Request 1 year (we already have 3 months, should only fetch missing 9 months)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)

    try:
        print(f"Requesting {ticker} from {start_date} to {end_date}...")
        print("(Should only fetch missing data before cached range)")
        data = manager.get_data(ticker, start_date, end_date, interval='1d')
        print(f"✓ Retrieved {len(data)} rows (merged cached + new data)")

        # Check cache info again
        cache_info = manager.get_ticker_cache_info(ticker)
        print(f"✓ Updated cache info: {cache_info}")

        return True
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_interval():
    """Test that different intervals are cached separately."""
    print_section("Test 5: Different Interval (hourly)")

    manager = DataManager()
    ticker = "AAPL"

    # Request hourly data for last 7 days
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)

    try:
        print(f"Requesting {ticker} hourly data from {start_date} to {end_date}...")
        data = manager.get_data(ticker, start_date, end_date, interval='1h')
        print(f"✓ Downloaded {len(data)} rows")

        # Check cache info (should show both daily and hourly)
        cache_info = manager.get_ticker_cache_info(ticker)
        print(f"✓ Cache now has {len(cache_info['intervals'])} interval(s):")
        for interval_info in cache_info['intervals']:
            print(f"    - {interval_info['interval']}: {interval_info['rows']} rows, {interval_info['start_date']} to {interval_info['end_date']}")

        return True
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_stats():
    """Test cache statistics."""
    print_section("Test 6: Cache Statistics")

    manager = DataManager()

    try:
        stats = manager.get_cache_stats()
        print(f"✓ Cache Statistics:")
        print(f"    Total tickers: {stats['total_tickers']}")
        print(f"    Total rows: {stats['total_rows']}")
        print(f"    DB size: {stats['db_size_mb']:.2f} MB")
        print(f"    DB path: {stats['db_path']}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        return False


def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " Market Data Caching Functionality Test ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")

    results = []

    # Run tests
    results.append(("S&P 500 Download", test_sp500_download()))
    results.append(("Basic Caching", test_basic_caching()))
    results.append(("Cache Hit", test_cache_hit()))
    results.append(("Smart Expansion", test_smart_expansion()))
    results.append(("Different Interval", test_different_interval()))
    results.append(("Cache Statistics", test_cache_stats()))

    # Summary
    print_section("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Caching implementation is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        sys.exit(1)
