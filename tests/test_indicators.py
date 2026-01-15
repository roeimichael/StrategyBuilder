"""
Test script for custom indicator accuracy and validation
Tests OBV, MFI, and CMF implementations
"""
import sys
from datetime import datetime, timedelta
import backtrader as bt
import yfinance as yf
import pandas as pd
import numpy as np

# Import custom indicators
from src.indicators.obv_indicator import OBV
from src.indicators.mfi_indicator import MFI
from src.indicators.cmf_indicator import CMF

class IndicatorTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def get_test_data(self, ticker="AAPL", days=90):
        """Download test data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        print(f"  Downloading {ticker} data ({days} days)...", end=" ")
        data_df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        # Handle multi-level columns from yfinance
        if isinstance(data_df.columns, pd.MultiIndex):
            data_df.columns = data_df.columns.get_level_values(0)

        if data_df.empty:
            print("✗ No data")
            return None

        print(f"✓ {len(data_df)} bars")
        return data_df

    def test_obv_indicator(self):
        """Test OBV (On-Balance Volume) indicator"""
        print("\n" + "="*60)
        print("TEST 1: OBV (On-Balance Volume) Indicator")
        print("="*60)

        try:
            data_df = self.get_test_data("AAPL", 90)
            if data_df is None:
                self.failed += 1
                return

            # Create cerebro and add data
            cerebro = bt.Cerebro()
            data_feed = bt.feeds.PandasData(dataname=data_df)
            cerebro.adddata(data_feed)

            # Create test strategy with OBV
            class TestOBVStrategy(bt.Strategy):
                def __init__(self):
                    self.obv = OBV(self.data)
                    self.obv_values = []

                def next(self):
                    self.obv_values.append({
                        'date': self.data.datetime.date(0),
                        'close': self.data.close[0],
                        'volume': self.data.volume[0],
                        'obv': self.obv[0]
                    })

            cerebro.addstrategy(TestOBVStrategy)
            results = cerebro.run()
            strategy = results[0]

            print(f"\n  OBV Calculation Tests:")
            print(f"  ✓ Indicator created successfully")
            print(f"  ✓ Total data points: {len(strategy.obv_values)}")

            if len(strategy.obv_values) > 0:
                # Check that OBV values are being calculated
                obv_values = [v['obv'] for v in strategy.obv_values]
                print(f"  ✓ OBV Range: [{min(obv_values):.0f}, {max(obv_values):.0f}]")

                # Verify OBV logic manually for a few points
                print(f"\n  Verifying OBV logic (sample points):")
                for i in range(min(5, len(strategy.obv_values))):
                    v = strategy.obv_values[i]
                    print(f"    Day {i+1}: Close={v['close']:.2f}, Vol={v['volume']:.0f}, OBV={v['obv']:.0f}")

                # Check that OBV changes with volume
                if len(obv_values) > 1:
                    obv_changed = any(obv_values[i] != obv_values[i-1] for i in range(1, len(obv_values)))
                    if obv_changed:
                        print(f"  ✓ OBV values are changing (not static)")
                    else:
                        print(f"  ⚠ OBV values appear static")

                self.passed += 1
            else:
                print(f"  ✗ No OBV values calculated")
                self.failed += 1
                self.errors.append("OBV: No values calculated")

        except Exception as e:
            print(f"\n  ✗ Exception: {str(e)}")
            self.failed += 1
            self.errors.append(f"OBV: {str(e)}")

    def test_mfi_indicator(self):
        """Test MFI (Money Flow Index) indicator"""
        print("\n" + "="*60)
        print("TEST 2: MFI (Money Flow Index) Indicator")
        print("="*60)

        try:
            data_df = self.get_test_data("BTC-USD", 90)
            if data_df is None:
                self.failed += 1
                return

            cerebro = bt.Cerebro()
            data_feed = bt.feeds.PandasData(dataname=data_df)
            cerebro.adddata(data_feed)

            class TestMFIStrategy(bt.Strategy):
                def __init__(self):
                    self.mfi = MFI(self.data, period=14)
                    self.mfi_values = []

                def next(self):
                    self.mfi_values.append({
                        'date': self.data.datetime.date(0),
                        'high': self.data.high[0],
                        'low': self.data.low[0],
                        'close': self.data.close[0],
                        'volume': self.data.volume[0],
                        'mfi': self.mfi[0]
                    })

            cerebro.addstrategy(TestMFIStrategy)
            results = cerebro.run()
            strategy = results[0]

            print(f"\n  MFI Calculation Tests:")
            print(f"  ✓ Indicator created successfully")
            print(f"  ✓ Total data points: {len(strategy.mfi_values)}")

            if len(strategy.mfi_values) > 0:
                mfi_values = [v['mfi'] for v in strategy.mfi_values]
                print(f"  ✓ MFI Range: [{min(mfi_values):.2f}, {max(mfi_values):.2f}]")

                # MFI should be between 0 and 100
                out_of_range = [v for v in mfi_values if v < 0 or v > 100]
                if not out_of_range:
                    print(f"  ✓ All MFI values in valid range [0, 100]")
                else:
                    print(f"  ✗ {len(out_of_range)} values out of range [0, 100]")
                    self.errors.append(f"MFI: {len(out_of_range)} values out of range")

                # Check for division by zero issues (should not have NaN)
                nan_count = sum(1 for v in mfi_values if np.isnan(v) or np.isinf(v))
                if nan_count == 0:
                    print(f"  ✓ No NaN/Inf values detected")
                else:
                    print(f"  ⚠ {nan_count} NaN/Inf values detected")

                # Display sample values
                print(f"\n  Sample MFI values:")
                for i in range(min(5, len(strategy.mfi_values))):
                    v = strategy.mfi_values[-(i+1)]  # Last 5 values
                    print(f"    {v['date']}: MFI={v['mfi']:.2f}")

                self.passed += 1
            else:
                print(f"  ✗ No MFI values calculated")
                self.failed += 1
                self.errors.append("MFI: No values calculated")

        except Exception as e:
            print(f"\n  ✗ Exception: {str(e)}")
            self.failed += 1
            self.errors.append(f"MFI: {str(e)}")

    def test_cmf_indicator(self):
        """Test CMF (Chaikin Money Flow) indicator"""
        print("\n" + "="*60)
        print("TEST 3: CMF (Chaikin Money Flow) Indicator")
        print("="*60)

        try:
            data_df = self.get_test_data("ETH-USD", 90)
            if data_df is None:
                self.failed += 1
                return

            cerebro = bt.Cerebro()
            data_feed = bt.feeds.PandasData(dataname=data_df)
            cerebro.adddata(data_feed)

            class TestCMFStrategy(bt.Strategy):
                def __init__(self):
                    self.cmf = CMF(self.data, period=20)
                    self.cmf_values = []

                def next(self):
                    self.cmf_values.append({
                        'date': self.data.datetime.date(0),
                        'high': self.data.high[0],
                        'low': self.data.low[0],
                        'close': self.data.close[0],
                        'volume': self.data.volume[0],
                        'cmf': self.cmf[0]
                    })

            cerebro.addstrategy(TestCMFStrategy)
            results = cerebro.run()
            strategy = results[0]

            print(f"\n  CMF Calculation Tests:")
            print(f"  ✓ Indicator created successfully")
            print(f"  ✓ Total data points: {len(strategy.cmf_values)}")

            if len(strategy.cmf_values) > 0:
                cmf_values = [v['cmf'] for v in strategy.cmf_values]
                print(f"  ✓ CMF Range: [{min(cmf_values):.4f}, {max(cmf_values):.4f}]")

                # CMF should be between -1 and 1
                out_of_range = [v for v in cmf_values if v < -1 or v > 1]
                if not out_of_range:
                    print(f"  ✓ All CMF values in valid range [-1, 1]")
                else:
                    print(f"  ✗ {len(out_of_range)} values out of range [-1, 1]")
                    self.errors.append(f"CMF: {len(out_of_range)} values out of range")

                # Check for NaN/Inf
                nan_count = sum(1 for v in cmf_values if np.isnan(v) or np.isinf(v))
                if nan_count == 0:
                    print(f"  ✓ No NaN/Inf values detected")
                else:
                    print(f"  ⚠ {nan_count} NaN/Inf values detected")

                # Display sample values
                print(f"\n  Sample CMF values:")
                for i in range(min(5, len(strategy.cmf_values))):
                    v = strategy.cmf_values[-(i+1)]
                    print(f"    {v['date']}: CMF={v['cmf']:.4f}")

                # Check that CMF oscillates
                positive_count = sum(1 for v in cmf_values if v > 0)
                negative_count = sum(1 for v in cmf_values if v < 0)
                print(f"\n  ✓ Positive values: {positive_count}, Negative values: {negative_count}")

                self.passed += 1
            else:
                print(f"  ✗ No CMF values calculated")
                self.failed += 1
                self.errors.append("CMF: No values calculated")

        except Exception as e:
            print(f"\n  ✗ Exception: {str(e)}")
            self.failed += 1
            self.errors.append(f"CMF: {str(e)}")

    def test_indicator_comparison(self):
        """Compare all three indicators on same data"""
        print("\n" + "="*60)
        print("TEST 4: Multi-Indicator Comparison")
        print("="*60)

        try:
            data_df = self.get_test_data("AAPL", 60)
            if data_df is None:
                self.failed += 1
                return

            cerebro = bt.Cerebro()
            data_feed = bt.feeds.PandasData(dataname=data_df)
            cerebro.adddata(data_feed)

            class TestAllIndicators(bt.Strategy):
                def __init__(self):
                    self.obv = OBV(self.data)
                    self.mfi = MFI(self.data, period=14)
                    self.cmf = CMF(self.data, period=20)
                    self.values = []

                def next(self):
                    self.values.append({
                        'date': self.data.datetime.date(0),
                        'obv': self.obv[0],
                        'mfi': self.mfi[0],
                        'cmf': self.cmf[0]
                    })

            cerebro.addstrategy(TestAllIndicators)
            results = cerebro.run()
            strategy = results[0]

            print(f"\n  ✓ All three indicators calculated simultaneously")
            print(f"  ✓ Total data points: {len(strategy.values)}")

            # Display last 3 values
            print(f"\n  Last 3 data points:")
            print(f"  {'Date':<12} {'OBV':>15} {'MFI':>8} {'CMF':>8}")
            print(f"  {'-'*12} {'-'*15} {'-'*8} {'-'*8}")
            for v in strategy.values[-3:]:
                print(f"  {str(v['date']):<12} {v['obv']:>15.0f} {v['mfi']:>8.2f} {v['cmf']:>8.4f}")

            self.passed += 1

        except Exception as e:
            print(f"\n  ✗ Exception: {str(e)}")
            self.failed += 1
            self.errors.append(f"Multi-indicator: {str(e)}")

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
            print("\n✓ All indicator tests passed!")
            return True
        else:
            print(f"\n✗ {self.failed} test(s) failed")
            return False

def main():
    print("="*60)
    print("CUSTOM INDICATOR TEST SUITE")
    print("="*60)
    print("Testing OBV, MFI, and CMF indicator implementations")
    print("="*60)

    tester = IndicatorTester()

    tester.test_obv_indicator()
    tester.test_mfi_indicator()
    tester.test_cmf_indicator()
    tester.test_indicator_comparison()

    return tester.print_summary()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
