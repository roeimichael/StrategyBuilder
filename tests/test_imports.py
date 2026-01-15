"""
Test script for validating all imports and __init__ files
Ensures all modules can be imported without errors
"""
import sys
import os
import importlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class ImportTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test_module_import(self, module_name, description=""):
        """Test importing a single module"""
        try:
            print(f"  Testing {module_name}...", end=" ")
            importlib.import_module(module_name)
            print("[OK]")
            self.passed += 1
            return True
        except Exception as e:
            print(f"[FAIL]")
            print(f"    Error: {str(e)}")
            self.failed += 1
            self.errors.append(f"{module_name}: {str(e)}")
            return False

    def test_core_modules(self):
        """Test all core module imports"""
        print("\n" + "="*60)
        print("TEST 1: Core Modules")
        print("="*60)

        modules = [
            "src.core.strategy_skeleton",
            "src.core.data_manager",
            "src.core.optimizer",
            "src.core.strategy_optimization_config"
        ]

        for module in modules:
            self.test_module_import(module)

    def test_api_modules(self):
        """Test all API module imports"""
        print("\n" + "="*60)
        print("TEST 2: API Modules")
        print("="*60)

        modules = [
            "src.api.main",
            "src.api.models",
            "src.api.models.requests",
            "src.api.models.responses"
        ]

        for module in modules:
            self.test_module_import(module)

    def test_service_modules(self):
        """Test all service module imports"""
        print("\n" + "="*60)
        print("TEST 3: Service Modules")
        print("="*60)

        modules = [
            "src.services.strategy_service",
            "src.services.backtest_service"
        ]

        for module in modules:
            self.test_module_import(module)

    def test_indicator_modules(self):
        """Test all indicator imports"""
        print("\n" + "="*60)
        print("TEST 4: Indicator Modules")
        print("="*60)

        modules = [
            "src.indicators.obv_indicator",
            "src.indicators.mfi_indicator",
            "src.indicators.cmf_indicator"
        ]

        for module in modules:
            self.test_module_import(module)

    def test_strategy_modules(self):
        """Test all strategy imports"""
        print("\n" + "="*60)
        print("TEST 5: Strategy Modules")
        print("="*60)

        # Find all strategy files
        strategies_dir = Path("src/strategies")
        strategy_files = [f for f in strategies_dir.glob("*.py")
                         if not f.name.startswith("__")]

        for strategy_file in sorted(strategy_files):
            module_name = f"src.strategies.{strategy_file.stem}"
            self.test_module_import(module_name)

    def test_exception_modules(self):
        """Test exception module imports"""
        print("\n" + "="*60)
        print("TEST 6: Exception Modules")
        print("="*60)

        modules = [
            "src.exceptions",
            "src.exceptions.base",
            "src.exceptions.data_errors",
            "src.exceptions.strategy_errors"
        ]

        for module in modules:
            self.test_module_import(module)

    def test_data_modules(self):
        """Test data module imports"""
        print("\n" + "="*60)
        print("TEST 7: Data Modules")
        print("="*60)

        modules = [
            "src.data",
            "src.data.run_repository"
        ]

        for module in modules:
            self.test_module_import(module)

    def test_config_modules(self):
        """Test config module imports"""
        print("\n" + "="*60)
        print("TEST 8: Config Modules")
        print("="*60)

        modules = [
            "src.config",
            "src.config.constants",
            "src.config.backtest_config"
        ]

        for module in modules:
            self.test_module_import(module)

    def test_init_exports(self):
        """Test that __init__ files export expected items"""
        print("\n" + "="*60)
        print("TEST 9: __init__ Exports Validation")
        print("="*60)

        # Test src/__init__.py
        try:
            print("  Testing src.__init__ exports...", end=" ")
            import src
            if hasattr(src, '__all__'):
                print(f"[OK] ({len(src.__all__)} exports)")
                self.passed += 1
            else:
                print("[WARN] No __all__ defined")
                self.passed += 1
        except Exception as e:
            print(f"[FAIL] {str(e)}")
            self.failed += 1
            self.errors.append(f"src.__init__: {str(e)}")

        # Test src.api.models.__init__.py
        try:
            print("  Testing src.api.models.__init__ exports...", end=" ")
            from src.api import models
            if hasattr(models, '__all__'):
                expected_exports = [
                    'BacktestRequest', 'MarketDataRequest', 'OptimizationRequest',
                    'BacktestResponse', 'OptimizationResponse', 'OptimizationResult',
                    'StrategyInfo', 'ParameterInfo'
                ]
                missing = [e for e in expected_exports if e not in models.__all__]
                if not missing:
                    print(f"[OK] All expected exports present ({len(models.__all__)} total)")
                    self.passed += 1
                else:
                    print(f"[WARN] Missing exports: {missing}")
                    self.passed += 1
            else:
                print("[WARN] No __all__ defined")
                self.passed += 1
        except Exception as e:
            print(f"[FAIL] {str(e)}")
            self.failed += 1
            self.errors.append(f"src.api.models.__init__: {str(e)}")

        # Test src.exceptions.__init__.py
        try:
            print("  Testing src.exceptions.__init__ exports...", end=" ")
            from src import exceptions
            if hasattr(exceptions, '__all__'):
                print(f"[OK] ({len(exceptions.__all__)} exports)")
                self.passed += 1
            else:
                print("[WARN] No __all__ defined")
                self.passed += 1
        except Exception as e:
            print(f"[FAIL] {str(e)}")
            self.failed += 1
            self.errors.append(f"src.exceptions.__init__: {str(e)}")

    def test_circular_imports(self):
        """Test for circular import issues"""
        print("\n" + "="*60)
        print("TEST 10: Circular Import Detection")
        print("="*60)

        print("  Testing simultaneous imports...")
        try:
            # Import everything at once to detect circular dependencies
            from src.core import data_manager
            from src.core import optimizer
            from src.services import strategy_service, backtest_service
            from src.api import main
            print("  [OK] No circular import issues detected")
            self.passed += 1
        except ImportError as e:
            print(f"  [FAIL] Circular import detected: {str(e)}")
            self.failed += 1
            self.errors.append(f"Circular import: {str(e)}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.failed == 0:
            print("\n[OK] All imports validated successfully!")
            return True
        else:
            print(f"\n[FAIL] {self.failed} import test(s) failed")
            return False

def main():
    print("="*60)
    print("IMPORT VALIDATION TEST SUITE")
    print("="*60)
    print("Testing all module imports and __init__ files")
    print("="*60)

    tester = ImportTester()

    tester.test_core_modules()
    tester.test_api_modules()
    tester.test_service_modules()
    tester.test_indicator_modules()
    tester.test_strategy_modules()
    tester.test_exception_modules()
    tester.test_data_modules()
    tester.test_config_modules()
    tester.test_init_exports()
    tester.test_circular_imports()

    return tester.print_summary()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
