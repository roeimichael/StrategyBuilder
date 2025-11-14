"""Stock Monitoring Script for Live Trading"""

import sys
import os
import argparse
import datetime
import yfinance as yf

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import TradingDatabase
from core.run_strategy import Run_strategy
from strategies.bollinger_bands_strategy import Bollinger_three
from strategies.tema_macd_strategy import TEMA_MACD
from strategies.alligator_strategy import Alligator_strategy
from strategies.adx_strategy import adx_strat
from strategies.cmf_atr_macd_strategy import MACD_CMF_ATR_Strategy
from strategies.tema_crossover_strategy import Tema20_tema60
from strategies.rsi_stochastic_strategy import RSI_Stochastic
from strategies.williams_r_strategy import Williams_R
from strategies.mfi_strategy import MFI_Strategy
from strategies.cci_atr_strategy import CCI_ATR_Strategy
from strategies.momentum_multi_strategy import Momentum_Multi
from strategies.keltner_channel_strategy import Keltner_Channel


# Strategy mapping
STRATEGIES = {
    'Bollinger Bands': Bollinger_three,
    'TEMA + MACD': TEMA_MACD,
    'Alligator': Alligator_strategy,
    'ADX Adaptive': adx_strat,
    'CMF + ATR + MACD': MACD_CMF_ATR_Strategy,
    'TEMA Crossover': Tema20_tema60,
    'RSI + Stochastic': RSI_Stochastic,
    'Williams %R': Williams_R,
    'MFI (Money Flow)': MFI_Strategy,
    'CCI + ATR': CCI_ATR_Strategy,
    'Momentum Multi': Momentum_Multi,
    'Keltner Channel': Keltner_Channel,
}


def get_latest_price(ticker: str) -> float:
    """Get latest price for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return hist['Close'].iloc[-1]
        return None
    except Exception as e:
        print(f"  Error getting price for {ticker}: {str(e)}")
        return None


def check_strategy_signal(monitor: dict, verbose: bool = False) -> dict:
    """Run strategy on latest data and check for signals"""
    try:
        # Determine lookback period based on interval
        if monitor['interval'] == '1d':
            lookback_days = 90  # 90 days for daily
        elif monitor['interval'] == '1h':
            lookback_days = 30  # 30 days for hourly
        else:
            lookback_days = 14  # 14 days for shorter intervals

        start_date = datetime.date.today() - datetime.timedelta(days=lookback_days)
        end_date = datetime.date.today()

        strategy_class = STRATEGIES.get(monitor['strategy'])
        if not strategy_class:
            if verbose:
                print(f"  Unknown strategy: {monitor['strategy']}")
            return None

        runner = Run_strategy(monitor['parameters'], strategy_class)
        results = runner.runstrat(
            ticker=monitor['ticker'],
            start_date=start_date,
            interval=monitor['interval'],
            end_date=end_date
        )

        if not results:
            if verbose:
                print(f"  No results from backtest")
            return None

        trades = results.get('trades', [])

        if not trades:
            if verbose:
                print(f"  No trades in recent period")
            return None

        # Get the most recent trade
        latest_trade = trades[-1]

        # Check if it's today's signal (exit is today)
        trade_date = latest_trade['exit_date']
        if isinstance(trade_date, str):
            trade_date = datetime.datetime.strptime(trade_date, '%Y-%m-%d').date()

        cutoff_date = datetime.date.today() - datetime.timedelta(days=3)

        if trade_date >= cutoff_date:
            signal_type = "SELL"
            price = latest_trade['exit_price']
            pnl = latest_trade['pnl']

            reason = f"{monitor['strategy']} generated exit signal. P&L: ${pnl:+,.2f}"

            if verbose:
                print(f"  Signal detected: {signal_type} at ${price:.2f}")

            return {
                'signal_type': signal_type,
                'price': price,
                'reason': reason
            }

        if verbose:
            print(f"  No recent signals")

        return None

    except Exception as e:
        if verbose:
            print(f"  Error checking strategy: {str(e)}")
            import traceback
            traceback.print_exc()
        return None


def monitor_stocks(verbose: bool = False):
    """Main monitoring function"""

    print("="*70)
    print(f"Stock Monitoring - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    db = TradingDatabase()

    monitored = db.get_monitored_stocks(status='active')

    if not monitored:
        print("\nNo stocks are currently being monitored.")
        print("Add stocks to monitoring via the GUI (Live Trading tab)")
        return

    print(f"\nMonitoring {len(monitored)} stock(s)...\n")

    signals_found = 0

    for monitor in monitored:
        print(f"Checking {monitor['ticker']} ({monitor['strategy']}, {monitor['interval']})...")

        price = get_latest_price(monitor['ticker'])

        if price:
            if verbose:
                print(f"  Current price: ${price:.2f}")

            signal = check_strategy_signal(monitor, verbose=verbose)

            if signal:
                db.log_signal(
                    monitor_id=monitor['id'],
                    ticker=monitor['ticker'],
                    signal_type=signal['signal_type'],
                    price=signal['price'],
                    reason=signal['reason']
                )

                print(f"  Logged {signal['signal_type']} signal at ${signal['price']:.2f}")
                signals_found += 1
            else:
                if verbose:
                    print(f"  No new signals")

        db.update_monitor_last_checked(monitor['id'])

        print()

    print("="*70)
    print(f"Monitoring complete! Found {signals_found} new signal(s)")
    print("="*70)


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(description='Monitor stocks for trading signals')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    try:
        monitor_stocks(verbose=args.verbose)
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
