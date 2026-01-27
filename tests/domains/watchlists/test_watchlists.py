"""Comprehensive tests for watchlist domain."""
import sys
import os
import tempfile
import datetime
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.domains.watchlists.repository import WatchlistRepository


def test_create_and_retrieve_watchlist() -> Dict[str, Any]:
    """Test creating a watchlist and retrieving it."""
    # Use temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = WatchlistRepository(db_path)

        # Create watchlist
        watchlist_data = {
            'name': 'Test Watchlist',
            'description': 'Testing watchlist functionality',
            'ticker': 'AAPL',
            'strategy': 'macd_strategy',
            'parameters': {'fast': 12, 'slow': 26, 'signal': 9},
            'interval': '1d',
            'cash': 10000.0,
            'active': True
        }

        watchlist_id = repo.create_watchlist(watchlist_data)
        assert watchlist_id is not None and watchlist_id > 0, "Failed to create watchlist"

        # Retrieve watchlist
        retrieved = repo.get_watchlist_by_id(watchlist_id)
        assert retrieved is not None, "Failed to retrieve watchlist"
        assert retrieved['name'] == watchlist_data['name'], "Name mismatch"
        assert retrieved['ticker'] == watchlist_data['ticker'], "Ticker mismatch"
        assert retrieved['strategy'] == watchlist_data['strategy'], "Strategy mismatch"
        assert retrieved['cash'] == watchlist_data['cash'], "Cash mismatch"
        assert retrieved['parameters'] == watchlist_data['parameters'], "Parameters mismatch"

        print(f"  [PASS] Create and retrieve watchlist (ID: {watchlist_id})")
        return {"passed": True, "name": "Create and Retrieve Watchlist", "error": None}

    except Exception as e:
        print(f"  [FAIL] Create and retrieve failed: {str(e)}")
        return {"passed": False, "name": "Create and Retrieve Watchlist", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_list_watchlists() -> Dict[str, Any]:
    """Test listing watchlists with filters."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = WatchlistRepository(db_path)

        # Create multiple watchlists
        watchlists_data = [
            {
                'name': 'AAPL Watch',
                'description': 'Apple watchlist',
                'ticker': 'AAPL',
                'strategy': 'macd_strategy',
                'parameters': {'fast': 12},
                'interval': '1d',
                'cash': 10000.0,
                'active': True
            },
            {
                'name': 'MSFT Watch',
                'description': 'Microsoft watchlist',
                'ticker': 'MSFT',
                'strategy': 'rsi_strategy',
                'parameters': {'period': 14},
                'interval': '1d',
                'cash': 10000.0,
                'active': True
            },
            {
                'name': 'Inactive Watch',
                'description': 'Inactive watchlist',
                'ticker': 'GOOGL',
                'strategy': 'sma_strategy',
                'parameters': {'period': 20},
                'interval': '1d',
                'cash': 10000.0,
                'active': False
            }
        ]

        created_ids = []
        for data in watchlists_data:
            wl_id = repo.create_watchlist(data)
            created_ids.append(wl_id)

        # Test list all watchlists
        all_watchlists = repo.list_watchlists()
        assert len(all_watchlists) == 3, f"Expected 3 watchlists, got {len(all_watchlists)}"

        # Test list active only
        active_watchlists = repo.list_watchlists(active_only=True)
        assert len(active_watchlists) == 2, f"Expected 2 active watchlists, got {len(active_watchlists)}"

        # Test filter by ticker
        aapl_watchlists = repo.list_watchlists(ticker='AAPL')
        assert len(aapl_watchlists) == 1, f"Expected 1 AAPL watchlist, got {len(aapl_watchlists)}"
        assert aapl_watchlists[0]['ticker'] == 'AAPL', "Ticker filter failed"

        print(f"  [PASS] List watchlists with filters (3 total, 2 active, 1 AAPL)")
        return {"passed": True, "name": "List Watchlists", "error": None}

    except Exception as e:
        print(f"  [FAIL] List watchlists failed: {str(e)}")
        return {"passed": False, "name": "List Watchlists", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_update_watchlist() -> Dict[str, Any]:
    """Test updating watchlist fields."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = WatchlistRepository(db_path)

        # Create watchlist
        watchlist_data = {
            'name': 'Test Watchlist',
            'description': 'Original description',
            'ticker': 'AAPL',
            'strategy': 'macd_strategy',
            'parameters': {'fast': 12},
            'interval': '1d',
            'cash': 10000.0,
            'active': True
        }

        watchlist_id = repo.create_watchlist(watchlist_data)

        # Update watchlist
        updates = {
            'description': 'Updated description',
            'active': False,
            'current_value': 12000.0,
            'pnl': 2000.0,
            'return_pct': 20.0
        }

        success = repo.update_watchlist(watchlist_id, updates)
        assert success, "Update failed"

        # Verify updates
        updated = repo.get_watchlist_by_id(watchlist_id)
        assert updated['description'] == 'Updated description', "Description not updated"
        assert updated['active'] == False, "Active status not updated"
        assert updated['current_value'] == 12000.0, "Current value not updated"
        assert updated['pnl'] == 2000.0, "PnL not updated"
        assert updated['return_pct'] == 20.0, "Return % not updated"

        print(f"  [PASS] Update watchlist fields")
        return {"passed": True, "name": "Update Watchlist", "error": None}

    except Exception as e:
        print(f"  [FAIL] Update watchlist failed: {str(e)}")
        return {"passed": False, "name": "Update Watchlist", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_delete_watchlist() -> Dict[str, Any]:
    """Test deleting a watchlist."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = WatchlistRepository(db_path)

        # Create watchlist
        watchlist_data = {
            'name': 'Test Watchlist',
            'description': 'To be deleted',
            'ticker': 'AAPL',
            'strategy': 'macd_strategy',
            'parameters': {'fast': 12},
            'interval': '1d',
            'cash': 10000.0,
            'active': True
        }

        watchlist_id = repo.create_watchlist(watchlist_data)

        # Delete watchlist
        success = repo.delete_watchlist(watchlist_id)
        assert success, "Delete failed"

        # Verify deletion
        deleted = repo.get_watchlist_by_id(watchlist_id)
        assert deleted is None, "Watchlist still exists after deletion"

        print(f"  [PASS] Delete watchlist")
        return {"passed": True, "name": "Delete Watchlist", "error": None}

    except Exception as e:
        print(f"  [FAIL] Delete watchlist failed: {str(e)}")
        return {"passed": False, "name": "Delete Watchlist", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_position_workflow() -> Dict[str, Any]:
    """Test complete position workflow: create position, retrieve, close."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = WatchlistRepository(db_path)

        # Create watchlist first
        watchlist_data = {
            'name': 'Position Test Watchlist',
            'description': 'Testing positions',
            'ticker': 'AAPL',
            'strategy': 'macd_strategy',
            'parameters': {'fast': 12},
            'interval': '1d',
            'cash': 10000.0,
            'active': True
        }

        watchlist_id = repo.create_watchlist(watchlist_data)

        # Create position
        position_data = {
            'watchlist_id': watchlist_id,
            'position_type': 'LONG',
            'entry_date': datetime.date.today().isoformat(),
            'entry_price': 150.0,
            'size': 100
        }

        position_id = repo.create_position(position_data)
        assert position_id > 0, "Failed to create position"

        # Get positions for watchlist
        positions = repo.get_positions_for_watchlist(watchlist_id)
        assert len(positions) == 1, f"Expected 1 position, got {len(positions)}"
        assert positions[0]['status'] == 'OPEN', "Position should be OPEN"

        # Close position
        exit_date = datetime.date.today().isoformat()
        exit_price = 160.0
        pnl = (exit_price - position_data['entry_price']) * position_data['size']

        success = repo.close_position(position_id, exit_date, exit_price, pnl)
        assert success, "Failed to close position"

        # Verify position is closed
        closed_positions = repo.get_positions_for_watchlist(watchlist_id, status='CLOSED')
        assert len(closed_positions) == 1, "Position should be closed"
        assert closed_positions[0]['exit_price'] == exit_price, "Exit price mismatch"
        assert closed_positions[0]['pnl'] == pnl, "PnL mismatch"

        print(f"  [PASS] Position workflow (create → close)")
        return {"passed": True, "name": "Position Workflow", "error": None}

    except Exception as e:
        print(f"  [FAIL] Position workflow failed: {str(e)}")
        return {"passed": False, "name": "Position Workflow", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_duplicate_name_validation() -> Dict[str, Any]:
    """Test that duplicate watchlist names are prevented."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = WatchlistRepository(db_path)

        # Create first watchlist
        watchlist_data = {
            'name': 'Unique Name',
            'description': 'First watchlist',
            'ticker': 'AAPL',
            'strategy': 'macd_strategy',
            'parameters': {'fast': 12},
            'interval': '1d',
            'cash': 10000.0,
            'active': True
        }

        repo.create_watchlist(watchlist_data)

        # Try to create second watchlist with same name
        duplicate_data = watchlist_data.copy()
        duplicate_data['ticker'] = 'MSFT'  # Different ticker, same name

        try:
            repo.create_watchlist(duplicate_data)
            print(f"  [FAIL] Duplicate name validation failed: duplicate was allowed")
            return {"passed": False, "name": "Duplicate Name Validation", "error": "Duplicate name was allowed"}
        except Exception:
            # Expected to fail due to UNIQUE constraint
            print(f"  [PASS] Duplicate name validation working")
            return {"passed": True, "name": "Duplicate Name Validation", "error": None}

    except Exception as e:
        print(f"  [FAIL] Duplicate name validation error: {str(e)}")
        return {"passed": False, "name": "Duplicate Name Validation", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def run_tests() -> list:
    """Run all watchlist tests."""
    print("\n" + "=" * 80)
    print("WATCHLIST DOMAIN TESTS (COMPREHENSIVE)")
    print("=" * 80)

    results = []
    results.append(test_create_and_retrieve_watchlist())
    results.append(test_list_watchlists())
    results.append(test_update_watchlist())
    results.append(test_delete_watchlist())
    results.append(test_position_workflow())
    results.append(test_duplicate_name_validation())

    passed = sum(1 for r in results if r['passed'])
    total = len(results)

    print(f"\nWatchlist Tests: {passed}/{total} passed")

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
