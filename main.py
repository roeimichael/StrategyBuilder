from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from run_strategy import Run_strategy
from dateutil.relativedelta import relativedelta
from TEMA_MACD_NEW import TEMA_MACD_NEW
from alligator_strategy import Alligator_strategy
from bollinger_three import Bollinger_three
import datetime


if __name__ == '__main__':

    ticker = "AAPL"
    start_date = datetime.date.today() - relativedelta(years=1)

    # end_date = "2021-09-23"
    # intervals = {"30m": "2021-09-01", "1h": "2021-08-25", "90m": "2021-08-01", "1d": "2021-06-01"}
    interval = "1h"
    strategy = Bollinger_three
    parameters = dict(cash=10000,
                      macd1=12,
                      macd2=26,
                      macdsig=9,
                      atrperiod=14,
                      atrdist=2.0,
                      order_pct=1.0, )

    run_cerebro = Run_strategy(parameters, strategy)
    run_cerebro.runstrat(ticker, start_date, interval)
