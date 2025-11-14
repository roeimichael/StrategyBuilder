"""
Tests for Risk Manager

Includes scenario tests and stress tests to verify:
- Maximum drawdown stops are triggered correctly
- Portfolio heat limits are enforced
- Position sizing constraints work
- Real-time risk monitoring functions properly
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.risk.risk_manager import RiskManager


class TestRiskManagerBasics(unittest.TestCase):
    """Test basic RiskManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(
            max_portfolio_heat=0.20,
            max_drawdown_pct=0.25,
            max_position_size_pct=0.10
        )
        self.risk_manager.initialize(10000)

    def test_initialization(self):
        """Test RiskManager initialization."""
        self.assertEqual(self.risk_manager.initial_capital, 10000)
        self.assertEqual(self.risk_manager.current_equity, 10000)
        self.assertEqual(self.risk_manager.peak_equity, 10000)
        self.assertEqual(self.risk_manager.current_drawdown, 0.0)
        self.assertFalse(self.risk_manager.trading_halted)

    def test_equity_update_with_profit(self):
        """Test equity update when profitable."""
        result = self.risk_manager.update_equity(11000)

        self.assertTrue(result)
        self.assertEqual(self.risk_manager.current_equity, 11000)
        self.assertEqual(self.risk_manager.peak_equity, 11000)
        self.assertEqual(self.risk_manager.current_drawdown, 0.0)

    def test_equity_update_with_loss(self):
        """Test equity update when losing."""
        # First go up
        self.risk_manager.update_equity(12000)

        # Then go down
        result = self.risk_manager.update_equity(11000)

        self.assertTrue(result)
        self.assertEqual(self.risk_manager.current_equity, 11000)
        self.assertEqual(self.risk_manager.peak_equity, 12000)
        expected_dd = (12000 - 11000) / 12000
        self.assertAlmostEqual(self.risk_manager.current_drawdown, expected_dd, places=4)

    def test_get_statistics(self):
        """Test risk statistics retrieval."""
        stats = self.risk_manager.get_statistics()

        self.assertIn('initial_capital', stats)
        self.assertIn('current_equity', stats)
        self.assertIn('peak_equity', stats)
        self.assertIn('current_drawdown', stats)
        self.assertIn('max_drawdown_limit', stats)
        self.assertIn('trading_halted', stats)


class TestDrawdownLimits(unittest.TestCase):
    """Test drawdown limit enforcement (SCENARIO TESTS)."""

    def test_max_drawdown_stops_trading(self):
        """CRITICAL: Test that max drawdown limit halts trading."""
        # Create risk manager with 25% max drawdown
        risk_manager = RiskManager(max_drawdown_pct=0.25)
        risk_manager.initialize(10000)

        # Simulate equity growth to 15000
        result1 = risk_manager.update_equity(15000)
        self.assertTrue(result1)
        self.assertFalse(risk_manager.trading_halted)
        self.assertEqual(risk_manager.peak_equity, 15000)

        # Simulate drawdown to 12000 (20% from peak - still OK)
        result2 = risk_manager.update_equity(12000)
        self.assertTrue(result2)
        self.assertFalse(risk_manager.trading_halted)
        current_dd = (15000 - 12000) / 15000
        self.assertAlmostEqual(current_dd, 0.20, places=2)

        # Simulate further drawdown to 11000 (26.67% from peak - BREACHED)
        result3 = risk_manager.update_equity(11000)
        self.assertFalse(result3)  # Should return False
        self.assertTrue(risk_manager.trading_halted)  # Trading should be halted
        self.assertIsNotNone(risk_manager.halt_reason)
        self.assertIn("drawdown", risk_manager.halt_reason.lower())

        # Verify drawdown calculation
        breached_dd = (15000 - 11000) / 15000
        self.assertGreater(breached_dd, 0.25)

    def test_drawdown_exactly_at_limit(self):
        """Test behavior when drawdown exactly equals limit."""
        risk_manager = RiskManager(max_drawdown_pct=0.20)
        risk_manager.initialize(10000)

        # Peak at 10000
        # Drop to exactly 20% drawdown
        result = risk_manager.update_equity(8000)

        # Should be halted at exactly the limit
        self.assertFalse(result)
        self.assertTrue(risk_manager.trading_halted)

    def test_multiple_drawdown_events(self):
        """Test risk manager tracks multiple drawdown events."""
        risk_manager = RiskManager(max_drawdown_pct=0.30)
        risk_manager.initialize(10000)

        # First peak and drawdown
        risk_manager.update_equity(12000)  # New peak
        risk_manager.update_equity(10000)  # 16.67% drawdown - OK

        # Recovery to new peak
        risk_manager.update_equity(15000)  # New peak

        # Second drawdown - exceeds limit
        result = risk_manager.update_equity(10000)  # 33.33% drawdown - BREACHED

        self.assertFalse(result)
        self.assertTrue(risk_manager.trading_halted)

    def test_drawdown_below_initial_capital(self):
        """Test drawdown when equity falls below initial capital."""
        risk_manager = RiskManager(max_drawdown_pct=0.15)
        risk_manager.initialize(10000)

        # Grow to 15000
        risk_manager.update_equity(15000)

        # Drop to 9000 (below initial but within drawdown limit from peak)
        # Drawdown = (15000 - 9000) / 15000 = 40%
        result = risk_manager.update_equity(9000)

        self.assertFalse(result)  # Should be halted
        self.assertTrue(risk_manager.trading_halted)


class TestPortfolioHeatLimits(unittest.TestCase):
    """Test portfolio heat limit enforcement."""

    def setUp(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(
            max_portfolio_heat=0.20,
            max_position_size_pct=0.15
        )
        self.risk_manager.initialize(10000)

    def test_can_open_position_within_limits(self):
        """Test opening position within size limits."""
        # 10% position size (within 15% limit)
        can_open = self.risk_manager.can_open_position(
            position_size=1000,
            stop_loss_pct=0.05
        )

        self.assertTrue(can_open)

    def test_position_size_limit_exceeded(self):
        """Test that oversized positions are rejected."""
        # 20% position size (exceeds 15% limit)
        can_open = self.risk_manager.can_open_position(
            position_size=2000,
            stop_loss_pct=0.05
        )

        self.assertFalse(can_open)

        # Check that event was logged
        risk_events = self.risk_manager.risk_events
        self.assertTrue(any(e['event_type'] == 'POSITION_SIZE_LIMIT' for e in risk_events))

    def test_portfolio_heat_limit_exceeded(self):
        """Test that excessive portfolio heat prevents new positions."""
        # Add two positions with 10% risk each
        self.risk_manager.add_position('pos1', 5000, 100, 90)  # 10% stop
        self.risk_manager.add_position('pos2', 5000, 100, 90)  # 10% stop

        # Try to add another position (would exceed 20% portfolio heat)
        can_open = self.risk_manager.can_open_position(
            position_size=2000,
            stop_loss_pct=0.10
        )

        # Should be rejected due to portfolio heat
        self.assertFalse(can_open)

    def test_calculate_portfolio_heat(self):
        """Test portfolio heat calculation."""
        # Add position with known risk
        # Position: $5000, Entry: $100, Stop: $95
        # Shares: 50, Risk per share: $5, Total risk: $250
        self.risk_manager.add_position('pos1', 5000, 100, 95)

        heat = self.risk_manager.calculate_portfolio_heat()

        # Expected risk: 50 shares * $5 = $250
        expected_risk = 50 * 5
        self.assertAlmostEqual(heat, expected_risk, places=0)

    def test_portfolio_heat_with_no_stop_loss(self):
        """Test portfolio heat calculation when no stop loss set."""
        # Add position without stop loss (uses default 2% risk)
        self.risk_manager.add_position('pos1', 1000, 100, None)

        heat = self.risk_manager.calculate_portfolio_heat()

        # Expected: $1000 * 0.02 = $20
        expected_risk = 1000 * 0.02
        self.assertAlmostEqual(heat, expected_risk, places=2)


class TestPositionManagement(unittest.TestCase):
    """Test position tracking and management."""

    def setUp(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager()
        self.risk_manager.initialize(10000)

    def test_add_position(self):
        """Test adding open position."""
        self.risk_manager.add_position('pos1', 1000, 100, 95)

        self.assertEqual(len(self.risk_manager.open_positions), 1)
        self.assertIn('pos1', self.risk_manager.open_positions)

        pos = self.risk_manager.open_positions['pos1']
        self.assertEqual(pos['size'], 1000)
        self.assertEqual(pos['entry_price'], 100)
        self.assertEqual(pos['stop_loss'], 95)

    def test_remove_position(self):
        """Test removing closed position."""
        self.risk_manager.add_position('pos1', 1000, 100, 95)
        self.assertEqual(len(self.risk_manager.open_positions), 1)

        self.risk_manager.remove_position('pos1')
        self.assertEqual(len(self.risk_manager.open_positions), 0)

    def test_multiple_positions(self):
        """Test managing multiple open positions."""
        self.risk_manager.add_position('pos1', 1000, 100, 95)
        self.risk_manager.add_position('pos2', 1500, 50, 48)
        self.risk_manager.add_position('pos3', 2000, 200, 190)

        self.assertEqual(len(self.risk_manager.open_positions), 3)

        # Remove one
        self.risk_manager.remove_position('pos2')
        self.assertEqual(len(self.risk_manager.open_positions), 2)
        self.assertNotIn('pos2', self.risk_manager.open_positions)


class TestRiskAdjustedPositionSizing(unittest.TestCase):
    """Test risk-adjusted position sizing calculations."""

    def setUp(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(max_position_size_pct=0.20)
        self.risk_manager.initialize(10000)

    def test_position_size_calculation(self):
        """Test position size based on risk."""
        # Risk 2% of $10,000 = $200
        # Entry: $100, Stop: $95, Risk per share: $5
        # Position size: $200 / $5 = 40 shares = $4000
        # BUT max_position_size_pct is 0.20 = $2000 max
        # So should be capped at $2000
        size = self.risk_manager.get_risk_adjusted_position_size(
            entry_price=100,
            stop_loss=95,
            risk_per_trade_pct=0.02
        )

        expected_size = 2000  # Capped by max_position_size_pct (20% of $10,000)
        self.assertAlmostEqual(size, expected_size, places=0)

    def test_position_size_with_max_limit(self):
        """Test that position size respects maximum limit."""
        # Max position: 20% of $10,000 = $2000
        # Calculated size would be larger, but should be capped
        size = self.risk_manager.get_risk_adjusted_position_size(
            entry_price=10,
            stop_loss=9,
            risk_per_trade_pct=0.10  # 10% risk would normally be huge
        )

        max_allowed = 10000 * 0.20  # $2000
        self.assertLessEqual(size, max_allowed)

    def test_position_size_with_zero_risk(self):
        """Test position sizing when stop equals entry (zero risk)."""
        size = self.risk_manager.get_risk_adjusted_position_size(
            entry_price=100,
            stop_loss=100,  # Same as entry
            risk_per_trade_pct=0.02
        )

        self.assertEqual(size, 0)


class TestTrailingStop(unittest.TestCase):
    """Test trailing stop functionality."""

    def test_trailing_stop_triggered(self):
        """Test that trailing stop halts trading."""
        risk_manager = RiskManager(
            enable_trailing_stop=True,
            trailing_stop_pct=0.15  # 15% trailing stop
        )
        risk_manager.initialize(10000)

        # Equity grows to 15000
        risk_manager.update_equity(15000)
        self.assertEqual(risk_manager.peak_equity, 15000)

        # Drop to 13000 (13.33% from peak - still OK)
        result1 = risk_manager.update_equity(13000)
        self.assertTrue(result1)
        self.assertFalse(risk_manager.trading_halted)

        # Drop to 12500 (16.67% from peak - TRIGGERED)
        result2 = risk_manager.update_equity(12500)
        self.assertFalse(result2)
        self.assertTrue(risk_manager.trading_halted)
        self.assertIn("trailing stop", risk_manager.halt_reason.lower())

    def test_trailing_stop_disabled(self):
        """Test that trailing stop doesn't trigger when disabled."""
        risk_manager = RiskManager(
            enable_trailing_stop=False,
            max_drawdown_pct=0.50  # High limit to avoid regular drawdown stop
        )
        risk_manager.initialize(10000)

        risk_manager.update_equity(15000)
        result = risk_manager.update_equity(12000)  # 20% drop

        # Should still be trading (no trailing stop)
        self.assertTrue(result)
        self.assertFalse(risk_manager.trading_halted)


class TestEquityCurve(unittest.TestCase):
    """Test equity curve generation."""

    def test_get_equity_curve(self):
        """Test equity curve DataFrame generation."""
        risk_manager = RiskManager()
        risk_manager.initialize(10000)

        # Update equity multiple times
        timestamps = [
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            datetime(2024, 1, 3),
            datetime(2024, 1, 4)
        ]

        equities = [10000, 10500, 10200, 11000]

        for ts, eq in zip(timestamps, equities):
            risk_manager.update_equity(eq, timestamp=ts)

        # Get equity curve
        df = risk_manager.get_equity_curve()

        self.assertEqual(len(df), 5)  # Initial + 4 updates
        self.assertIn('timestamp', df.columns)
        self.assertIn('equity', df.columns)
        self.assertIn('peak', df.columns)
        self.assertIn('drawdown', df.columns)
        self.assertIn('drawdown_pct', df.columns)

    def test_equity_curve_drawdown_calculation(self):
        """Test that equity curve correctly calculates drawdowns."""
        risk_manager = RiskManager()
        risk_manager.initialize(10000)

        risk_manager.update_equity(12000)  # New peak
        risk_manager.update_equity(11000)  # Drawdown

        df = risk_manager.get_equity_curve()

        # Last row should show drawdown
        last_row = df.iloc[-1]
        expected_dd = (12000 - 11000) / 12000

        self.assertAlmostEqual(last_row['drawdown'], expected_dd, places=4)


class TestStressScenarios(unittest.TestCase):
    """STRESS TEST SCENARIOS."""

    def test_flash_crash_scenario(self):
        """Test risk manager during flash crash (sudden large drop)."""
        risk_manager = RiskManager(max_drawdown_pct=0.30)
        risk_manager.initialize(100000)

        # Normal growth
        risk_manager.update_equity(110000)
        risk_manager.update_equity(120000)

        # Flash crash: 40% drop in single update
        result = risk_manager.update_equity(72000)

        # Should be halted immediately
        self.assertFalse(result)
        self.assertTrue(risk_manager.trading_halted)

        # Drawdown should be 40%
        expected_dd = (120000 - 72000) / 120000
        self.assertAlmostEqual(risk_manager.current_drawdown, expected_dd, places=2)

    def test_slow_bleed_scenario(self):
        """Test risk manager during slow gradual decline."""
        risk_manager = RiskManager(max_drawdown_pct=0.20)
        risk_manager.initialize(10000)

        equities = [10000, 9800, 9600, 9400, 9200, 9000, 8800, 8600, 8400, 8000]

        halted_at = None
        for i, eq in enumerate(equities):
            result = risk_manager.update_equity(eq)
            if not result:
                halted_at = i
                break

        # Should be halted before reaching 8000 (20% from 10000)
        self.assertIsNotNone(halted_at)
        self.assertTrue(risk_manager.trading_halted)
        self.assertLessEqual(risk_manager.current_equity, 8000)

    def test_volatility_whipsaw_scenario(self):
        """Test risk manager during high volatility (up and down)."""
        risk_manager = RiskManager(max_drawdown_pct=0.25)
        risk_manager.initialize(10000)

        # Volatile movements
        equities = [10000, 11000, 9500, 12000, 10500, 8500, 11500, 9000, 8500]

        halted = False
        for eq in equities:
            result = risk_manager.update_equity(eq)
            if not result:
                halted = True
                break

        # Peak was 12000, final 8500 = 29.17% drawdown
        # Should be halted
        self.assertTrue(halted)
        self.assertTrue(risk_manager.trading_halted)

    def test_recovery_after_drawdown(self):
        """Test that risk manager doesn't reset after recovery."""
        risk_manager = RiskManager(max_drawdown_pct=0.30)
        risk_manager.initialize(10000)

        # Drawdown scenario
        risk_manager.update_equity(15000)  # Peak
        risk_manager.update_equity(11000)  # 26.67% drawdown

        # Recover
        risk_manager.update_equity(14000)  # Recovery but not new peak

        # Another drawdown from new lower peak should trigger
        result = risk_manager.update_equity(9500)  # From 15000 peak = 36.67%

        self.assertFalse(result)
        self.assertTrue(risk_manager.trading_halted)


class TestResetFunctionality(unittest.TestCase):
    """Test reset functionality."""

    def test_reset_clears_state(self):
        """Test that reset clears all state."""
        risk_manager = RiskManager()
        risk_manager.initialize(10000)

        # Modify state
        risk_manager.update_equity(12000)
        risk_manager.add_position('pos1', 1000, 100, 95)
        risk_manager.update_equity(8000)  # Create drawdown

        # Reset
        risk_manager.reset()

        # Should be back to initial state
        self.assertEqual(risk_manager.current_equity, 10000)
        self.assertEqual(risk_manager.peak_equity, 10000)
        self.assertEqual(risk_manager.current_drawdown, 0.0)
        self.assertEqual(len(risk_manager.open_positions), 0)
        self.assertEqual(len(risk_manager.risk_events), 0)
        self.assertFalse(risk_manager.trading_halted)


if __name__ == '__main__':
    unittest.main(verbosity=2)
