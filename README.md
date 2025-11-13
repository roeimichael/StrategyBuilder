# StrategyBuilder

A Python-based backtesting framework for algorithmic trading strategies using Backtrader.

## Features

- **Multiple Trading Strategies**: 7+ pre-built strategies including TEMA+MACD, Bollinger Bands, ADX, Alligator, and more
- **Flexible Configuration**: YAML-based configuration for easy parameter tuning
- **Performance Analytics**: Built-in Sharpe ratio, drawdown, and ROI calculations
- **Notifications**: Optional Telegram and Email alerts
- **Custom Indicators**: Includes custom indicators like CMF (Chaikin Money Flow)

## Project Structure

```
StrategyBuilder/
├── src/
│   ├── core/              # Core backtesting engine
│   ├── strategies/        # Trading strategy implementations
│   ├── indicators/        # Custom technical indicators
│   ├── utils/             # Utilities (scanner, notifications, etc.)
│   └── main.py           # Main entry point
├── data/                  # Market data files
├── config.yaml           # Configuration file
├── .env.example          # Environment variables template
└── requirements.txt      # Python dependencies
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd StrategyBuilder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional, for notifications)
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Configure parameters**
   - Edit `config.yaml` to adjust backtesting parameters, indicator settings, and risk management

## Quick Start

### Running a Backtest

```bash
python src/main.py
```

By default, this runs a Bollinger Bands strategy on AAPL with 1 year of historical data.

### Customizing the Backtest

Edit `src/main.py` to change:

```python
# Change ticker
ticker = "TSLA"

# Change strategy
from strategies.tema_macd_strategy import TEMA_MACD
strategy = TEMA_MACD

# Change time interval
interval = "1h"  # Options: 1m, 5m, 15m, 30m, 1h, 90m, 1d, 5d, 1wk, 1mo
```

## Available Strategies

| Strategy | File | Description |
|----------|------|-------------|
| **TEMA + MACD** | `tema_macd_strategy.py` | Combines Triple EMA with MACD for trend confirmation |
| **CMF + ATR + MACD** | `cmf_atr_macd_strategy.py` | Multi-indicator with volume, volatility, and momentum |
| **ADX** | `adx_strategy.py` | Adaptive strategy for trending vs range-bound markets |
| **Alligator** | `alligator_strategy.py` | Bill Williams' Alligator indicator |
| **Bollinger Bands** | `bollinger_bands_strategy.py` | Mean reversion using Bollinger Bands |
| **TEMA Crossover** | `tema_crossover_strategy.py` | TEMA 20/60 crossover with volume filter |
| **Pair Trading** | `pair_trading_strategy.py` | Statistical arbitrage (incomplete) |

## Configuration

### config.yaml

Key configuration sections:

```yaml
backtesting:
  cash: 10000                    # Starting capital
  order_percentage: 1.0          # Position size (1.0 = 100%)

indicators:
  macd:
    fast_period: 12
    slow_period: 26
    signal_period: 9

  atr:
    period: 14
    distance: 2.0               # Stop loss/take profit in ATR multiples

data:
  default_interval: "1d"
  default_lookback_years: 1
```

## Notifications (Optional)

### Telegram Setup

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   TELEGRAM_CHAT_ID=your_chat_id
   ```

### Email Setup

1. Generate an app-specific password (for Gmail)
2. Add to `.env`:
   ```
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   ```

## Development

### Creating a New Strategy

1. Create a new file in `src/strategies/`
2. Inherit from `Strategy_skeleton`:

```python
from core.strategy_skeleton import Strategy_skeleton
import backtrader as bt

class MyStrategy(Strategy_skeleton):
    def __init__(self, args):
        super(MyStrategy, self).__init__(args)
        # Initialize indicators here

    def next(self):
        # Strategy logic here
        if not self.position:
            if <buy_condition>:
                self.buy()
        else:
            if <sell_condition>:
                self.close()
```

3. Import and use in `main.py`

## Data Sources

- **Default**: Yahoo Finance via `yfinance` library
- Data is downloaded automatically for the specified ticker and timeframe
- Historical data cached by yfinance

## Requirements

- Python 3.7+
- backtrader
- yfinance
- pandas
- numpy
- PyYAML

See `requirements.txt` for full list.

## Performance Metrics

Each backtest displays:
- Starting/ending portfolio value
- Percentage gain/loss
- Sharpe ratio
- Maximum drawdown
- Trade-by-trade breakdown

## Troubleshooting

**Import errors after reorganization:**
- Make sure you're running from the project root
- Ensure `src/` directory has `__init__.py`

**Data download failures:**
- Check internet connection
- Verify ticker symbol is valid
- Try a different time interval

**Notification not working:**
- Verify `.env` file exists and has correct credentials
- Enable notifications in `config.yaml`
- Check API tokens are valid

## License

MIT License (or specify your license)

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Disclaimer

This software is for educational and research purposes only. Do not use for live trading without thorough testing and understanding of the risks involved. Past performance does not guarantee future results.
