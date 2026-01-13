"""
Test script for the new persistent run storage feature.
This script validates the implementation without requiring all dependencies.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all new modules can be imported."""
    print("Testing imports...")

    try:
        from src.data.run_repository import RunRepository
        print("✓ RunRepository imported successfully")
    except Exception as e:
        print(f"✗ Failed to import RunRepository: {e}")
        return False

    try:
        from src.api.models import ReplayRunRequest, SavedRunSummaryResponse, SavedRunDetailResponse
        print("✓ New API models imported successfully")
    except Exception as e:
        print(f"✗ Failed to import API models: {e}")
        return False

    try:
        from src.config.constants import TABLE_STRATEGY_RUNS
        print(f"✓ Constants imported successfully (TABLE_STRATEGY_RUNS={TABLE_STRATEGY_RUNS})")
    except Exception as e:
        print(f"✗ Failed to import constants: {e}")
        return False

    return True

def test_run_repository():
    """Test RunRepository basic functionality."""
    print("\nTesting RunRepository...")

    try:
        from src.data.run_repository import RunRepository
        import tempfile
        import os

        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db = f.name

        try:
            # Initialize repository
            repo = RunRepository(db_path=temp_db)
            print("✓ RunRepository initialized successfully")

            # Test saving a run
            run_record = {
                'ticker': 'AAPL',
                'strategy': 'test_strategy',
                'parameters': {'period': 14},
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
            print(f"✓ Run saved successfully with ID: {run_id}")

            # Test retrieving the run
            retrieved_run = repo.get_run_by_id(run_id)
            if retrieved_run and retrieved_run['ticker'] == 'AAPL':
                print("✓ Run retrieved successfully")
            else:
                print("✗ Failed to retrieve run correctly")
                return False

            # Test listing runs
            runs = repo.list_runs(limit=10)
            if len(runs) == 1:
                print(f"✓ List runs successful (found {len(runs)} run)")
            else:
                print(f"✗ List runs returned unexpected count: {len(runs)}")
                return False

            # Test filtering by ticker
            runs = repo.list_runs(ticker='AAPL')
            if len(runs) == 1:
                print("✓ Filter by ticker successful")
            else:
                print(f"✗ Filter by ticker failed: {len(runs)}")
                return False

            # Test count
            count = repo.get_run_count()
            if count == 1:
                print(f"✓ Count runs successful (count={count})")
            else:
                print(f"✗ Count runs unexpected: {count}")
                return False

            return True

        finally:
            # Clean up temp database
            if os.path.exists(temp_db):
                os.unlink(temp_db)
                print("✓ Cleaned up temporary database")

    except Exception as e:
        print(f"✗ RunRepository test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pydantic_models():
    """Test that Pydantic models are properly defined."""
    print("\nTesting Pydantic models...")

    try:
        from src.api.models import (
            ReplayRunRequest,
            SavedRunSummaryResponse,
            SavedRunDetailResponse
        )

        # Test ReplayRunRequest
        replay_req = ReplayRunRequest(
            start_date="2024-01-01",
            end_date="2024-12-31",
            cash=20000.0
        )
        print(f"✓ ReplayRunRequest created: {replay_req.dict()}")

        # Test SavedRunSummaryResponse
        summary = SavedRunSummaryResponse(
            id=1,
            ticker="AAPL",
            strategy="test_strategy",
            interval="1d",
            pnl=500.0,
            return_pct=5.0,
            created_at="2024-01-01T00:00:00"
        )
        print(f"✓ SavedRunSummaryResponse created: {summary.dict()}")

        # Test SavedRunDetailResponse
        detail = SavedRunDetailResponse(
            id=1,
            ticker="AAPL",
            strategy="test_strategy",
            parameters={"period": 14},
            start_date="2024-01-01",
            end_date="2024-12-31",
            interval="1d",
            cash=10000.0,
            pnl=500.0,
            return_pct=5.0,
            sharpe_ratio=1.2,
            max_drawdown=10.0,
            total_trades=10,
            winning_trades=6,
            losing_trades=4,
            created_at="2024-01-01T00:00:00"
        )
        print(f"✓ SavedRunDetailResponse created")

        return True

    except Exception as e:
        print(f"✗ Pydantic models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Persistent Run Storage Implementation")
    print("=" * 60)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test RunRepository
    if not test_run_repository():
        all_passed = False

    # Test Pydantic models
    if not test_pydantic_models():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nImplementation Summary:")
        print("- RunRepository: Create, read, list, filter functionality working")
        print("- Pydantic models: All models properly defined")
        print("- Database: SQLite schema created successfully")
        print("\nNext steps:")
        print("1. Start the API server: python run_api.py")
        print("2. Test the new endpoints:")
        print("   - GET /runs")
        print("   - GET /runs/{run_id}")
        print("   - POST /runs/{run_id}/replay")
        print("3. Verify that backtests are being saved automatically")
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
