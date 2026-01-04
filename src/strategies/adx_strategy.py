import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class adx_strat(Strategy_skeleton):

    def __init__(self, args):
        super(adx_strat, self).__init__(args)
        self.type = 0
        self.adx = bt.indicators.AverageDirectionalMovementIndex()
        self.ma20 = bt.indicators.MovingAverageSimple(period=20)
        self.ma50 = bt.indicators.MovingAverageSimple(period=50)
        self.boll = bt.indicators.BollingerBands(period=14)
        self.ma_cross = bt.ind.CrossOver(self.ma20, self.ma50)
        self.boll_cross_bot = bt.ind.CrossOver(self.data.close, self.boll.lines.bot)
        self.boll_cross_mid = bt.ind.CrossOver(self.data.close, self.boll.lines.mid)

    def next(self):
        self.log('Close, %.2f' % self.data[0])
        if self.order:
            return
        if len(self) < 51:
            return

        if self.type == 0:
            if self.adx[-1] >= 25:
                if self.ma_cross > 0:
                    self.buy()
                    self.log('BUY CREATE (LONG TRENDY), %.2f ' % self.data[0])
                    self.type = 1
            else:
                if self.boll_cross_bot < 0:
                    self.buy()
                    self.log('BUY CREATE (LONG STABLE), %.2f ' % self.data[0])
                    self.type = 2
        else:
            if self.type == 1:
                if self.ma_cross < 0:
                    self.close()
                    self.log('SELL CREATE (LONG TRENDY), %.2f ' % self.data[0])
                    self.type = 0
            elif self.type == 2:
                if self.boll_cross_mid > 0:
                    self.close()
                    self.log('SELL CREATE (LONG STABLE), %.2f ' % self.data[0])
                    self.type = 0
