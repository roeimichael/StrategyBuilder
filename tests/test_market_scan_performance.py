"""
Market Scan Performance Analysis Test

This test analyzes the performance of the market-wide scan endpoint:
- Measures total execution time
- Identifies which stocks fail and why
- Tracks per-stock timing
- Provides statistical analysis of execution times
"""

import requests
import json
from datetime import datetime
import statistics

BASE_URL = "http://localhost:8086"

def test_market_scan_performance():
    """
    Run a market scan and analyze performance metrics
    """
    print("="*80)
    print("MARKET SCAN PERFORMANCE ANALYSIS")
    print("="*80)
    print(f"Starting test at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This test will scan all S&P 500 stocks and provide detailed performance metrics")
    print("="*80)

    # Use a shorter date range for faster testing
    test_params = {
        "strategy": "bollinger_bands_strategy",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",  # 3 months
        "interval": "1d",
        "cash": 10000.0,
        "parameters": {
            "period": 20,
            "devfactor": 2.0
        }
    }

    print(f"\nTest parameters:")
    print(f"  Strategy: {test_params['strategy']}")
    print(f"  Date range: {test_params['start_date']} to {test_params['end_date']}")
    print(f"  Interval: {test_params['interval']}")
    print(f"\nSending request to {BASE_URL}/market-scan...")
    print("="*80)

    start_time = datetime.now()

    try:
        response = requests.post(
            f"{BASE_URL}/market-scan",
            json=test_params,
            timeout=900  # 15 minutes timeout
        )

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        print(f"\nRequest completed!")
        print(f"Status Code: {response.status_code}")
        print(f"Total duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
        print("="*80)

        if response.status_code == 200:
            result = response.json()

            # Extract performance data
            perf_data = result.get('performance_data', {})
            stock_timings = perf_data.get('stock_timings', {})
            failed_stocks = perf_data.get('failed_stocks', [])

            print("\n" + "="*80)
            print("PERFORMANCE ANALYSIS RESULTS")
            print("="*80)

            # Overall metrics
            print(f"\n1. OVERALL METRICS")
            print(f"   Total execution time: {perf_data.get('total_time_seconds', 0):.2f}s")
            print(f"   Stocks processed: {result['stocks_scanned'] + len(failed_stocks)}")
            print(f"   Successful: {perf_data.get('successful_count', 0)}")
            print(f"   Failed: {perf_data.get('failed_count', 0)}")
            print(f"   Average time per stock: {perf_data.get('avg_time_per_stock', 0):.3f}s")

            # Timing statistics
            if stock_timings:
                timings_list = list(stock_timings.values())
                print(f"\n2. TIMING STATISTICS")
                print(f"   Min time: {min(timings_list):.3f}s")
                print(f"   Max time: {max(timings_list):.3f}s")
                print(f"   Mean time: {statistics.mean(timings_list):.3f}s")
                print(f"   Median time: {statistics.median(timings_list):.3f}s")
                print(f"   Std deviation: {statistics.stdev(timings_list) if len(timings_list) > 1 else 0:.3f}s")

                # Percentile analysis
                sorted_timings = sorted(timings_list)
                p50 = sorted_timings[len(sorted_timings)//2]
                p90 = sorted_timings[int(len(sorted_timings)*0.9)]
                p95 = sorted_timings[int(len(sorted_timings)*0.95)]
                p99 = sorted_timings[int(len(sorted_timings)*0.99)]

                print(f"\n   Percentiles:")
                print(f"     P50 (median): {p50:.3f}s")
                print(f"     P90: {p90:.3f}s")
                print(f"     P95: {p95:.3f}s")
                print(f"     P99: {p99:.3f}s")

            # Slowest stocks
            if stock_timings:
                print(f"\n3. SLOWEST 20 STOCKS")
                sorted_timings = sorted(stock_timings.items(), key=lambda x: x[1], reverse=True)
                for i, (ticker, elapsed) in enumerate(sorted_timings[:20], 1):
                    print(f"   {i:2d}. {ticker:6s}: {elapsed:6.3f}s")

            # Failed stocks analysis
            if failed_stocks:
                print(f"\n4. FAILED STOCKS ({len(failed_stocks)} total)")
                print(f"   Showing all failures:")

                # Group failures by error type
                error_types = {}
                for failure in failed_stocks:
                    error_msg = failure['error'][:100]  # First 100 chars
                    if error_msg not in error_types:
                        error_types[error_msg] = []
                    error_types[error_msg].append(failure['ticker'])

                for error_msg, tickers in error_types.items():
                    print(f"\n   Error: {error_msg}")
                    print(f"   Affected tickers ({len(tickers)}): {', '.join(tickers[:10])}")
                    if len(tickers) > 10:
                        print(f"   ... and {len(tickers) - 10} more")

                # List all failed tickers
                print(f"\n   Complete list of failed tickers:")
                all_failed_tickers = [f['ticker'] for f in failed_stocks]
                for i in range(0, len(all_failed_tickers), 10):
                    print(f"   {', '.join(all_failed_tickers[i:i+10])}")

            else:
                print(f"\n4. FAILED STOCKS")
                print(f"   ✓ No failures! All {len(stock_timings)} stocks processed successfully")

            # Performance insights
            print(f"\n5. PERFORMANCE INSIGHTS")
            avg_time = perf_data.get('avg_time_per_stock', 0)
            total_time = perf_data.get('total_time_seconds', 0)

            if avg_time > 0:
                stocks_per_minute = 60 / avg_time
                estimated_full_scan = (503 * avg_time) / 60

                print(f"   Processing rate: {stocks_per_minute:.1f} stocks/minute")
                print(f"   Estimated time for full S&P 500: {estimated_full_scan:.1f} minutes")

                if avg_time > 2.0:
                    print(f"\n   ⚠️  WARNING: Average time per stock is high ({avg_time:.3f}s)")
                    print(f"   Expected: ~0.5-1.5s per stock for daily data")
                    print(f"   Possible issues:")
                    print(f"     - Network latency fetching market data")
                    print(f"     - Slow indicator calculations")
                    print(f"     - Database operations")
                elif avg_time < 0.5:
                    print(f"\n   ✓ GOOD: Fast processing ({avg_time:.3f}s per stock)")
                else:
                    print(f"\n   ✓ ACCEPTABLE: Normal processing speed ({avg_time:.3f}s per stock)")

            # Trading results summary
            print(f"\n6. TRADING RESULTS SUMMARY")
            print(f"   Total PnL: ${result['pnl']:,.2f}")
            print(f"   Return: {result['return_pct']:.2f}%")
            print(f"   Stocks with trades: {result['stocks_with_trades']}/{result['stocks_scanned']}")
            print(f"   Total trades: {result['total_trades']}")
            print(f"   Win rate: {result['macro_statistics']['win_rate']:.2f}%")

            # Export timing data to JSON for further analysis
            output_file = "market_scan_performance_analysis.json"
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'test_parameters': test_params,
                'performance_data': perf_data,
                'overall_metrics': {
                    'total_time_seconds': total_duration,
                    'stocks_processed': result['stocks_scanned'] + len(failed_stocks),
                    'successful_count': result['stocks_scanned'],
                    'failed_count': len(failed_stocks)
                },
                'trading_results': {
                    'pnl': result['pnl'],
                    'return_pct': result['return_pct'],
                    'total_trades': result['total_trades'],
                    'win_rate': result['macro_statistics']['win_rate']
                }
            }

            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)

            print(f"\n7. DATA EXPORT")
            print(f"   ✓ Performance data exported to: {output_file}")
            print(f"   This file contains:")
            print(f"     - Per-stock timing data (dict with {len(stock_timings)} entries)")
            print(f"     - Failed stocks details")
            print(f"     - Statistical analysis")

            print("\n" + "="*80)
            print("TEST COMPLETED SUCCESSFULLY")
            print("="*80)

            return True

        else:
            print(f"\nERROR: Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("\nERROR: Request timed out after 15 minutes")
        print("The market scan is taking longer than expected")
        return False
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to API server")
        print("Please ensure the server is running on http://localhost:8086")
        return False
    except Exception as e:
        print(f"\nERROR: Unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_single_stock_baseline():
    """
    Test a single stock to establish baseline performance
    """
    print("\n" + "="*80)
    print("SINGLE STOCK BASELINE TEST")
    print("="*80)
    print("Testing single stock backtest to establish baseline performance")

    test_params = {
        "ticker": "AAPL",
        "strategy": "bollinger_bands_strategy",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "interval": "1d",
        "cash": 10000.0,
        "parameters": {
            "period": 20,
            "devfactor": 2.0
        }
    }

    print(f"\nTesting {test_params['ticker']}...")

    start_time = datetime.now()

    try:
        response = requests.post(
            f"{BASE_URL}/backtest",
            json=test_params,
            timeout=30
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if response.status_code == 200:
            result = response.json()
            print(f"✓ Success in {duration:.3f}s")
            print(f"  PnL: ${result['pnl']:.2f}")
            print(f"  Return: {result['return_pct']:.2f}%")
            print(f"  Trades: {result['total_trades']}")

            print(f"\n  BASELINE: Single stock takes {duration:.3f}s")
            print(f"  Extrapolated to 503 stocks: {(duration * 503)/60:.1f} minutes")
            print(f"  (Sequential processing, no parallelization)")

            return True
        else:
            print(f"✗ Failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("MARKET SCAN PERFORMANCE TEST SUITE")
    print("="*80)
    print("This test suite will:")
    print("  1. Run a single stock baseline test")
    print("  2. Run a full market scan with performance tracking")
    print("  3. Analyze timing, failures, and bottlenecks")
    print("  4. Export detailed results to JSON")
    print("\nMake sure the API server is running on localhost:8086")
    print("="*80)

    input("\nPress Enter to start the test suite...")

    # Run baseline test
    baseline_success = test_single_stock_baseline()

    # Run full performance test
    if baseline_success:
        print("\n")
        input("Press Enter to start the full market scan (this will take 5-15 minutes)...")
        performance_success = test_market_scan_performance()

        print("\n" + "="*80)
        print("TEST SUITE SUMMARY")
        print("="*80)
        print(f"Baseline test: {'✓ PASSED' if baseline_success else '✗ FAILED'}")
        print(f"Performance test: {'✓ PASSED' if performance_success else '✗ FAILED'}")
        print("="*80)
    else:
        print("\n⚠️  Skipping market scan test due to baseline failure")
