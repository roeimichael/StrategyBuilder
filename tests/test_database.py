"""Database functionality tests"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import tempfile
import datetime
from utils.database import TradingDatabase


def test_database_operations():
    """Test all database operations"""
    print("=" * 80)
    print("DATABASE OPERATIONS TESTING")
    print("=" * 80)

    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        db = TradingDatabase(db_path)
        print(f"✓ Database initialized: {db_path}")

        # Test 1: Save backtest
        print("\nTest 1: Save backtest...")
        test_results = {
            'ticker': 'AAPL',
            'interval': '1d',
            'start_date': '2023-01-01',
            'end_date': '2024-01-01',
            'start_value': 10000,
            'end_value': 11500,
            'return_pct': 15.0,
            'sharpe_ratio': 1.2,
            'max_drawdown': 5.5,
            'total_trades': 10,
            'trades': [
                {'entry_date': datetime.date(2023, 1, 15), 'exit_date': datetime.date(2023, 2, 1),
                 'entry_price': 150.0, 'exit_price': 155.0, 'size': 10, 'pnl': 50.0, 'pnl_pct': 3.33}
            ]
        }

        backtest_id = db.save_backtest(
            results=test_results,
            strategy='Bollinger Bands',
            parameters={'period': 20, 'devfactor': 2.0},
            notes='Test backtest'
        )
        print(f"✓ Backtest saved with ID: {backtest_id}")
        assert backtest_id > 0, "Backtest ID should be positive"

        # Test 2: Retrieve backtests
        print("\nTest 2: Retrieve backtests...")
        backtests = db.get_backtests(limit=10)
        print(f"✓ Retrieved {len(backtests)} backtest(s)")
        assert len(backtests) > 0, "Should retrieve at least one backtest"
        assert backtests[0]['ticker'] == 'AAPL', "Ticker should match"

        # Test 3: Filter by ticker
        print("\nTest 3: Filter by ticker...")
        aapl_backtests = db.get_backtests(ticker='AAPL')
        print(f"✓ Found {len(aapl_backtests)} AAPL backtest(s)")
        assert all(b['ticker'] == 'AAPL' for b in aapl_backtests), "All results should be AAPL"

        # Test 4: Filter by strategy
        print("\nTest 4: Filter by strategy...")
        bb_backtests = db.get_backtests(strategy='Bollinger Bands')
        print(f"✓ Found {len(bb_backtests)} Bollinger Bands backtest(s)")
        assert all(b['strategy'] == 'Bollinger Bands' for b in bb_backtests)

        # Test 5: Add to monitoring
        print("\nTest 5: Add to monitoring...")
        monitor_id = db.add_to_monitoring(
            ticker='AAPL',
            strategy='Bollinger Bands',
            interval='1d',
            parameters={'period': 20, 'devfactor': 2.0},
            backtest_id=backtest_id
        )
        print(f"✓ Added to monitoring with ID: {monitor_id}")
        assert monitor_id > 0, "Monitor ID should be positive"

        # Test 6: Get monitored stocks
        print("\nTest 6: Get monitored stocks...")
        monitored = db.get_monitored_stocks()
        print(f"✓ Retrieved {len(monitored)} monitored stock(s)")
        assert len(monitored) > 0, "Should have at least one monitored stock"
        assert monitored[0]['ticker'] == 'AAPL', "Monitored ticker should be AAPL"

        # Test 7: Log signal
        print("\nTest 7: Log trading signal...")
        db.log_signal(
            monitor_id=monitor_id,
            ticker='AAPL',
            signal_type='BUY',
            price=150.0,
            size=10,
            reason='Test signal'
        )
        print("✓ Signal logged successfully")

        # Test 8: Get signals
        print("\nTest 8: Get signals...")
        signals = db.get_signals(days=30)
        print(f"✓ Retrieved {len(signals)} signal(s)")
        assert len(signals) > 0, "Should have at least one signal"
        assert signals[0]['signal_type'] == 'BUY', "Signal type should be BUY"

        # Test 9: Update last checked
        print("\nTest 9: Update last checked...")
        db.update_monitor_last_checked(monitor_id)
        monitored_updated = db.get_monitored_stocks()
        print("✓ Last checked timestamp updated")
        assert monitored_updated[0]['last_checked'] is not None

        # Test 10: Remove from monitoring
        print("\nTest 10: Remove from monitoring...")
        db.remove_from_monitoring(monitor_id)
        active_monitored = db.get_monitored_stocks(status='active')
        print(f"✓ Removed from monitoring, {len(active_monitored)} active stocks remaining")
        assert len(active_monitored) == 0, "Should have no active monitored stocks"

        # Test 11: Multiple backtests
        print("\nTest 11: Save multiple backtests...")
        for i in range(5):
            db.save_backtest(
                results={**test_results, 'ticker': f'TEST{i}'},
                strategy='TEMA + MACD',
                parameters={},
                notes=f'Test {i}'
            )
        print("✓ Saved 5 additional backtests")

        all_backtests = db.get_backtests(limit=100)
        print(f"✓ Total backtests in database: {len(all_backtests)}")
        assert len(all_backtests) >= 6, "Should have at least 6 backtests"

        print("\n" + "=" * 80)
        print("ALL DATABASE TESTS PASSED ✓")
        print("=" * 80)

        return True

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
            print(f"\nCleaned up test database: {db_path}")


if __name__ == "__main__":
    success = test_database_operations()
    sys.exit(0 if success else 1)
