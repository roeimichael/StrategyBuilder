"""
StrategyBuilder - Streamlit GUI Application
Interactive backtesting interface with visualizations
"""
import streamlit as st
import sys
import os
import datetime
from typing import List, Dict, Any
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.gui_helpers import (
    get_sp500_tickers,
    get_popular_tickers,
    format_strategy_name
)
from core.run_strategy import Run_strategy
from strategies.bollinger_bands_strategy import Bollinger_three
from strategies.tema_macd_strategy import TEMA_MACD
from strategies.alligator_strategy import Alligator_strategy
from strategies.adx_strategy import adx_strat
from strategies.cmf_atr_macd_strategy import MACD_CMF_ATR_Strategy
from strategies.tema_crossover_strategy import Tema20_tema60

# Page configuration
st.set_page_config(
    page_title="StrategyBuilder",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem;
        border-radius: 10px;
    }
    .stButton>button:hover {
        background-color: #145a8f;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Strategy definitions
STRATEGIES = {
    'Bollinger Bands': {
        'class': Bollinger_three,
        'description': 'Mean reversion using Bollinger Bands',
        'params': {'period': 20, 'devfactor': 2}
    },
    'TEMA + MACD': {
        'class': TEMA_MACD,
        'description': 'Triple EMA crossover with MACD confirmation',
        'params': {}
    },
    'Alligator': {
        'class': Alligator_strategy,
        'description': 'Bill Williams Alligator indicator',
        'params': {}
    },
    'ADX Adaptive': {
        'class': adx_strat,
        'description': 'Adaptive strategy for trending vs ranging markets',
        'params': {}
    },
    'CMF + ATR + MACD': {
        'class': MACD_CMF_ATR_Strategy,
        'description': 'Multi-indicator with volume and volatility',
        'params': {}
    },
    'TEMA Crossover': {
        'class': Tema20_tema60,
        'description': 'TEMA 20/60 crossover with volume filter',
        'params': {}
    },
}

# Initialize session state
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = {}
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None


def main():
    """Main application"""

    # Header
    st.markdown('<h1 class="main-header">📈 StrategyBuilder 📉</h1>', unsafe_allow_html=True)
    st.markdown("### Professional Backtesting Platform")
    st.markdown("---")

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Ticker Selection
        st.subheader("📊 Stock Selection")
        ticker_source = st.radio(
            "Select ticker source:",
            ["Popular Stocks", "S&P 500", "Custom Input"],
            help="Choose where to select stocks from"
        )

        selected_tickers = []

        if ticker_source == "Popular Stocks":
            popular = get_popular_tickers()
            category = st.selectbox("Category:", list(popular.keys()))
            selected_tickers = st.multiselect(
                "Select stocks:",
                popular[category],
                default=[popular[category][0]]
            )

        elif ticker_source == "S&P 500":
            with st.spinner("Loading S&P 500 tickers..."):
                sp500_tickers = get_sp500_tickers()
            selected_tickers = st.multiselect(
                "Select stocks:",
                sp500_tickers,
                default=['AAPL']
            )

        else:  # Custom Input
            custom_input = st.text_input(
                "Enter ticker(s) (comma-separated):",
                value="AAPL",
                help="Example: AAPL,MSFT,TSLA"
            )
            selected_tickers = [t.strip().upper() for t in custom_input.split(',') if t.strip()]

        st.markdown("---")

        # Strategy Selection
        st.subheader("🎯 Strategy")
        strategy_name = st.selectbox(
            "Select strategy:",
            list(STRATEGIES.keys()),
            help="Choose a trading strategy to backtest"
        )

        strategy_info = STRATEGIES[strategy_name]
        st.info(f"ℹ️ {strategy_info['description']}")

        # Strategy Parameters (if any)
        strategy_params = {}
        if strategy_info['params']:
            with st.expander("📝 Strategy Parameters"):
                for param_name, default_value in strategy_info['params'].items():
                    if isinstance(default_value, int):
                        strategy_params[param_name] = st.number_input(
                            param_name.capitalize(),
                            value=default_value,
                            min_value=1,
                            help=f"Adjust {param_name} parameter"
                        )
                    elif isinstance(default_value, float):
                        strategy_params[param_name] = st.number_input(
                            param_name.capitalize(),
                            value=default_value,
                            min_value=0.1,
                            step=0.1,
                            help=f"Adjust {param_name} parameter"
                        )

        st.markdown("---")

        # Date Range
        st.subheader("📅 Date Range")
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Start date",
                value=datetime.date.today() - datetime.timedelta(days=365),
                max_value=datetime.date.today()
            )

        with col2:
            end_date = st.date_input(
                "End date",
                value=datetime.date.today(),
                max_value=datetime.date.today()
            )

        st.markdown("---")

        # Time Interval
        st.subheader("⏱️ Time Interval")
        interval = st.selectbox(
            "Select interval:",
            ["1d", "1h", "30m", "15m", "5m", "1wk"],
            index=0,
            help="Data granularity for backtesting"
        )

        st.markdown("---")

        # Backtesting Parameters
        st.subheader("💰 Backtest Settings")

        starting_cash = st.number_input(
            "Starting capital ($):",
            value=10000,
            min_value=1000,
            step=1000,
            help="Initial portfolio value"
        )

        position_size = st.slider(
            "Position size (%):",
            min_value=10,
            max_value=100,
            value=100,
            step=10,
            help="Percentage of capital to use per trade"
        ) / 100

        # Advanced parameters
        with st.expander("⚙️ Advanced Parameters"):
            macd_fast = st.number_input("MACD Fast Period", value=12, min_value=5, max_value=50)
            macd_slow = st.number_input("MACD Slow Period", value=26, min_value=10, max_value=100)
            macd_signal = st.number_input("MACD Signal Period", value=9, min_value=3, max_value=30)
            atr_period = st.number_input("ATR Period", value=14, min_value=5, max_value=50)
            atr_distance = st.number_input("ATR Distance", value=2.0, min_value=0.5, max_value=5.0, step=0.1)

        st.markdown("---")

        # Run Button
        run_button = st.button("🚀 Run Backtest", type="primary")

    # Main content area
    if not selected_tickers:
        st.warning("⚠️ Please select at least one stock ticker to begin.")
        st.info("""
        ### How to use StrategyBuilder:
        1. Select one or more stock tickers from the sidebar
        2. Choose a trading strategy
        3. Set your date range and time interval
        4. Configure backtest settings (capital, position size)
        5. Click 'Run Backtest' to see results
        """)
        return

    # Show selected configuration
    with st.expander("📋 Current Configuration", expanded=False):
        config_col1, config_col2, config_col3 = st.columns(3)
        with config_col1:
            st.write("**Tickers:**", ", ".join(selected_tickers))
            st.write("**Strategy:**", strategy_name)
        with config_col2:
            st.write("**Date Range:**", f"{start_date} to {end_date}")
            st.write("**Interval:**", interval)
        with config_col3:
            st.write("**Capital:**", f"${starting_cash:,.2f}")
            st.write("**Position Size:**", f"{position_size*100:.0f}%")

    # Run backtest
    if run_button:
        st.session_state.backtest_results = {}

        # Build parameters
        parameters = {
            'cash': starting_cash,
            'order_pct': position_size,
            'macd1': macd_fast,
            'macd2': macd_slow,
            'macdsig': macd_signal,
            'atrperiod': atr_period,
            'atrdist': atr_distance,
        }

        # Add strategy-specific parameters
        parameters.update(strategy_params)

        strategy_class = strategy_info['class']

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, ticker in enumerate(selected_tickers):
            status_text.text(f"Running backtest for {ticker}... ({idx + 1}/{len(selected_tickers)})")
            progress_bar.progress((idx + 1) / len(selected_tickers))

            try:
                run_cerebro = Run_strategy(parameters, strategy_class)
                results = run_cerebro.runstrat(ticker, start_date, interval, end_date)

                if results:
                    st.session_state.backtest_results[ticker] = results
                else:
                    st.error(f"❌ Failed to run backtest for {ticker}")

            except Exception as e:
                st.error(f"❌ Error backtesting {ticker}: {str(e)}")

        progress_bar.empty()
        status_text.empty()

        if st.session_state.backtest_results:
            st.success(f"✅ Backtesting completed for {len(st.session_state.backtest_results)} stock(s)!")
            st.session_state.selected_stock = list(st.session_state.backtest_results.keys())[0]

    # Display results
    if st.session_state.backtest_results:
        st.markdown("---")
        st.header("📊 Backtest Results")

        # Stock selector for multiple stocks
        if len(st.session_state.backtest_results) > 1:
            stock_tabs = st.tabs([f"📈 {ticker}" for ticker in st.session_state.backtest_results.keys()])

            for idx, ticker in enumerate(st.session_state.backtest_results.keys()):
                with stock_tabs[idx]:
                    display_results(ticker, st.session_state.backtest_results[ticker])
        else:
            ticker = list(st.session_state.backtest_results.keys())[0]
            display_results(ticker, st.session_state.backtest_results[ticker])


def display_results(ticker: str, results: Dict[str, Any]):
    """Display backtest results for a single stock"""

    st.subheader(f"Results for {ticker}")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Starting Value",
            f"${results['start_value']:,.2f}"
        )

    with col2:
        st.metric(
            "Final Value",
            f"${results['end_value']:,.2f}",
            delta=f"${results['pnl']:,.2f}"
        )

    with col3:
        st.metric(
            "Total Return",
            f"{results['return_pct']:+.2f}%",
            delta=f"{results['return_pct']:+.2f}%"
        )

    with col4:
        if results.get('sharpe_ratio'):
            st.metric(
                "Sharpe Ratio",
                f"{results['sharpe_ratio']:.3f}"
            )
        else:
            st.metric("Sharpe Ratio", "N/A")

    # Additional metrics
    st.markdown("---")
    metrics_col1, metrics_col2 = st.columns(2)

    with metrics_col1:
        if results.get('max_drawdown'):
            st.metric("Maximum Drawdown", f"{results['max_drawdown']:.2f}%")

    with metrics_col2:
        if results.get('total_trades'):
            st.metric("Total Trades", results['total_trades'])

    # Placeholder for charts (will implement in Phase 4)
    st.markdown("---")
    st.info("📊 Chart visualization will be added in the next phase")


if __name__ == "__main__":
    main()
