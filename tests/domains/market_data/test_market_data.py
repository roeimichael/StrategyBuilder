"""Comprehensive tests for market data domain - focuses on caching functionality."""
import sys
import os
import tempfile
import datetime
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.domains.market_data.manager import DataManager


def test_basic_data_fetch() -> Dict[str, Any]:
    """Test basic market data fetching and caching."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        manager = DataManager(db_path)
        ticker = "AAPL"

        # Fetch 1 month of data
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=30)

        data = manager.get_data(ticker, start_date, end_date, interval='1d')

        assert not data.empty, "No data returned"
        assert len(data) > 0, "Expected some data rows"
        assert 'Open' in data.columns, "Missing Open column"
        assert 'High' in data.columns, "Missing High column"
        assert 'Low' in data.columns, "Missing Low column"
        assert 'Close' in data.columns, "Missing Close column"
        assert 'Volume' in data.columns, "Missing Volume column"

        print(f"  [PASS] Basic data fetch ({len(data)} rows for {ticker})")
        return {"passed": True, "name": "Basic Data Fetch", "error": None}

    except Exception as e:
        print(f"  [FAIL] Basic data fetch failed: {str(e)}")
        return {"passed": False, "name": "Basic Data Fetch", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_cache_hit() -> Dict[str, Any]:
    """Test that cached data is returned without re-downloading."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        manager = DataManager(db_path)
        ticker = "AAPL"

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=30)

        # First fetch - should download
        data1 = manager.get_data(ticker, start_date, end_date, interval='1d')
        rows1 = len(data1)

        # Second fetch - should hit cache
        data2 = manager.get_data(ticker, start_date, end_date, interval='1d')
        rows2 = len(data2)

        assert rows1 == rows2, f"Row count mismatch: {rows1} vs {rows2}"
        assert data1.index.equals(data2.index), "Index mismatch between fetches"

        print(f"  [PASS] Cache hit working ({rows2} rows from cache)")
        return {"passed": True, "name": "Cache Hit", "error": None}

    except Exception as e:
        print(f"  [FAIL] Cache hit test failed: {str(e)}")
        return {"passed": False, "name": "Cache Hit", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_smart_range_expansion() -> Dict[str, Any]:
    """Test that expanding date range only fetches missing data."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        manager = DataManager(db_path)
        ticker = "AAPL"

        # First fetch - 1 month
        end_date = datetime.date.today()
        start_date_short = end_date - datetime.timedelta(days=30)
        data_short = manager.get_data(ticker, start_date_short, end_date, interval='1d')
        rows_short = len(data_short)

        # Second fetch - 3 months (should smart-fetch missing 2 months)
        start_date_long = end_date - datetime.timedelta(days=90)
        data_long = manager.get_data(ticker, start_date_long, end_date, interval='1d')
        rows_long = len(data_long)

        assert rows_long > rows_short, f"Expected more rows in long range: {rows_long} vs {rows_short}"

        # Verify cache info
        cache_info = manager.get_ticker_cache_info(ticker)
        assert cache_info['cached'], "Ticker should be cached"
        assert len(cache_info['intervals']) > 0, "Should have interval data"

        print(f"  [PASS] Smart range expansion ({rows_short} → {rows_long} rows)")
        return {"passed": True, "name": "Smart Range Expansion", "error": None}

    except Exception as e:
        print(f"  [FAIL] Smart range expansion failed: {str(e)}")
        return {"passed": False, "name": "Smart Range Expansion", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_different_intervals_cached_separately() -> Dict[str, Any]:
    """Test that different intervals are cached separately."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        manager = DataManager(db_path)
        ticker = "AAPL"

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=7)

        # Fetch daily data
        data_daily = manager.get_data(ticker, start_date, end_date, interval='1d')
        rows_daily = len(data_daily)

        # Fetch hourly data
        data_hourly = manager.get_data(ticker, start_date, end_date, interval='1h')
        rows_hourly = len(data_hourly)

        # Hourly should have more data points
        assert rows_hourly >= rows_daily, "Hourly should have at least as many points as daily"

        # Check cache has both intervals
        cache_info = manager.get_ticker_cache_info(ticker)
        intervals = [info['interval'] for info in cache_info['intervals']]

        assert '1d' in intervals, "Daily interval should be cached"
        assert '1h' in intervals, "Hourly interval should be cached"

        print(f"  [PASS] Different intervals cached (1d: {rows_daily}, 1h: {rows_hourly})")
        return {"passed": True, "name": "Different Intervals", "error": None}

    except Exception as e:
        print(f"  [FAIL] Different intervals test failed: {str(e)}")
        return {"passed": False, "name": "Different Intervals", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_cache_stats() -> Dict[str, Any]:
    """Test cache statistics functionality."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        manager = DataManager(db_path)

        # Fetch data for multiple tickers
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=30)

        manager.get_data("AAPL", start_date, end_date, interval='1d')
        manager.get_data("MSFT", start_date, end_date, interval='1d')

        # Get cache stats
        stats = manager.get_cache_stats()

        assert stats['total_tickers'] >= 2, f"Expected at least 2 tickers, got {stats['total_tickers']}"
        assert stats['total_rows'] > 0, "Expected some cached rows"
        assert stats['db_size_mb'] > 0, "Expected non-zero DB size"

        print(f"  [PASS] Cache stats ({stats['total_tickers']} tickers, {stats['total_rows']} rows, {stats['db_size_mb']:.2f} MB)")
        return {"passed": True, "name": "Cache Statistics", "error": None}

    except Exception as e:
        print(f"  [FAIL] Cache stats test failed: {str(e)}")
        return {"passed": False, "name": "Cache Statistics", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_sp500_ticker_download() -> Dict[str, Any]:
    """Test S&P 500 ticker list download with custom headers."""
    try:
        tickers = DataManager.get_sp500_tickers()

        assert len(tickers) > 0, "No tickers returned"
        assert len(tickers) >= 400, f"Expected at least 400 S&P 500 tickers, got {len(tickers)}"
        assert 'AAPL' in tickers, "AAPL should be in S&P 500"
        assert 'MSFT' in tickers, "MSFT should be in S&P 500"

        print(f"  [PASS] S&P 500 ticker download ({len(tickers)} tickers)")
        return {"passed": True, "name": "S&P 500 Ticker Download", "error": None}

    except Exception as e:
        print(f"  [FAIL] S&P 500 download failed: {str(e)}")
        return {"passed": False, "name": "S&P 500 Ticker Download", "error": str(e)}


def test_bulk_download() -> Dict[str, Any]:
    """Test bulk download functionality."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        manager = DataManager(db_path)

        tickers = ["AAPL", "MSFT", "GOOGL"]
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=30)

        results = manager.bulk_download(tickers, start_date, end_date, interval='1d')

        assert len(results) == 3, f"Expected 3 results, got {len(results)}"

        successful = sum(1 for r in results.values() if r['success'])
        assert successful >= 2, f"Expected at least 2 successful downloads, got {successful}"

        print(f"  [PASS] Bulk download ({successful}/{len(tickers)} successful)")
        return {"passed": True, "name": "Bulk Download", "error": None}

    except Exception as e:
        print(f"  [FAIL] Bulk download failed: {str(e)}")
        return {"passed": False, "name": "Bulk Download", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def run_tests() -> list:
    """Run all market data tests."""
    print("\n" + "=" * 80)
    print("MARKET DATA DOMAIN TESTS (COMPREHENSIVE - CACHING FOCUSED)")
    print("=" * 80)

    results = []
    results.append(test_sp500_ticker_download())
    results.append(test_basic_data_fetch())
    results.append(test_cache_hit())
    results.append(test_smart_range_expansion())
    results.append(test_different_intervals_cached_separately())
    results.append(test_cache_stats())
    results.append(test_bulk_download())

    passed = sum(1 for r in results if r['passed'])
    total = len(results)

    print(f"\nMarket Data Tests: {passed}/{total} passed")

    if passed < total:
        print("\nFailed tests:")
        for r in results:
            if not r['passed']:
                print(f"  - {r['name']}: {r['error']}")

    print("=" * 80)

    return results


if __name__ == "__main__":
    results = run_tests()
    sys.exit(0 if all(r['passed'] for r in results) else 1)
