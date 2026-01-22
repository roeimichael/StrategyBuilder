import backtrader as bt
from ..core.strategy_skeleton import Strategy_skeleton


class RSI_Stochastic(Strategy_skeleton):
    params = (
        ("rsi_period", 14),
        ("rsi_oversold", 30),
        ("rsi_overbought", 70),
        ("stoch_period", 14),
        ("stoch_oversold", 20),
        ("stoch_overbought", 80)
    )

    def __init__(self, args):
        super(RSI_Stochastic, self).__init__(args)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.stoch = bt.indicators.Stochastic(self.data, period=self.p.stoch_period)
        self.position_type = 0

    def get_technical_indicators(self):
        return {
            'RSI': self.rsi,
            'Stochastic_K': self.stoch.percK,
            'Stochastic_D': self.stoch.percD
        }

    def next(self):
        self.log('Close, %.2f' % self.data[0])

        if self.order:
            return

        if not self.position:
            if len(self) < max(self.p.rsi_period, self.p.stoch_period):
                return
            if (self.rsi[0] < self.p.rsi_oversold and
                    self.stoch.percK[0] < self.p.stoch_oversold):
                self.buy()
                self.position_type = 1
                self.log(f'BUY CREATE (LONG - RSI: {self.rsi[0]:.2f}, Stoch: {self.stoch.percK[0]:.2f}), %.2f' % self.data[0])
            elif (self.rsi[0] > self.p.rsi_overbought and
                    self.stoch.percK[0] > self.p.stoch_overbought):
                self.sell()
                self.position_type = -1
                self.log(f'SELL CREATE (SHORT - RSI: {self.rsi[0]:.2f}, Stoch: {self.stoch.percK[0]:.2f}), %.2f' % self.data[0])
        else:
            if self.position_type == 1:
                if (self.rsi[0] > self.p.rsi_overbought or
                        self.stoch.percK[0] > self.p.stoch_overbought):
                    self.close()
                    self.position_type = 0
                    self.log(f'SELL CREATE (LONG EXIT - RSI: {self.rsi[0]:.2f}, Stoch: {self.stoch.percK[0]:.2f}), %.2f' % self.data[0])
            elif self.position_type == -1:
                if (self.rsi[0] < self.p.rsi_oversold or
                        self.stoch.percK[0] < self.p.stoch_oversold):
                    self.close()
                    self.position_type = 0
                    self.log(f'BUY CREATE (SHORT EXIT - RSI: {self.rsi[0]:.2f}, Stoch: {self.stoch.percK[0]:.2f}), %.2f' % self.data[0])
