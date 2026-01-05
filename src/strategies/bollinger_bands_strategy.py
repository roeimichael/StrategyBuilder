import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class Bollinger_three(Strategy_skeleton):
    params = (
        ("period", 20),
        ("devfactor", 2)
    )

    def __init__(self, args):
        super(Bollinger_three, self).__init__(args)
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)
        self.crossover_bot = bt.ind.CrossOver(self.data.close, self.boll.lines.bot)
        self.crossover_mid = bt.ind.CrossOver(self.data.close, self.boll.lines.mid)

    def get_technical_indicators(self):
        """Return technical indicators to be exposed for charting"""
        return {
            'Bollinger_Upper': self.boll.lines.top,
            'Bollinger_Middle': self.boll.lines.mid,
            'Bollinger_Lower': self.boll.lines.bot
        }

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if not self.position:
            if self.crossover_bot < 0:
                self.buy()
                self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
        else:
            if self.crossover_mid > 0:
                self.close()
                self.log('SELL CREATE (LONG), %.2f ' % self.data[0])
