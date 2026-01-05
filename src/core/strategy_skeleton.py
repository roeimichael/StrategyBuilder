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

        # Get the trade size - use value if history is not available
        initial_size = 0
        if len(trade.history) > 0:
            initial_size = trade.history[0].size
        elif trade.size != 0:
            # Fallback to trade.size if history is not available
            initial_size = abs(trade.size)

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

        trade_dict = {
            'entry_date': entry_dt,
            'exit_date': exit_dt,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'size': initial_size,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'bar_duration': trade.barlen,
            'type': 'LONG' if initial_size > 0 else 'SHORT'
        }

        self.trades.append(trade_dict)
        print(f"[DEBUG] Trade added to markers: {trade.ref} - {trade_dict['type']} at {trade_dict['entry_price']:.2f}, closed at {trade_dict['exit_price']:.2f}, PNL: {pnl:.2f}")

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