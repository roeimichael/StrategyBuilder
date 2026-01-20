import requests
import json

BASE_URL = "http://localhost:8086"

def cleanup_portfolio():
    try:
        response = requests.get(f"{BASE_URL}/portfolio")
        if response.status_code == 200:
            portfolio = response.json()
            for position in portfolio['positions']:
                requests.delete(f"{BASE_URL}/portfolio/{position['id']}")
    except:
        pass

def test_add_position():
    print("\n" + "="*60)
    print("TEST 1: Add Portfolio Position")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/portfolio",
        json={
            "ticker": "AAPL",
            "quantity": 100,
            "entry_price": 150.50,
            "entry_date": "2024-01-15",
            "notes": "Initial tech position"
        }
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Position added successfully")
        print(f"  ID: {result['id']}")
        print(f"  Ticker: {result['ticker']}")
        print(f"  Quantity: {result['quantity']}")
        print(f"  Entry Price: ${result['entry_price']}")
        print(f"  Position Size: ${result['position_size']}")
        print(f"  Entry Date: {result['entry_date']}")

        assert result['ticker'] == 'AAPL'
        assert result['quantity'] == 100
        assert result['entry_price'] == 150.50
        assert result['position_size'] == 15050.0
        print("✓ Test passed!")
        return result['id']
    else:
        print(f"[FAIL] Error: {response.text}")
        return None

def test_get_portfolio():
    print("\n" + "="*60)
    print("TEST 2: Get Portfolio")
    print("="*60)

    response = requests.get(f"{BASE_URL}/portfolio")

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Portfolio retrieved successfully")
        print(f"  Total Positions: {result['total_positions']}")
        print(f"  Total Portfolio Value: ${result['total_portfolio_value']:,.2f}")
        print(f"\n  Positions:")
        for pos in result['positions']:
            print(f"    - {pos['ticker']}: {pos['quantity']} shares @ ${pos['entry_price']} = ${pos['position_size']:,.2f}")

        assert 'total_positions' in result
        assert 'positions' in result
        print("✓ Test passed!")
        return True
    else:
        print(f"[FAIL] Error: {response.text}")
        return False

def test_update_position(position_id):
    print("\n" + "="*60)
    print("TEST 3: Update Portfolio Position")
    print("="*60)

    response = requests.put(
        f"{BASE_URL}/portfolio/{position_id}",
        json={
            "quantity": 150,
            "notes": "Increased position"
        }
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Position updated successfully")
        print(f"  ID: {result['id']}")
        print(f"  New Quantity: {result['quantity']}")
        print(f"  New Position Size: ${result['position_size']:,.2f}")
        print(f"  Updated Notes: {result['notes']}")

        assert result['quantity'] == 150
        assert result['position_size'] == 22575.0
        print("✓ Test passed!")
        return True
    else:
        print(f"[FAIL] Error: {response.text}")
        return False

def test_add_multiple_positions():
    print("\n" + "="*60)
    print("TEST 4: Add Multiple Positions")
    print("="*60)

    positions = [
        {"ticker": "MSFT", "quantity": 50, "entry_price": 300.0, "entry_date": "2024-01-20", "notes": "Cloud play"},
        {"ticker": "GOOGL", "quantity": 75, "entry_price": 140.0, "entry_date": "2024-02-01", "notes": "AI exposure"},
        {"ticker": "TSLA", "quantity": 30, "entry_price": 200.0, "entry_date": "2024-02-15", "notes": "EV sector"}
    ]

    added_ids = []
    for pos in positions:
        response = requests.post(f"{BASE_URL}/portfolio", json=pos)
        if response.status_code == 200:
            result = response.json()
            added_ids.append(result['id'])
            print(f"[OK] Added {pos['ticker']}: ${pos['quantity'] * pos['entry_price']:,.2f}")
        else:
            print(f"[FAIL] Failed to add {pos['ticker']}: {response.text}")

    print(f"\n  Total positions added: {len(added_ids)}")
    assert len(added_ids) == 3
    print("✓ Test passed!")
    return added_ids

def test_portfolio_analysis():
    print("\n" + "="*60)
    print("TEST 5: Portfolio Analysis")
    print("="*60)
    print("Running strategy analysis across portfolio (may take 1-2 minutes)...")

    response = requests.post(
        f"{BASE_URL}/portfolio/analyze",
        json={
            "strategy": "bollinger_bands_strategy",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "interval": "1d",
            "parameters": {
                "period": 20,
                "devfactor": 2.0
            }
        },
        timeout=300
    )

    print(f"\nStatus Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Portfolio analysis completed successfully")

        print(f"\n{'='*60}")
        print("PORTFOLIO WEIGHTED METRICS")
        print(f"{'='*60}")
        print(f"Strategy: {result['strategy']}")
        print(f"Date Range: {result['start_date']} to {result['end_date']}")
        print(f"Interval: {result['interval']}")

        print(f"\nPortfolio Value: ${result['total_portfolio_value']:,.2f}")
        print(f"Weighted PnL: ${result['weighted_pnl']:,.2f}")
        print(f"Weighted Return: {result['weighted_return_pct']:.2f}%")
        print(f"Weighted Sharpe Ratio: {result['weighted_sharpe_ratio']}")
        print(f"Weighted Max Drawdown: {result['weighted_max_drawdown']:.2f}%")

        print(f"\nTrading Activity:")
        print(f"  Total Trades: {result['total_trades']}")
        print(f"  Winning Trades: {result['winning_trades']}")
        print(f"  Losing Trades: {result['losing_trades']}")
        print(f"  Positions Analyzed: {result['positions_analyzed']}")

        print(f"\n{'='*60}")
        print("PORTFOLIO STATISTICS")
        print(f"{'='*60}")
        stats = result['portfolio_statistics']
        print(f"Average Position PnL: ${stats['avg_position_pnl']:,.2f}")
        print(f"Median Position PnL: ${stats['median_position_pnl']:,.2f}")
        print(f"Std Dev Position PnL: ${stats['std_position_pnl']:,.2f}")
        print(f"Min Position PnL: ${stats['min_position_pnl']:,.2f}")
        print(f"Max Position PnL: ${stats['max_position_pnl']:,.2f}")
        print(f"\nProfitable Positions: {stats['profitable_positions']}")
        print(f"Losing Positions: {stats['losing_positions']}")
        print(f"Win Rate: {stats['win_rate']:.2f}%")
        print(f"Avg Trades Per Position: {stats['avg_trades_per_position']:.2f}")

        print(f"\n{'='*60}")
        print("INDIVIDUAL POSITION RESULTS")
        print(f"{'='*60}")
        for pos in result['position_results']:
            print(f"\n{pos['ticker']}:")
            print(f"  Position Size: ${pos['position_size']:,.2f} ({pos['weight']}% of portfolio)")
            print(f"  PnL: ${pos['pnl']:,.2f} ({pos['return_pct']}%)")
            print(f"  Trades: {pos['total_trades']} (W:{pos['winning_trades']} L:{pos['losing_trades']})")
            print(f"  Sharpe: {pos['sharpe_ratio']}, Max DD: {pos['max_drawdown']}%")

        print(f"\n{'='*60}")
        print("TEST VALIDATION")
        print(f"{'='*60}")

        assert result['success'] == True
        assert result['positions_analyzed'] > 0
        assert 'weighted_pnl' in result
        assert 'portfolio_statistics' in result
        assert len(result['position_results']) == result['positions_analyzed']

        print("✓ All validations passed!")
        return True
    else:
        print(f"[FAIL] Error: {response.text}")
        return False

def test_delete_position(position_id):
    print("\n" + "="*60)
    print("TEST 6: Delete Portfolio Position")
    print("="*60)

    response = requests.delete(f"{BASE_URL}/portfolio/{position_id}")

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"[OK] Position deleted successfully")
        print(f"  Message: {result['message']}")

        verify = requests.get(f"{BASE_URL}/portfolio/{position_id}")
        assert verify.status_code == 404
        print("✓ Test passed!")
        return True
    else:
        print(f"[FAIL] Error: {response.text}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("PORTFOLIO MANAGEMENT TEST SUITE")
    print("="*60)
    print("Make sure the API server is running on localhost:8086")
    print("="*60)

    try:
        cleanup_portfolio()

        passed = 0
        total = 6

        position_id = test_add_position()
        if position_id:
            passed += 1

        if test_get_portfolio():
            passed += 1

        if position_id and test_update_position(position_id):
            passed += 1

        added_ids = test_add_multiple_positions()
        if added_ids:
            passed += 1

        if test_portfolio_analysis():
            passed += 1

        if position_id and test_delete_position(position_id):
            passed += 1

        print("\n" + "="*60)
        print(f"TEST SUMMARY: {passed}/{total} tests passed")
        print("="*60)

        cleanup_portfolio()

    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API server.")
        print("Please start the server with: python -m src.api.main")
    except requests.exceptions.Timeout:
        print("\nError: Request timed out.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
