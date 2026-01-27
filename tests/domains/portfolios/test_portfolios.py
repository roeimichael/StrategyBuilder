"""Comprehensive tests for portfolio domain."""
import sys
import os
import tempfile
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.domains.portfolios.repository import PortfolioRepository
from src.domains.portfolios.models import PortfolioHolding


def test_create_and_retrieve_portfolio() -> Dict[str, Any]:
    """Test creating a portfolio and retrieving it."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = PortfolioRepository(db_path)

        # Create portfolio
        portfolio_data = {
            'name': 'Tech Portfolio',
            'description': 'Technology stocks portfolio',
            'holdings': [
                PortfolioHolding(ticker="AAPL", shares=100.0, weight=0.5),
                PortfolioHolding(ticker="MSFT", shares=50.0, weight=0.5)
            ]
        }

        portfolio_id = repo.create_portfolio(portfolio_data)
        assert portfolio_id is not None and portfolio_id > 0, "Failed to create portfolio"

        # Retrieve portfolio
        retrieved = repo.get_portfolio_by_id(portfolio_id)
        assert retrieved is not None, "Failed to retrieve portfolio"
        assert retrieved['name'] == portfolio_data['name'], "Name mismatch"
        assert retrieved['description'] == portfolio_data['description'], "Description mismatch"
        assert len(retrieved['holdings']) == 2, "Holdings count mismatch"

        print(f"  [PASS] Create and retrieve portfolio (ID: {portfolio_id}, {len(retrieved['holdings'])} holdings)")
        return {"passed": True, "name": "Create and Retrieve Portfolio", "error": None}

    except Exception as e:
        print(f"  [FAIL] Create and retrieve failed: {str(e)}")
        return {"passed": False, "name": "Create and Retrieve Portfolio", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_list_portfolios() -> Dict[str, Any]:
    """Test listing portfolios."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = PortfolioRepository(db_path)

        # Create multiple portfolios
        portfolios_data = [
            {
                'name': 'Tech Portfolio',
                'description': 'Tech stocks',
                'holdings': [PortfolioHolding(ticker="AAPL", shares=100.0)]
            },
            {
                'name': 'Finance Portfolio',
                'description': 'Financial stocks',
                'holdings': [PortfolioHolding(ticker="JPM", shares=50.0)]
            }
        ]

        for data in portfolios_data:
            repo.create_portfolio(data)

        # List all portfolios
        all_portfolios = repo.list_portfolios()
        assert len(all_portfolios) == 2, f"Expected 2 portfolios, got {len(all_portfolios)}"

        print(f"  [PASS] List portfolios ({len(all_portfolios)} portfolios)")
        return {"passed": True, "name": "List Portfolios", "error": None}

    except Exception as e:
        print(f"  [FAIL] List portfolios failed: {str(e)}")
        return {"passed": False, "name": "List Portfolios", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_update_portfolio() -> Dict[str, Any]:
    """Test updating portfolio fields."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = PortfolioRepository(db_path)

        # Create portfolio
        portfolio_data = {
            'name': 'Original Name',
            'description': 'Original description',
            'holdings': [PortfolioHolding(ticker="AAPL", shares=100.0)]
        }

        portfolio_id = repo.create_portfolio(portfolio_data)

        # Update portfolio
        updates = {
            'name': 'Updated Name',
            'description': 'Updated description',
            'holdings': [
                PortfolioHolding(ticker="AAPL", shares=150.0),
                PortfolioHolding(ticker="MSFT", shares=50.0)
            ]
        }

        success = repo.update_portfolio(portfolio_id, updates)
        assert success, "Update failed"

        # Verify updates
        updated = repo.get_portfolio_by_id(portfolio_id)
        assert updated['name'] == 'Updated Name', "Name not updated"
        assert updated['description'] == 'Updated description', "Description not updated"
        assert len(updated['holdings']) == 2, "Holdings not updated"

        print(f"  [PASS] Update portfolio fields")
        return {"passed": True, "name": "Update Portfolio", "error": None}

    except Exception as e:
        print(f"  [FAIL] Update portfolio failed: {str(e)}")
        return {"passed": False, "name": "Update Portfolio", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_delete_portfolio() -> Dict[str, Any]:
    """Test deleting a portfolio."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = PortfolioRepository(db_path)

        # Create portfolio
        portfolio_data = {
            'name': 'To Be Deleted',
            'description': 'Will be deleted',
            'holdings': [PortfolioHolding(ticker="AAPL", shares=100.0)]
        }

        portfolio_id = repo.create_portfolio(portfolio_data)

        # Delete portfolio
        success = repo.delete_portfolio(portfolio_id)
        assert success, "Delete failed"

        # Verify deletion
        deleted = repo.get_portfolio_by_id(portfolio_id)
        assert deleted is None, "Portfolio still exists after deletion"

        print(f"  [PASS] Delete portfolio")
        return {"passed": True, "name": "Delete Portfolio", "error": None}

    except Exception as e:
        print(f"  [FAIL] Delete portfolio failed: {str(e)}")
        return {"passed": False, "name": "Delete Portfolio", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_portfolio_weights() -> Dict[str, Any]:
    """Test portfolio with weighted holdings."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = PortfolioRepository(db_path)

        # Create portfolio with weights
        portfolio_data = {
            'name': 'Weighted Portfolio',
            'description': 'Portfolio with weights',
            'holdings': [
                PortfolioHolding(ticker="AAPL", shares=100.0, weight=0.6),
                PortfolioHolding(ticker="MSFT", shares=50.0, weight=0.4)
            ]
        }

        portfolio_id = repo.create_portfolio(portfolio_data)

        # Retrieve and verify
        portfolio = repo.get_portfolio_by_id(portfolio_id)
        holdings = portfolio['holdings']

        total_weight = sum(h.get('weight', 0) for h in holdings)
        assert abs(total_weight - 1.0) < 0.01, f"Weights should sum to 1.0, got {total_weight}"

        print(f"  [PASS] Portfolio weights validation (total weight: {total_weight:.2f})")
        return {"passed": True, "name": "Portfolio Weights", "error": None}

    except Exception as e:
        print(f"  [FAIL] Portfolio weights test failed: {str(e)}")
        return {"passed": False, "name": "Portfolio Weights", "error": str(e)}
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_duplicate_name_validation() -> Dict[str, Any]:
    """Test that duplicate portfolio names are prevented."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    try:
        repo = PortfolioRepository(db_path)

        # Create first portfolio
        portfolio_data = {
            'name': 'Unique Name',
            'description': 'First portfolio',
            'holdings': [PortfolioHolding(ticker="AAPL", shares=100.0)]
        }

        repo.create_portfolio(portfolio_data)

        # Try to create second portfolio with same name
        duplicate_data = portfolio_data.copy()

        try:
            repo.create_portfolio(duplicate_data)
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
    """Run all portfolio tests."""
    print("\n" + "=" * 80)
    print("PORTFOLIO DOMAIN TESTS (COMPREHENSIVE)")
    print("=" * 80)

    results = []
    results.append(test_create_and_retrieve_portfolio())
    results.append(test_list_portfolios())
    results.append(test_update_portfolio())
    results.append(test_delete_portfolio())
    results.append(test_portfolio_weights())
    results.append(test_duplicate_name_validation())

    passed = sum(1 for r in results if r['passed'])
    total = len(results)

    print(f"\nPortfolio Tests: {passed}/{total} passed")

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
