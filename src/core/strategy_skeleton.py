"""Base strategy class for all backtrader strategies"""
import backtrader as bt


class Strategy_skeleton(bt.Strategy):
    """Base strategy with trade tracking and debugging utilities"""

    def __init__(self, args):
        self.args = args
        self.size = 0
        self.trades = []
        self.last_buy_price = None
        self.last_buy_date = None
        self.last_buy_size = None
        self.order = None
        self.val_start = None

    def notify_order(self, order):
        """Track order execution and record trade details"""
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

    def log(self, txt, dt=None):
        """Log message with timestamp"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def start(self):
        """Initialize strategy"""
        self.order = None
        self.val_start = self.broker.get_cash()

    def next(self):
        """Main strategy logic - override in subclasses"""
        pass

    def stop(self):
        """Calculate and print final ROI"""
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print(f'ROI: {100.0 * self.roi:.2f}%')
