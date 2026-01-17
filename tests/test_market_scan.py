import requests
import json

BASE_URL = "http://localhost:8086"

def test_market_scan_basic():
    print("Testing Market Scan with Bollinger Bands strategy...")
    print("This test will scan all S&P 500 stocks (may take several minutes)")

    response = requests.post(
        f"{BASE_URL}/market-scan",
        json={
            "strategy": "bollinger_bands_strategy",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "interval": "1d",
            "cash": 10000.0,
            "parameters": {
                "period": 20,
                "devfactor": 2.0
            }
        },
        timeout=600
    )

    print(f"\nStatus Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"\n{'='*60}")
        print("AGGREGATE METRICS")
        print(f"{'='*60}")
        print(f"Strategy: {result['strategy']}")
        print(f"Date Range: {result['start_date']} to {result['end_date']}")
        print(f"Interval: {result['interval']}")
        print(f"\nPortfolio Performance:")
        print(f"  Initial Capital: ${result['start_value']:,.2f}")
        print(f"  Final Value: ${result['end_value']:,.2f}")
        print(f"  Total PnL: ${result['pnl']:,.2f}")
        print(f"  Return: {result['return_pct']:.2f}%")
        print(f"  Sharpe Ratio: {result['sharpe_ratio']}")
        print(f"  Max Drawdown: {result['max_drawdown']:.2f}%")

        print(f"\nTrading Activity:")
        print(f"  Total Trades: {result['total_trades']}")
        print(f"  Winning Trades: {result['winning_trades']}")
        print(f"  Losing Trades: {result['losing_trades']}")
        print(f"  Stocks Scanned: {result['stocks_scanned']}")
        print(f"  Stocks With Trades: {result['stocks_with_trades']}")

        print(f"\n{'='*60}")
        print("MACRO STATISTICS")
        print(f"{'='*60}")
        macro = result['macro_statistics']
        print(f"\nPnL Distribution:")
        print(f"  Average PnL: ${macro['avg_pnl']:,.2f}")
        print(f"  Median PnL: ${macro['median_pnl']:,.2f}")
        print(f"  Std Dev PnL: ${macro['std_pnl']:,.2f}")
        print(f"  Min PnL: ${macro['min_pnl']:,.2f}")
        print(f"  Max PnL: ${macro['max_pnl']:,.2f}")

        print(f"\nReturn Distribution:")
        print(f"  Average Return: {macro['avg_return_pct']:.2f}%")
        print(f"  Median Return: {macro['median_return_pct']:.2f}%")
        print(f"  Std Dev Return: {macro['std_return_pct']:.2f}%")
        print(f"  Min Return: {macro['min_return_pct']:.2f}%")
        print(f"  Max Return: {macro['max_return_pct']:.2f}%")

        print(f"\nStock Profitability:")
        print(f"  Profitable Stocks: {macro['profitable_stocks']}")
        print(f"  Losing Stocks: {macro['losing_stocks']}")
        print(f"  Neutral Stocks: {macro['neutral_stocks']}")
        print(f"  Profitability Rate: {macro['profitability_rate']:.2f}%")

        print(f"\nTrading Metrics:")
        print(f"  Avg Trades Per Stock: {macro['avg_trades_per_stock']:.2f}")
        print(f"  Overall Win Rate: {macro['win_rate']:.2f}%")

        print(f"\n{'='*60}")
        print("TOP 10 PERFORMERS")
        print(f"{'='*60}")
        stock_results = result['stock_results']
        for i, stock in enumerate(stock_results[:10], 1):
            print(f"\n{i}. {stock['ticker']}")
            print(f"   PnL: ${stock['pnl']:,.2f} ({stock['return_pct']:.2f}%)")
            print(f"   Trades: {stock['total_trades']} (W:{stock['winning_trades']} L:{stock['losing_trades']})")
            print(f"   Sharpe: {stock['sharpe_ratio']}, Max DD: {stock['max_drawdown']}%")

        print(f"\n{'='*60}")
        print("BOTTOM 10 PERFORMERS")
        print(f"{'='*60}")
        for i, stock in enumerate(stock_results[-10:], 1):
            print(f"\n{i}. {stock['ticker']}")
            print(f"   PnL: ${stock['pnl']:,.2f} ({stock['return_pct']:.2f}%)")
            print(f"   Trades: {stock['total_trades']} (W:{stock['winning_trades']} L:{stock['losing_trades']})")
            print(f"   Sharpe: {stock['sharpe_ratio']}, Max DD: {stock['max_drawdown']}%")

        print(f"\n{'='*60}")
        print("TEST VALIDATION")
        print(f"{'='*60}")

        assert result['success'] == True, "Response should indicate success"
        assert result['stocks_scanned'] > 0, "Should scan at least one stock"
        assert len(stock_results) > 0, "Should have stock results"
        assert 'macro_statistics' in result, "Should have macro statistics"
        assert macro['avg_pnl'] is not None, "Should have average PnL"
        assert macro['profitability_rate'] >= 0, "Profitability rate should be non-negative"

        print("✓ All validations passed!")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_market_scan_minimal():
    print("\n" + "="*60)
    print("Testing Market Scan with minimal parameters (defaults)...")

    response = requests.post(
        f"{BASE_URL}/market-scan",
        json={
            "strategy": "williams_r_strategy"
        },
        timeout=600
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['success']}")
        print(f"Strategy: {result['strategy']}")
        print(f"Stocks Scanned: {result['stocks_scanned']}")
        print(f"Total PnL: ${result['pnl']:,.2f}")
        print(f"Return: {result['return_pct']:.2f}%")
        print(f"Profitability Rate: {result['macro_statistics']['profitability_rate']:.2f}%")

        assert result['success'] == True
        print("✓ Test passed!")
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("MARKET SCAN ENDPOINT TEST SUITE")
    print("="*60)
    print("Make sure the API server is running on localhost:8086")
    print("WARNING: This test scans all S&P 500 stocks and may take 5-10 minutes")
    print("="*60)

    try:
        passed = 0
        total = 2

        if test_market_scan_basic():
            passed += 1

        if test_market_scan_minimal():
            passed += 1

        print("\n" + "="*60)
        print(f"TEST SUMMARY: {passed}/{total} tests passed")
        print("="*60)

    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API server.")
        print("Please start the server with: python -m src.api.main")
    except requests.exceptions.Timeout:
        print("\nError: Request timed out. Market scan may be taking longer than expected.")
        print("Consider increasing the timeout or testing with a shorter date range.")
