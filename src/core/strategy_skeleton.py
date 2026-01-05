from typing import Dict, List, Optional, Any
import backtrader as bt
import datetime


class Strategy_skeleton(bt.Strategy):
    def __init__(self, args: Dict[str, float]):
        self.args = args
        self.trades: List[Dict[str, Any]] = []
        self.order: Optional[bt.Order] = None
        self.val_start: Optional[float] = None
        self.entry_order: Optional[Dict[str, Any]] = None

    def notify_order(self, order: bt.Order) -> None:
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                if self.entry_order is None:
                    self.entry_order = {
                        'date': bt.num2date(order.executed.dt),
                        'price': order.executed.price,
                        'size': order.executed.size,
                        'type': 'LONG' if order.executed.size > 0 else 'SHORT'
                    }
                else:
                    self._record_trade_from_orders(order, is_close=True)
            else:
                if self.entry_order is not None:
                    self._record_trade_from_orders(order, is_close=True)
                else:
                    self.entry_order = {
                        'date': bt.num2date(order.executed.dt),
                        'price': order.executed.price,
                        'size': -order.executed.size,
                        'type': 'SHORT'
                    }
        if not order.alive():
            self.order = None

    def _record_trade_from_orders(self, exit_order: bt.Order, is_close: bool) -> None:
        if self.entry_order is None:
            return
        exit_date = bt.num2date(exit_order.executed.dt)
        exit_price = exit_order.executed.price
        size = abs(self.entry_order['size'])
        entry_price = self.entry_order['price']
        if self.entry_order['type'] == 'LONG':
            pnl_raw = (exit_price - entry_price) * size
        else:
            pnl_raw = (entry_price - exit_price) * size
        pnl = pnl_raw
        pnl_pct = 0.0
        cost = entry_price * size
        if cost != 0:
            pnl_pct = (pnl_raw / cost) * 100
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
        self.entry_order = None

    def log(self, txt: str, dt: Optional[Any] = None) -> None:
        pass

    def start(self) -> None:
        self.order = None
        self.val_start = self.broker.get_cash()

    def next(self) -> None:
        pass
