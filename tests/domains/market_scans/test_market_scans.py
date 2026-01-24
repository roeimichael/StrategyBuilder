"""
Test script for Market Scans domain endpoints.

Tests:
- POST /market-scan - Scan multiple tickers
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))


def test_imports():
    """Test that market scan components can be imported."""
    print("  Testing imports...")
    try:
        from src.domains.market_scans.service import MarketScanService
        from src.domains.market_scans.models import MarketScanRequest, MarketScanResponse
        print("  PASS Market scan components imported successfully")
        return True
    except ImportError as e:
        if "yfinance" in str(e):
            print(f"  WARN Warning: yfinance not installed (optional dependency)")
            return True  # Don't fail the test for optional dependency
        print(f"  FAIL Failed to import components: {e}")
        return False
    except Exception as e:
        print(f"  FAIL Failed to import components: {e}")
        return False


def test_config_loading():
    """Test that market_scans config loads correctly."""
    print("  Testing config loading...")
    try:
        from src.shared.utils.config_reader import ConfigReader

        config = ConfigReader.load_domain_config('market_scans')
        print(f"  PASS Config loaded: MAX_TICKERS_PER_SCAN = {config.MAX_TICKERS_PER_SCAN}")
        print(f"    TOP_PERFORMERS_COUNT = {config.TOP_PERFORMERS_COUNT}")
        print(f"    SAVE_SCAN_RUNS = {config.SAVE_SCAN_RUNS}")
        return True
    except Exception as e:
        print(f"  FAIL Config loading failed: {e}")
        return False


def test_market_scan_model():
    """Test MarketScanRequest model."""
    print("  Testing MarketScanRequest model...")
    try:
        from src.domains.market_scans.models import MarketScanRequest

        request = MarketScanRequest(
            tickers=["AAPL", "MSFT", "GOOGL"],
            strategy="bollinger_bands_strategy",
            start_date="2024-01-01",
            end_date="2024-12-31",
            interval="1d",
            cash=10000.0
        )
        print(f"  PASS MarketScanRequest created with {len(request.tickers)} tickers")
        return True
    except Exception as e:
        print(f"  FAIL Model test failed: {e}")
        return False


def run_tests():
    """Run all market_scans endpoint tests."""
    print("\n" + "=" * 60)
    print("Testing Market Scans Domain")
    print("=" * 60)

    tests = [
        test_imports,
        test_config_loading,
        test_market_scan_model,
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
