from typing import Dict, List, Optional, Any
import backtrader as bt
import datetime


class Strategy_skeleton(bt.Strategy):
    def __init__(self, args: Dict[str, float]):
        self.args = args
        self.trades: List[Dict[str, Any]] = []
        self.order: Optional[bt.Order] = None
        self.val_start: Optional[float] = None
        self.entry_order: Optional[Dict[str, Any]] = None  # Track entry order details

    def notify_order(self, order: bt.Order) -> None:
        """Track executed orders to build trade history"""
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted - do nothing yet
            return

        if order.status in [order.Completed]:
            # Order completed - track it
            if order.isbuy():
                # This is an entry order (or closing a short)
                if self.entry_order is None:
                    # Opening a new position
                    self.entry_order = {
                        'date': bt.num2date(order.executed.dt),
                        'price': order.executed.price,
                        'size': order.executed.size,
                        'type': 'LONG' if order.executed.size > 0 else 'SHORT'
                    }
                    print(f"[DEBUG] Entry order recorded: {self.entry_order['type']} {abs(self.entry_order['size'])} @ {self.entry_order['price']:.2f}")
                else:
                    # Closing a short position
                    self._record_trade_from_orders(order, is_close=True)
            else:
                # This is an exit order (or opening a short)
                if self.entry_order is not None:
                    # Closing a long position
                    self._record_trade_from_orders(order, is_close=True)
                else:
                    # Opening a short position
                    self.entry_order = {
                        'date': bt.num2date(order.executed.dt),
                        'price': order.executed.price,
                        'size': -order.executed.size,  # Negative for short
                        'type': 'SHORT'
                    }
                    print(f"[DEBUG] Entry order recorded: SHORT {abs(self.entry_order['size'])} @ {self.entry_order['price']:.2f}")

        if order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f"[DEBUG] Order {order.ref} was canceled/rejected")

        # Clear the order reference
        if not order.alive():
            self.order = None

    def _record_trade_from_orders(self, exit_order: bt.Order, is_close: bool) -> None:
        """Record a completed trade from entry and exit orders"""
        if self.entry_order is None:
            print("[DEBUG] WARNING: Exit order but no entry order found!")
            return

        exit_date = bt.num2date(exit_order.executed.dt)
        exit_price = exit_order.executed.price
        size = abs(self.entry_order['size'])
        entry_price = self.entry_order['price']

        # Calculate P&L
        if self.entry_order['type'] == 'LONG':
            pnl_raw = (exit_price - entry_price) * size
        else:  # SHORT
            pnl_raw = (entry_price - exit_price) * size

        # Account for commission (approximate)
        pnl = pnl_raw  # Commission is already deducted by broker

        pnl_pct = 0.0
        cost = entry_price * size
        if cost != 0:
            pnl_pct = (pnl_raw / cost) * 100

        # Calculate bar duration (approximate)
        bar_duration = (exit_date - self.entry_order['date']).days

        trade_dict = {
            'entry_date': self.entry_order['date'],
            'exit_date': exit_date,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'size': size,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'bar_duration': bar_duration,
            'type': self.entry_order['type']
        }

        self.trades.append(trade_dict)
        print(f"[DEBUG] Trade recorded: {trade_dict['type']} - Entry: {entry_price:.2f} ({self.entry_order['date'].strftime('%Y-%m-%d')}), Exit: {exit_price:.2f} ({exit_date.strftime('%Y-%m-%d')}), PNL: {pnl:.2f} ({pnl_pct:.2f}%)")

        # Clear entry order for next trade
        self.entry_order = None

    def log(self, txt: str, dt: Optional[Any] = None) -> None:
        pass

    def start(self) -> None:
        self.order = None
        self.val_start = self.broker.get_cash()

    def next(self) -> None:
        pass