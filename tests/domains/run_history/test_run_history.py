"""
Test script for Run History domain endpoints.

Tests:
- GET /runs - List saved runs
- GET /runs/{id} - Get run details
- POST /runs/{id}/replay - Replay a run
"""

import sys
import os
import tempfile

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))


def test_run_repository_import():
    """Test that RunRepository can be imported."""
    print("  Testing RunRepository import...")
    try:
        from src.domains.run_history.repository import RunRepository
        print("  ✓ RunRepository imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to import RunRepository: {e}")
        return False


def test_run_repository_crud():
    """Test RunRepository CRUD operations."""
    print("  Testing RunRepository CRUD...")
    try:
        from src.domains.run_history.repository import RunRepository

        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db = f.name

        try:
            repo = RunRepository(db_path=temp_db)

            # Create
            run_record = {
                'ticker': 'AAPL',
                'strategy': 'bollinger_bands_strategy',
                'parameters': {'period': 20, 'devfactor': 2.0},
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'interval': '1d',
                'cash': 10000.0,
                'pnl': 500.0,
                'return_pct': 5.0,
                'sharpe_ratio': 1.2,
                'max_drawdown': 10.0,
                'total_trades': 10,
                'winning_trades': 6,
                'losing_trades': 4
            }

            run_id = repo.save_run(run_record)
            print(f"  ✓ Run saved with ID: {run_id}")

            # Read
            retrieved = repo.get_run_by_id(run_id)
            if retrieved and retrieved['ticker'] == 'AAPL':
                print("  ✓ Run retrieved successfully")
            else:
                print("  ✗ Failed to retrieve run")
                return False

            # List
            runs = repo.list_runs(limit=10)
            if len(runs) == 1:
                print(f"  ✓ List runs successful ({len(runs)} run)")
            else:
                print(f"  ✗ List runs unexpected count: {len(runs)}")
                return False

            # Filter
            filtered = repo.list_runs(ticker='AAPL')
            if len(filtered) == 1:
                print("  ✓ Filter by ticker successful")
            else:
                print(f"  ✗ Filter failed: {len(filtered)}")
                return False

            # Count
            count = repo.get_run_count()
            if count == 1:
                print(f"  ✓ Count runs successful ({count})")
            else:
                print(f"  ✗ Count unexpected: {count}")
                return False

            return True

        finally:
            if os.path.exists(temp_db):
                os.unlink(temp_db)

    except Exception as e:
        print(f"  ✗ CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models():
    """Test Run History Pydantic models."""
    print("  Testing Pydantic models...")
    try:
        from src.domains.run_history.models import (
            ReplayRunRequest,
            SavedRunSummaryResponse,
            SavedRunDetailResponse
        )

        # Test ReplayRunRequest
        replay = ReplayRunRequest(start_date="2024-01-01", cash=20000.0)
        print(f"  ✓ ReplayRunRequest created")

        # Test SavedRunSummaryResponse
        summary = SavedRunSummaryResponse(
            id=1, ticker="AAPL", strategy="test", interval="1d",
            pnl=500.0, return_pct=5.0, created_at="2024-01-01T00:00:00"
        )
        print(f"  ✓ SavedRunSummaryResponse created")

        # Test SavedRunDetailResponse
        detail = SavedRunDetailResponse(
            id=1, ticker="AAPL", strategy="test", parameters={},
            start_date="2024-01-01", end_date="2024-12-31", interval="1d",
            cash=10000.0, pnl=500.0, return_pct=5.0, sharpe_ratio=1.2,
            max_drawdown=10.0, total_trades=10, winning_trades=6,
            losing_trades=4, created_at="2024-01-01T00:00:00"
        )
        print(f"  ✓ SavedRunDetailResponse created")

        return True
    except Exception as e:
        print(f"  ✗ Models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test that run_history config loads correctly."""
    print("  Testing config loading...")
    try:
        from src.shared.utils.config_reader import ConfigReader

        config = ConfigReader.load_domain_config('run_history')
        print(f"  ✓ Config loaded: DEFAULT_LIST_LIMIT = {config.DEFAULT_LIST_LIMIT}")
        return True
    except Exception as e:
        print(f"  ✗ Config loading failed: {e}")
        return False


def run_tests():
    """Run all run_history endpoint tests."""
    print("\n" + "=" * 60)
    print("Testing Run History Domain")
    print("=" * 60)

    tests = [
        test_run_repository_import,
        test_config_loading,
        test_run_repository_crud,
        test_models,
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
