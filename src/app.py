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
from utils.visualization import (
    create_backtest_chart,
    create_trades_table,
    create_performance_metrics_chart,
    create_trade_distribution_chart
)
from utils.database import TradingDatabase
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

# Initialize database
@st.cache_resource
def init_database():
    return TradingDatabase()

# Initialize session state
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = {}
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None
if 'current_strategy' not in st.session_state:
    st.session_state.current_strategy = None
if 'current_parameters' not in st.session_state:
    st.session_state.current_parameters = None


def main():
    """Main application"""

    # Initialize database
    db = init_database()

    # Header
    st.markdown('<h1 class="main-header">📈 StrategyBuilder 📉</h1>', unsafe_allow_html=True)
    st.markdown("### Professional Backtesting & Live Trading Platform")
    st.markdown("---")

    # Main tabs
    tab1, tab2 = st.tabs(["📊 Backtest", "🔴 Live Trading"])

    with tab1:
        run_backtest_tab(db)

    with tab2:
        run_live_trading_tab(db)


def run_backtest_tab(db: TradingDatabase):
    """Backtest tab content"""

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

        # Store in session for later use (monitoring)
        st.session_state.current_strategy = strategy_name
        st.session_state.current_parameters = parameters.copy()

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
                    display_results(ticker, st.session_state.backtest_results[ticker], db)
        else:
            ticker = list(st.session_state.backtest_results.keys())[0]
            display_results(ticker, st.session_state.backtest_results[ticker], db)


def display_results(ticker: str, results: Dict[str, Any], db: TradingDatabase):
    """Display backtest results for a single stock"""

    st.subheader(f"Results for {ticker}")

    # Action buttons at the top
    col_save, col_monitor = st.columns([1, 1])

    with col_save:
        if st.button(f"💾 Save to Database", key=f"save_{ticker}"):
            try:
                backtest_id = db.save_backtest(
                    results=results,
                    strategy=st.session_state.current_strategy,
                    parameters=st.session_state.current_parameters,
                    notes=f"Backtest run on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                st.success(f"✅ Saved to database (ID: {backtest_id})")
            except Exception as e:
                st.error(f"Failed to save: {str(e)}")

    with col_monitor:
        if st.button(f"📡 Add to Live Monitoring", key=f"monitor_{ticker}"):
            try:
                monitor_id = db.add_to_monitoring(
                    ticker=ticker,
                    strategy=st.session_state.current_strategy,
                    interval=results['interval'],
                    parameters=st.session_state.current_parameters
                )
                st.success(f"✅ Added to live monitoring (Monitor ID: {monitor_id})")
            except Exception as e:
                st.error(f"Failed to add to monitoring: {str(e)}")

    st.markdown("---")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Starting Value",
            f"${results['start_value']:,.2f}"
        )

    with col2:
        pnl_color = "normal" if results['pnl'] >= 0 else "inverse"
        st.metric(
            "Final Value",
            f"${results['end_value']:,.2f}",
            delta=f"${results['pnl']:,.2f}",
            delta_color=pnl_color
        )

    with col3:
        return_color = "normal" if results['return_pct'] >= 0 else "inverse"
        st.metric(
            "Total Return",
            f"{results['return_pct']:+.2f}%",
            delta=f"{results['return_pct']:+.2f}%",
            delta_color=return_color
        )

    with col4:
        if results.get('sharpe_ratio'):
            st.metric(
                "Sharpe Ratio",
                f"{results['sharpe_ratio']:.3f}"
            )
        else:
            st.metric("Sharpe Ratio", "N/A")

    # Second row of metrics
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        if results.get('max_drawdown'):
            st.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
        else:
            st.metric("Max Drawdown", "N/A")

    with col6:
        st.metric("Total Trades", results.get('total_trades', 0))

    with col7:
        trades = results.get('trades', [])
        if trades:
            winning_trades = len([t for t in trades if t['pnl'] > 0])
            win_rate = (winning_trades / len(trades)) * 100
            st.metric("Win Rate", f"{win_rate:.1f}%")
        else:
            st.metric("Win Rate", "N/A")

    with col8:
        if trades:
            avg_pnl = sum(t['pnl'] for t in trades) / len(trades)
            st.metric("Avg P&L per Trade", f"${avg_pnl:+,.2f}")
        else:
            st.metric("Avg P&L per Trade", "N/A")

    st.markdown("---")

    # Interactive price chart with entry/exit signals
    st.subheader("📊 Price Chart with Trade Signals")

    with st.spinner("Loading chart..."):
        fig = create_backtest_chart(
            ticker=results['ticker'],
            start_date=results['start_date'],
            end_date=results['end_date'],
            interval=results['interval'],
            trades=results.get('trades', [])
        )

    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Unable to load chart data")

    st.markdown("---")

    # Performance charts
    trades = results.get('trades', [])
    if trades:
        st.subheader("📈 Performance Analysis")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            cumulative_fig = create_performance_metrics_chart(trades)
            if cumulative_fig:
                st.plotly_chart(cumulative_fig, use_container_width=True)

        with chart_col2:
            distribution_fig = create_trade_distribution_chart(trades)
            if distribution_fig:
                st.plotly_chart(distribution_fig, use_container_width=True)

        st.markdown("---")

        # Trade details table
        st.subheader("📋 Trade Details")

        trades_df = create_trades_table(trades)

        if not trades_df.empty:
            # Color code P&L column
            def highlight_pnl(val):
                if isinstance(val, str) and val.startswith('$'):
                    # Extract numeric value
                    try:
                        numeric_val = float(val.replace('$', '').replace(',', '').replace('+', ''))
                        color = 'background-color: #d4edda' if numeric_val > 0 else 'background-color: #f8d7da'
                        return color
                    except:
                        return ''
                return ''

            # Apply styling (pandas 2.0+ uses 'map' instead of 'applymap')
            try:
                styled_df = trades_df.style.map(highlight_pnl, subset=['P&L'])
            except AttributeError:
                # Fallback for pandas < 2.0
                styled_df = trades_df.style.applymap(highlight_pnl, subset=['P&L'])

            st.dataframe(styled_df, use_container_width=True, height=400)

            # Download button for trade data
            csv = trades_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Trade Data (CSV)",
                data=csv,
                file_name=f"{ticker}_trades.csv",
                mime="text/csv"
            )
        else:
            st.info("No trades executed during this backtest")
    else:
        st.info("No trades executed during this backtest")


def run_live_trading_tab(db: TradingDatabase):
    """Live trading/monitoring tab content"""

    st.header("🔴 Live Trading & Monitoring")
    st.markdown("Monitor stocks with your tested strategies in real-time")
    st.markdown("---")

    # Create subtabs for different views
    subtab1, subtab2, subtab3 = st.tabs(["📊 Backtest History", "📡 Active Monitoring", "📈 Signals & Performance"])

    with subtab1:
        show_backtest_history(db)

    with subtab2:
        show_active_monitoring(db)

    with subtab3:
        show_signals_and_performance(db)


def show_backtest_history(db: TradingDatabase):
    """Display backtest history with option to add to monitoring"""

    st.subheader("📊 Past Backtest Configurations")
    st.markdown("Review your backtest history and add successful strategies to live monitoring")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_ticker = st.text_input("Filter by ticker:", placeholder="e.g., AAPL")

    with col2:
        filter_strategy = st.selectbox(
            "Filter by strategy:",
            ["All"] + list(STRATEGIES.keys())
        )

    with col3:
        limit = st.number_input("Number of results:", min_value=10, max_value=100, value=50)

    # Get backtests from database
    ticker_filter = filter_ticker.upper() if filter_ticker else None
    strategy_filter = None if filter_strategy == "All" else filter_strategy

    backtests = db.get_backtests(
        limit=limit,
        ticker=ticker_filter,
        strategy=strategy_filter
    )

    if not backtests:
        st.info("No backtests found. Run some backtests first in the Backtest tab!")
        return

    st.markdown(f"**Found {len(backtests)} backtest(s)**")
    st.markdown("---")

    # Display each backtest as a card
    for backtest in backtests:
        with st.expander(
            f"🔹 {backtest['ticker']} - {backtest['strategy']} "
            f"({backtest['start_date']} to {backtest['end_date']}) - "
            f"Return: {backtest['return_pct']:+.2f}%",
            expanded=False
        ):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Return", f"{backtest['return_pct']:+.2f}%")
                st.metric("Start Value", f"${backtest['start_value']:,.2f}")

            with col2:
                st.metric("End Value", f"${backtest['end_value']:,.2f}")
                st.metric("Total Trades", backtest['total_trades'])

            with col3:
                sharpe = backtest['sharpe_ratio'] if backtest['sharpe_ratio'] else "N/A"
                st.metric("Sharpe Ratio", f"{sharpe}" if isinstance(sharpe, str) else f"{sharpe:.3f}")
                st.metric("Win Rate", f"{backtest['win_rate']:.1f}%" if backtest['win_rate'] else "N/A")

            with col4:
                st.metric("Avg P&L/Trade", f"${backtest['avg_pnl']:+,.2f}" if backtest['avg_pnl'] else "N/A")
                st.metric("Max Drawdown", f"{backtest['max_drawdown']:.2f}%" if backtest['max_drawdown'] else "N/A")

            st.markdown("**Configuration:**")
            st.json(backtest['parameters'])

            if backtest['notes']:
                st.markdown(f"**Notes:** {backtest['notes']}")

            # Action button
            if st.button(f"📡 Add to Monitoring", key=f"add_monitor_{backtest['id']}"):
                try:
                    monitor_id = db.add_to_monitoring(
                        ticker=backtest['ticker'],
                        strategy=backtest['strategy'],
                        interval=backtest['interval'],
                        parameters=backtest['parameters'],
                        backtest_id=backtest['id']
                    )
                    st.success(f"✅ Added {backtest['ticker']} to monitoring (Monitor ID: {monitor_id})")
                except Exception as e:
                    st.error(f"Failed to add to monitoring: {str(e)}")


def show_active_monitoring(db: TradingDatabase):
    """Display and manage actively monitored stocks"""

    st.subheader("📡 Active Monitoring List")
    st.markdown("These stocks are being monitored for trading signals")

    # Get monitored stocks
    monitored = db.get_monitored_stocks()

    if not monitored:
        st.info("No stocks are currently being monitored. Add some from the Backtest History!")
        st.markdown("**How to add:**")
        st.markdown("1. Go to 'Backtest History' subtab")
        st.markdown("2. Find a successful backtest")
        st.markdown("3. Click 'Add to Monitoring'")
        return

    st.markdown(f"**Monitoring {len(monitored)} stock(s)**")
    st.markdown("---")

    # Display monitored stocks
    for stock in monitored:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                st.markdown(f"### {stock['ticker']}")
                st.markdown(f"**Strategy:** {stock['strategy']}")

            with col2:
                st.markdown(f"**Interval:** {stock['interval']}")
                st.markdown(f"**Added:** {stock['added_at'][:10]}")

            with col3:
                last_checked = stock['last_checked'] if stock['last_checked'] else "Never"
                if last_checked != "Never":
                    last_checked = last_checked[:19]  # Show datetime without microseconds
                st.markdown(f"**Last Checked:** {last_checked}")
                st.markdown(f"**Status:** {stock['status'].upper()}")

            with col4:
                if st.button("🗑️ Remove", key=f"remove_{stock['id']}"):
                    db.remove_from_monitoring(stock['id'])
                    st.success(f"Removed {stock['ticker']} from monitoring")
                    st.rerun()

            # Show parameters in expander
            with st.expander("View Configuration"):
                st.json(stock['parameters'])

            st.markdown("---")

    # Button to run monitoring script
    st.markdown("### 🔄 Manual Check")
    if st.button("Run Monitoring Check Now", type="primary"):
        st.info("Monitoring check will be implemented in the monitoring script. Use `python monitor_stocks.py` to run checks.")


def show_signals_and_performance(db: TradingDatabase):
    """Display trading signals and performance metrics"""

    st.subheader("📈 Trading Signals & Performance")
    st.markdown("Recent trading signals from monitored stocks")

    # Time filter
    days_back = st.slider("Show signals from last N days:", min_value=7, max_value=90, value=30)

    # Get signals
    signals = db.get_signals(days=days_back)

    if not signals:
        st.info(f"No trading signals in the last {days_back} days. Run the monitoring script to generate signals.")
        st.markdown("**To generate signals:**")
        st.code("python src/monitor_stocks.py", language="bash")
        return

    # Create DataFrame for display
    signals_df = pd.DataFrame(signals)

    st.markdown(f"**Found {len(signals)} signal(s)**")

    # Display signals
    st.dataframe(
        signals_df[['ticker', 'signal_type', 'signal_date', 'price', 'reason', 'created_at']],
        use_container_width=True,
        height=400
    )

    # Summary statistics
    st.markdown("### 📊 Signal Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        buy_signals = len(signals_df[signals_df['signal_type'] == 'BUY'])
        st.metric("Buy Signals", buy_signals)

    with col2:
        sell_signals = len(signals_df[signals_df['signal_type'] == 'SELL'])
        st.metric("Sell Signals", sell_signals)

    with col3:
        unique_tickers = signals_df['ticker'].nunique()
        st.metric("Active Stocks", unique_tickers)


if __name__ == "__main__":
    main()
