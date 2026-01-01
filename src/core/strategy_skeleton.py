from typing import Dict, List, Optional, Any
import backtrader as bt

class Strategy_skeleton(bt.Strategy):
    def __init__(self, args: Dict[str, float]):
        self.args = args
        self.size = 0
        self.trades: List[Dict[str, Any]] = []
        self.last_buy_price: Optional[float] = None
        self.last_buy_date: Optional[Any] = None
        self.last_buy_size: Optional[float] = None
        self.order: Optional[bt.Order] = None
        self.val_start: Optional[float] = None

    def notify_order(self, order: bt.Order) -> None:
        if order.status == order.Completed:
            if order.isbuy():
                self.last_buy_price = order.executed.price
                self.last_buy_date = self.data.datetime.date(0)
                self.last_buy_size = order.executed.size
            elif order.issell() and self.last_buy_price is not None:
                pnl = (order.executed.price - self.last_buy_price) * self.last_buy_size
                pnl_pct = ((order.executed.price / self.last_buy_price) - 1) * 100
                self.trades.append({
                    'entry_date': self.last_buy_date,
                    'exit_date': self.data.datetime.date(0),
                    'entry_price': self.last_buy_price,
                    'exit_price': order.executed.price,
                    'size': self.last_buy_size,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'type': 'LONG'
                })
        if not order.alive():
            self.order = None

    def log(self, txt: str, dt: Optional[Any] = None) -> None:
        dt = dt or self.datas[0].datetime.date(0)

    def start(self) -> None:
        self.order = None
        self.val_start = self.broker.get_cash()

    def next(self) -> None:
        pass

    def stop(self) -> None:
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
