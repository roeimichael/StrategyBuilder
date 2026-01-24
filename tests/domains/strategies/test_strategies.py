"""
Test script for Strategies domain endpoints.

Tests:
- GET /strategies - List all strategies
- GET /strategies/{name} - Get strategy details
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))


def test_strategy_service_import():
    """Test that StrategyService can be imported."""
    print("  Testing StrategyService import...")
    try:
        from src.domains.strategies.service import StrategyService
        print("  PASS StrategyService imported successfully")
        return True
    except Exception as e:
        print(f"  FAIL Failed to import StrategyService: {e}")
        return False


def test_list_strategies():
    """Test listing all strategies."""
    print("  Testing list_strategies...")
    try:
        from src.domains.strategies.service import StrategyService

        service = StrategyService()
        strategies = service.list_strategies()

        if len(strategies) > 0:
            print(f"  PASS Found {len(strategies)} strategies")
            for strat in strategies[:3]:  # Show first 3
                print(f"    - {strat.module}: {strat.class_name}")
            return True
        else:
            print("  FAIL No strategies found")
            return False
    except Exception as e:
        print(f"  FAIL test_list_strategies failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_strategy_info():
    """Test getting strategy details."""
    print("  Testing get_strategy_info...")
    try:
        from src.domains.strategies.service import StrategyService

        service = StrategyService()
        strategy_info = service.get_strategy_info('bollinger_bands_strategy')

        if strategy_info and 'class_name' in strategy_info:
            print(f"  PASS Strategy info retrieved: {strategy_info['class_name']}")
            print(f"    Parameters: {len(strategy_info.get('parameters', {}))} found")
            return True
        else:
            print("  FAIL Failed to get strategy info")
            return False
    except Exception as e:
        print(f"  FAIL test_get_strategy_info failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test that strategies config loads correctly."""
    print("  Testing config loading...")
    try:
        from src.shared.utils.config_reader import ConfigReader

        config = ConfigReader.load_domain_config('strategies')
        print(f"  PASS Config loaded: DEFAULT_CASH = {config.DEFAULT_PARAMETERS['cash']}")
        return True
    except Exception as e:
        print(f"  FAIL Config loading failed: {e}")
        return False


def run_tests():
    """Run all strategies endpoint tests."""
    print("\n" + "=" * 60)
    print("Testing Strategies Domain")
    print("=" * 60)

    tests = [
        test_strategy_service_import,
        test_config_loading,
        test_list_strategies,
        test_get_strategy_info,
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
