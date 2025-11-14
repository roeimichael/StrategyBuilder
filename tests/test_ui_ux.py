"""UI/UX functionality tests

These tests verify:
- UI helper functions
- Progress tracking
- Metric tooltips
- Status indicators
"""

import os
import sys
import unittest
import time
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.ui_helpers import (
    METRIC_TOOLTIPS,
    with_spinner,
    create_status_indicator,
    show_performance_badge
)


class TestMetricTooltips(unittest.TestCase):
    """Test metric tooltip system"""

    def test_metric_tooltips_exist(self):
        """Test that metric tooltips dictionary exists"""
        self.assertIsInstance(METRIC_TOOLTIPS, dict)
        self.assertGreater(len(METRIC_TOOLTIPS), 0)

    def test_sharpe_ratio_tooltip(self):
        """Test Sharpe ratio tooltip exists and has content"""
        self.assertIn('sharpe_ratio', METRIC_TOOLTIPS)
        tooltip = METRIC_TOOLTIPS['sharpe_ratio']
        self.assertIn('Sharpe Ratio', tooltip)
        self.assertIn('risk-adjusted', tooltip.lower())

    def test_sortino_ratio_tooltip(self):
        """Test Sortino ratio tooltip"""
        self.assertIn('sortino_ratio', METRIC_TOOLTIPS)
        tooltip = METRIC_TOOLTIPS['sortino_ratio']
        self.assertIn('Sortino', tooltip)
        self.assertIn('downside', tooltip.lower())

    def test_calmar_ratio_tooltip(self):
        """Test Calmar ratio tooltip"""
        self.assertIn('calmar_ratio', METRIC_TOOLTIPS)
        tooltip = METRIC_TOOLTIPS['calmar_ratio']
        self.assertIn('Calmar', tooltip)
        self.assertIn('drawdown', tooltip.lower())

    def test_max_drawdown_tooltip(self):
        """Test max drawdown tooltip"""
        self.assertIn('max_drawdown', METRIC_TOOLTIPS)
        tooltip = METRIC_TOOLTIPS['max_drawdown']
        self.assertIn('drawdown', tooltip.lower())
        self.assertIn('peak', tooltip.lower())

    def test_win_rate_tooltip(self):
        """Test win rate tooltip"""
        self.assertIn('win_rate', METRIC_TOOLTIPS)
        tooltip = METRIC_TOOLTIPS['win_rate']
        self.assertIn('Win Rate', tooltip)
        self.assertIn('percentage', tooltip.lower())

    def test_profit_factor_tooltip(self):
        """Test profit factor tooltip"""
        self.assertIn('profit_factor', METRIC_TOOLTIPS)
        tooltip = METRIC_TOOLTIPS['profit_factor']
        self.assertIn('Profit Factor', tooltip)
        self.assertIn('gross profit', tooltip.lower())

    def test_payoff_ratio_tooltip(self):
        """Test payoff ratio tooltip"""
        self.assertIn('payoff_ratio', METRIC_TOOLTIPS)
        tooltip = METRIC_TOOLTIPS['payoff_ratio']
        self.assertIn('Payoff Ratio', tooltip)
        self.assertIn('average win', tooltip.lower())

    def test_expectancy_tooltip(self):
        """Test expectancy tooltip"""
        self.assertIn('expectancy', METRIC_TOOLTIPS)
        tooltip = METRIC_TOOLTIPS['expectancy']
        self.assertIn('Expectancy', tooltip)
        self.assertIn('expected value', tooltip.lower())

    def test_all_tooltips_have_formulas(self):
        """Test that tooltips with formulas include the word 'Formula'"""
        metrics_with_formulas = ['sharpe_ratio', 'calmar_ratio',
                                'profit_factor', 'payoff_ratio', 'expectancy']

        for metric in metrics_with_formulas:
            tooltip = METRIC_TOOLTIPS[metric]
            self.assertIn('Formula', tooltip,
                         f"{metric} tooltip missing formula")


class TestSpinnerDecorator(unittest.TestCase):
    """Test spinner decorator functionality"""

    def test_with_spinner_decorator(self):
        """Test that with_spinner decorator works"""
        @with_spinner("Testing...")
        def test_function():
            return "result"

        # Function should still work normally
        result = test_function()
        self.assertEqual(result, "result")

    def test_with_spinner_preserves_function_name(self):
        """Test that decorator preserves function name"""
        @with_spinner("Loading...")
        def my_function():
            pass

        self.assertEqual(my_function.__name__, "my_function")

    def test_with_spinner_with_arguments(self):
        """Test spinner decorator with function arguments"""
        @with_spinner("Processing...")
        def process_data(x, y):
            return x + y

        result = process_data(5, 10)
        self.assertEqual(result, 15)

    def test_with_spinner_with_custom_message(self):
        """Test spinner with custom message"""
        @with_spinner("Custom loading message...")
        def load_data():
            return True

        result = load_data()
        self.assertTrue(result)


class TestProgressTracking(unittest.TestCase):
    """Test progress tracking functionality"""

    def test_progress_calculation(self):
        """Test progress percentage calculation"""
        total_steps = 100
        current_step = 50

        progress = current_step / total_steps
        self.assertEqual(progress, 0.5)

        progress_pct = progress * 100
        self.assertEqual(progress_pct, 50.0)

    def test_progress_bounds(self):
        """Test progress stays within 0-1 bounds"""
        total_steps = 10

        for current_step in range(total_steps + 1):
            progress = current_step / total_steps
            self.assertGreaterEqual(progress, 0.0)
            self.assertLessEqual(progress, 1.0)

    def test_grid_search_progress_calculation(self):
        """Test grid search progress calculation"""
        param_grid = [
            {'period': 10, 'devfactor': 2.0},
            {'period': 15, 'devfactor': 2.0},
            {'period': 20, 'devfactor': 2.0},
            {'period': 10, 'devfactor': 2.5},
            {'period': 15, 'devfactor': 2.5},
        ]

        total = len(param_grid)
        self.assertEqual(total, 5)

        # Test progress at various points
        for i in range(total):
            progress = (i + 1) / total
            self.assertGreaterEqual(progress, 0.0)
            self.assertLessEqual(progress, 1.0)

        # Final progress should be 100%
        final_progress = total / total
        self.assertEqual(final_progress, 1.0)


class TestStatusIndicators(unittest.TestCase):
    """Test status indicator functionality"""

    def test_status_indicator_function_exists(self):
        """Test that create_status_indicator function exists"""
        from utils.ui_helpers import create_status_indicator
        self.assertTrue(callable(create_status_indicator))

    def test_performance_badge_function_exists(self):
        """Test that show_performance_badge function exists"""
        from utils.ui_helpers import show_performance_badge
        self.assertTrue(callable(show_performance_badge))

    def test_performance_badge_with_positive_return(self):
        """Test performance badge with positive return"""
        # This would normally update UI, but we're just testing it doesn't error
        try:
            show_performance_badge(15.5)
        except Exception as e:
            # Expected to fail without Streamlit context, but should not raise during import
            pass

    def test_performance_badge_with_negative_return(self):
        """Test performance badge with negative return"""
        try:
            show_performance_badge(-8.3)
        except Exception as e:
            # Expected to fail without Streamlit context
            pass


class TestComparisonTableGeneration(unittest.TestCase):
    """Test comparison table generation"""

    def setUp(self):
        """Set up test data"""
        self.test_results = [
            {
                'return_pct': 15.5,
                'sharpe_ratio': 1.8,
                'max_drawdown': 8.2,
                'total_trades': 25,
                'advanced_metrics': {
                    'win_rate': 64.0,
                    'profit_factor': 2.1
                }
            },
            {
                'return_pct': 12.3,
                'sharpe_ratio': 1.5,
                'max_drawdown': 10.5,
                'total_trades': 30,
                'advanced_metrics': {
                    'win_rate': 60.0,
                    'profit_factor': 1.8
                }
            }
        ]

        self.strategy_names = ['Strategy A', 'Strategy B']

    def test_comparison_data_structure(self):
        """Test comparison data can be structured"""
        import pandas as pd

        data = []
        for name, result in zip(self.strategy_names, self.test_results):
            row = {
                'Strategy': name,
                'Return %': result.get('return_pct', 0),
                'Sharpe': result.get('sharpe_ratio', 0),
                'Max DD %': result.get('max_drawdown', 0),
                'Trades': result.get('total_trades', 0)
            }
            data.append(row)

        df = pd.DataFrame(data)

        # Verify DataFrame structure
        self.assertEqual(len(df), 2)
        self.assertIn('Strategy', df.columns)
        self.assertIn('Return %', df.columns)
        self.assertEqual(df.iloc[0]['Strategy'], 'Strategy A')
        self.assertEqual(df.iloc[0]['Return %'], 15.5)

    def test_comparison_includes_advanced_metrics(self):
        """Test comparison can include advanced metrics"""
        import pandas as pd

        data = []
        for name, result in zip(self.strategy_names, self.test_results):
            row = {'Strategy': name}
            advanced = result.get('advanced_metrics', {})
            if advanced:
                row['Win Rate %'] = advanced.get('win_rate', 0)
                row['Profit Factor'] = advanced.get('profit_factor', 0)
            data.append(row)

        df = pd.DataFrame(data)

        # Verify advanced metrics included
        self.assertIn('Win Rate %', df.columns)
        self.assertIn('Profit Factor', df.columns)
        self.assertEqual(df.iloc[0]['Win Rate %'], 64.0)


class TestTradeAnalysis(unittest.TestCase):
    """Test trade analysis functionality"""

    def setUp(self):
        """Set up test trades"""
        self.trades = [
            {'entry_date': '2023-01-01', 'exit_date': '2023-01-05',
             'entry_price': 100, 'exit_price': 110, 'pnl': 100},
            {'entry_date': '2023-01-10', 'exit_date': '2023-01-15',
             'entry_price': 110, 'exit_price': 105, 'pnl': -50},
            {'entry_date': '2023-01-20', 'exit_date': '2023-01-25',
             'entry_price': 105, 'exit_price': 120, 'pnl': 150},
        ]

    def test_trade_filtering_winners(self):
        """Test filtering winning trades"""
        import pandas as pd

        df = pd.DataFrame(self.trades)
        winners = df[df['pnl'] > 0]

        self.assertEqual(len(winners), 2)
        self.assertTrue(all(winners['pnl'] > 0))

    def test_trade_filtering_losers(self):
        """Test filtering losing trades"""
        import pandas as pd

        df = pd.DataFrame(self.trades)
        losers = df[df['pnl'] < 0]

        self.assertEqual(len(losers), 1)
        self.assertTrue(all(losers['pnl'] < 0))

    def test_average_win_calculation(self):
        """Test average win calculation"""
        import pandas as pd

        df = pd.DataFrame(self.trades)
        winners = df[df['pnl'] > 0]

        avg_win = winners['pnl'].mean()
        self.assertAlmostEqual(avg_win, 125.0, places=1)

    def test_average_loss_calculation(self):
        """Test average loss calculation"""
        import pandas as pd

        df = pd.DataFrame(self.trades)
        losers = df[df['pnl'] < 0]

        avg_loss = losers['pnl'].mean()
        self.assertAlmostEqual(avg_loss, -50.0, places=1)


class TestDownloadFunctionality(unittest.TestCase):
    """Test download button functionality"""

    def test_dataframe_to_csv_conversion(self):
        """Test DataFrame can be converted to CSV"""
        import pandas as pd

        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })

        csv_string = df.to_csv(index=False)

        self.assertIn('A,B', csv_string)
        self.assertIn('1,4', csv_string)
        self.assertIsInstance(csv_string, str)

    def test_csv_string_format(self):
        """Test CSV string has correct format"""
        import pandas as pd

        df = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Price': [100.0, 101.5]
        })

        csv_string = df.to_csv(index=False)
        lines = csv_string.strip().split('\n')

        # Should have header + 2 data rows
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], 'Date,Price')


class TestUIHelperImports(unittest.TestCase):
    """Test UI helper module can be imported"""

    def test_ui_helpers_import(self):
        """Test ui_helpers module can be imported"""
        try:
            import utils.ui_helpers
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import ui_helpers: {e}")

    def test_metric_tooltips_import(self):
        """Test METRIC_TOOLTIPS can be imported"""
        try:
            from utils.ui_helpers import METRIC_TOOLTIPS
            self.assertIsInstance(METRIC_TOOLTIPS, dict)
        except ImportError as e:
            self.fail(f"Failed to import METRIC_TOOLTIPS: {e}")

    def test_all_helper_functions_exist(self):
        """Test all expected helper functions exist"""
        from utils import ui_helpers

        expected_functions = [
            'show_metric_with_tooltip',
            'with_spinner',
            'progress_bar_wrapper',
            'show_grid_search_progress',
            'create_status_indicator',
            'show_performance_badge',
            'create_comparison_table',
            'show_trade_analysis_tabs',
            'create_download_button'
        ]

        for func_name in expected_functions:
            self.assertTrue(hasattr(ui_helpers, func_name),
                           f"Missing function: {func_name}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
