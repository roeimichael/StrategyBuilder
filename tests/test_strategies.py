"""
Test script for strategy validation
Tests all strategies can be loaded and executed
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path
import backtrader as bt
import yfinance as yf
import pandas as pd

from src.services.strategy_service import StrategyService
from src.core.data_manager import DataManager

class StrategyTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.strategy_service = StrategyService()
        self.data_manager = DataManager()

    def get_test_data(self):
        """Get standard test data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        data_df = yf.download("AAPL", start=start_date, end=end_date, progress=False)

        if isinstance(data_df.columns, pd.MultiIndex):
            data_df.columns = data_df.columns.get_level_values(0)

        return data_df

    def test_strategy_loading(self):
        """Test that all strategies can be loaded"""
        print("\n" + "="*60)
        print("TEST 1: Strategy Loading")
        print("="*60)

        strategies_dir = Path("src/strategies")
        strategy_files = [f for f in strategies_dir.glob("*.py")
                         if not f.name.startswith("__")]

        print(f"\n  Found {len(strategy_files)} strategy files")

        for strategy_file in sorted(strategy_files):
            strategy_name = strategy_file.stem
            try:
                print(f"  Loading {strategy_name}...", end=" ")
                strategy_class = self.strategy_service.load_strategy_class(strategy_name)

                if strategy_class:
                    print("✓")
                    self.passed += 1
                else:
                    print("✗ (returned None)")
                    self.failed += 1
                    self.errors.append(f"{strategy_name}: load returned None")

            except Exception as e:
                print(f"✗ {str(e)}")
                self.failed += 1
                self.errors.append(f"{strategy_name}: {str(e)}")

    def test_strategy_initialization(self):
        """Test that strategies can be initialized with parameters"""
        print("\n" + "="*60)
        print("TEST 2: Strategy Initialization")
        print("="*60)

        test_strategies = [
            ("bollinger_bands_strategy", {"period": 20, "devfactor": 2.0}),
            ("williams_r_strategy", {"period": 14, "oversold": -80, "overbought": -20}),
            ("rsi_stochastic_strategy", {
                "rsi_period": 14, "rsi_oversold": 30, "rsi_overbought": 70,
                "stoch_period": 14, "stoch_oversold": 20, "stoch_overbought": 80
            }),
            ("mfi_strategy", {"period": 14, "oversold": 20, "overbought": 80}),
            ("keltner_channel_strategy", {"ema_period": 20, "atr_period": 10, "atr_multiplier": 2.0}),
        ]

        data_df = self.get_test_data()
        if data_df.empty:
            print("  ✗ Could not get test data")
            self.failed += 1
            return

        for strategy_name, params in test_strategies:
            try:
                print(f"\n  Testing {strategy_name}...")
                strategy_class = self.strategy_service.load_strategy_class(strategy_name)

                if not strategy_class:
                    print(f"    ✗ Could not load strategy")
                    self.failed += 1
                    continue

                cerebro = bt.Cerebro()
                data_feed = bt.feeds.PandasData(dataname=data_df)
                cerebro.adddata(data_feed)
                cerebro.addstrategy(strategy_class, args=params, **params)

                print(f"    ✓ Strategy initialized with params: {params}")
                self.passed += 1

            except Exception as e:
                print(f"    ✗ Exception: {str(e)}")
                self.failed += 1
                self.errors.append(f"{strategy_name} init: {str(e)}")

    def test_strategy_execution(self):
        """Test that strategies can execute backtests"""
        print("\n" + "="*60)
        print("TEST 3: Strategy Execution")
        print("="*60)

        test_strategies = [
            ("bollinger_bands_strategy", {"period": 20, "devfactor": 2.0}),
            ("williams_r_strategy", {"period": 14, "oversold": -80, "overbought": -20}),
            ("tema_macd_strategy", {"macd1": 12, "macd2": 26, "macdsig": 9, "tema_period": 12}),
            ("alligator_strategy", {"lips_period": 5, "teeth_period": 8, "jaws_period": 13, "ema_period": 200}),
        ]

        data_df = self.get_test_data()
        if data_df.empty:
            print("  ✗ Could not get test data")
            self.failed += 1
            return

        for strategy_name, params in test_strategies:
            try:
                print(f"\n  Executing {strategy_name}...")
                strategy_class = self.strategy_service.load_strategy_class(strategy_name)

                if not strategy_class:
                    print(f"    ✗ Could not load strategy")
                    self.failed += 1
                    continue

                cerebro = bt.Cerebro()
                data_feed = bt.feeds.PandasData(dataname=data_df)
                cerebro.adddata(data_feed)
                cerebro.broker.setcash(10000.0)
                cerebro.broker.setcommission(commission=0.001)
                cerebro.addstrategy(strategy_class, args=params, **params)

                start_value = cerebro.broker.getvalue()
                results = cerebro.run()
                end_value = cerebro.broker.getvalue()
                pnl = end_value - start_value

                print(f"    ✓ Backtest completed")
                print(f"      Start: ${start_value:.2f}, End: ${end_value:.2f}, PnL: ${pnl:.2f}")
                self.passed += 1

            except Exception as e:
                print(f"    ✗ Exception: {str(e)}")
                self.failed += 1
                self.errors.append(f"{strategy_name} execution: {str(e)}")

    def test_strategy_parameters(self):
        """Test that strategies have proper parameter definitions"""
        print("\n" + "="*60)
        print("TEST 4: Strategy Parameter Definitions")
        print("="*60)

        strategies_dir = Path("src/strategies")
        strategy_files = [f for f in strategies_dir.glob("*.py")
                         if not f.name.startswith("__")]

        for strategy_file in sorted(strategy_files):
            strategy_name = strategy_file.stem
            try:
                print(f"\n  Checking {strategy_name}...")
                strategy_class = self.strategy_service.load_strategy_class(strategy_name)

                if not strategy_class:
                    print(f"    ✗ Could not load")
                    self.failed += 1
                    continue

                # Check if has params attribute
                if hasattr(strategy_class, 'params'):
                    param_count = 0
                    params_list = []

                    for param_name in dir(strategy_class.params):
                        if not param_name.startswith('_'):
                            param_value = getattr(strategy_class.params, param_name, None)
                            if param_value is not None and not callable(param_value):
                                param_count += 1
                                params_list.append(f"{param_name}={param_value}")

                    if param_count > 0:
                        print(f"    ✓ Has {param_count} parameters: {', '.join(params_list)}")
                        self.passed += 1
                    else:
                        print(f"    ⚠ No parameters defined")
                        self.passed += 1
                else:
                    print(f"    ⚠ No params attribute")
                    self.passed += 1

            except Exception as e:
                print(f"    ✗ Exception: {str(e)}")
                self.failed += 1
                self.errors.append(f"{strategy_name} params: {str(e)}")

    def test_strategy_info_endpoint(self):
        """Test strategy info retrieval"""
        print("\n" + "="*60)
        print("TEST 5: Strategy Info Retrieval")
        print("="*60)

        test_strategies = [
            "bollinger_bands_strategy",
            "williams_r_strategy",
            "rsi_stochastic_strategy",
            "mfi_strategy",
            "tema_macd_strategy"
        ]

        for strategy_name in test_strategies:
            try:
                print(f"\n  Getting info for {strategy_name}...")
                info = self.strategy_service.get_strategy_info(strategy_name)

                print(f"    ✓ Class: {info['class_name']}")
                print(f"      Module: {info['module']}")

                if info.get('optimizable_params'):
                    print(f"      Optimizable params: {len(info['optimizable_params'])}")
                    for param in info['optimizable_params']:
                        print(f"        - {param['name']}: {param['type']} [{param['min']}-{param['max']}]")
                else:
                    print(f"      ⚠ No optimizable params defined")

                self.passed += 1

            except Exception as e:
                print(f"    ✗ Exception: {str(e)}")
                self.failed += 1
                self.errors.append(f"{strategy_name} info: {str(e)}")

    def test_short_position_support(self):
        """Test which strategies support short positions"""
        print("\n" + "="*60)
        print("TEST 6: Short Position Support Detection")
        print("="*60)

        strategies_dir = Path("src/strategies")
        strategy_files = [f for f in strategies_dir.glob("*.py")
                         if not f.name.startswith("__")]

        strategies_with_shorts = []
        strategies_without_shorts = []

        for strategy_file in sorted(strategy_files):
            strategy_name = strategy_file.stem
            try:
                # Read strategy file and check for position_type and sell() calls
                with open(strategy_file, 'r') as f:
                    content = f.read()

                has_position_type = 'self.position_type' in content
                has_sell_call = 'self.sell()' in content
                has_short_logic = has_position_type and has_sell_call

                if has_short_logic:
                    strategies_with_shorts.append(strategy_name)
                    print(f"  ✓ {strategy_name}: SHORT SUPPORT")
                else:
                    strategies_without_shorts.append(strategy_name)
                    print(f"  - {strategy_name}: long only")

                self.passed += 1

            except Exception as e:
                print(f"  ✗ {strategy_name}: {str(e)}")
                self.failed += 1

        print(f"\n  Summary:")
        print(f"    Strategies with short support: {len(strategies_with_shorts)}")
        print(f"    Long-only strategies: {len(strategies_without_shorts)}")
        coverage = len(strategies_with_shorts) / (len(strategies_with_shorts) + len(strategies_without_shorts)) * 100
        print(f"    Short position coverage: {coverage:.1f}%")

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
            print("\n✓ All strategy tests passed!")
            return True
        else:
            print(f"\n✗ {self.failed} test(s) failed")
            return False

def main():
    print("="*60)
    print("STRATEGY VALIDATION TEST SUITE")
    print("="*60)
    print("Testing all strategy implementations")
    print("="*60)

    tester = StrategyTester()

    tester.test_strategy_loading()
    tester.test_strategy_initialization()
    tester.test_strategy_execution()
    tester.test_strategy_parameters()
    tester.test_strategy_info_endpoint()
    tester.test_short_position_support()

    return tester.print_summary()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
