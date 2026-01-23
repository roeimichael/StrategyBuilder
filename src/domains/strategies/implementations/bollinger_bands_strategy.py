import backtrader as bt
from src.shared.strategy_skeleton import Strategy_skeleton


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
        self.crossover_top = bt.ind.CrossOver(self.data.close, self.boll.lines.top)
        self.position_type = 0

    def get_technical_indicators(self):
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
                self.position_type = 1
                self.log('BUY CREATE (LONG), %.2f ' % self.data[0])
            elif self.crossover_top > 0:
                self.sell()
                self.position_type = -1
                self.log('SELL CREATE (SHORT), %.2f ' % self.data[0])
        else:
            if self.position_type == 1:
                if self.crossover_mid > 0:
                    self.close()
                    self.position_type = 0
                    self.log('SELL CREATE (LONG EXIT), %.2f ' % self.data[0])
            elif self.position_type == -1:
                if self.crossover_mid < 0:
                    self.close()
                    self.position_type = 0
                    self.log('BUY CREATE (SHORT EXIT), %.2f' % self.data[0])
