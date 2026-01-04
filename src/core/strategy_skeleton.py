from typing import Dict, List, Optional, Any
import backtrader as bt
import datetime


class Strategy_skeleton(bt.Strategy):
    def __init__(self, args: Dict[str, float]):
        self.args = args
        self.trades: List[Dict[str, Any]] = []
        self.order: Optional[bt.Order] = None
        self.val_start: Optional[float] = None

    def notify_trade(self, trade: bt.Trade) -> None:
        if not trade.isclosed:
            return

        initial_size = 0
        if len(trade.history) > 0:
            initial_size = trade.history[0].size

        if initial_size == 0:
            return

        pnl = trade.pnlcomm
        entry_price = trade.price
        exit_price = (trade.pnl / initial_size) + entry_price

        pnl_pct = 0.0
        cost = entry_price * initial_size
        if cost != 0:
            pnl_pct = (trade.pnl / abs(cost)) * 100

        entry_dt = bt.num2date(trade.dtopen)
        exit_dt = bt.num2date(trade.dtclose)

        self.trades.append({
            'entry_date': entry_dt,
            'exit_date': exit_dt,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'size': initial_size,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'bar_duration': trade.barlen,
            'type': 'LONG' if initial_size > 0 else 'SHORT'
        })

    def notify_order(self, order: bt.Order) -> None:
        if not order.alive():
            self.order = None

    def log(self, txt: str, dt: Optional[Any] = None) -> None:
        pass

    def start(self) -> None:
        self.order = None
        self.val_start = self.broker.get_cash()

    def next(self) -> None:
        pass