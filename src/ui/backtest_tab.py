"""Backtest tab module for StrategyBuilder Pro"""
import streamlit as st
import datetime
from typing import Dict, Any

from config import STRATEGIES
from utils.gui_helpers import get_sp500_tickers, get_popular_tickers
from utils.visualization import (
    create_backtest_chart,
    create_trades_table,
    create_performance_metrics_chart,
    create_trade_distribution_chart
)
from utils.database import TradingDatabase
from core.run_strategy import Run_strategy


def run_backtest_tab(db: TradingDatabase):
    """Backtest tab content"""
    with st.sidebar:
        st.header("Configuration")

        st.subheader("Stock Selection")
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

        else:
            custom_input = st.text_input(
                "Enter ticker(s) (comma-separated):",
                value="AAPL",
                help="Example: AAPL,MSFT,TSLA"
            )
            selected_tickers = [t.strip().upper() for t in custom_input.split(',') if t.strip()]

        st.markdown("---")

        st.subheader("Strategy")
        strategy_name = st.selectbox(
            "Select strategy:",
            list(STRATEGIES.keys()),
            help="Choose a trading strategy to backtest"
        )

        strategy_info = STRATEGIES[strategy_name]
        st.info(f"{strategy_info['description']}")

        strategy_params = {}
        if strategy_info['params']:
            with st.expander("Strategy Parameters"):
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

        st.subheader("Date Range")
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

        st.subheader("Time Interval")
        interval = st.selectbox(
            "Select interval:",
            ["1d", "1h", "30m", "15m", "5m", "1wk"],
            index=0,
            help="Data granularity for backtesting"
        )

        st.markdown("---")

        st.subheader("Backtest Settings")

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

        with st.expander("Advanced Parameters"):
            macd_fast = st.number_input("MACD Fast Period", value=12, min_value=5, max_value=50)
            macd_slow = st.number_input("MACD Slow Period", value=26, min_value=10, max_value=100)
            macd_signal = st.number_input("MACD Signal Period", value=9, min_value=3, max_value=30)
            atr_period = st.number_input("ATR Period", value=14, min_value=5, max_value=50)
            atr_distance = st.number_input("ATR Distance", value=2.0, min_value=0.5, max_value=5.0, step=0.1)

        st.markdown("---")

        run_button = st.button("⚡ Run Backtest", type="primary")

    if not selected_tickers:
        st.warning("Please select at least one stock ticker to begin.")
        st.info("""
        ### How to use StrategyBuilder:
        1. Select one or more stock tickers from the sidebar
        2. Choose a trading strategy
        3. Set your date range and time interval
        4. Configure backtest settings (capital, position size)
        5. Click 'Run Backtest' to see results
        """)
        return

    with st.expander("Current Configuration", expanded=False):
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

    if run_button:
        st.session_state.backtest_results = {}

        parameters = {
            'cash': starting_cash,
            'order_pct': position_size,
            'macd1': macd_fast,
            'macd2': macd_slow,
            'macdsig': macd_signal,
            'atrperiod': atr_period,
            'atrdist': atr_distance,
        }

        parameters.update(strategy_params)

        st.session_state.current_strategy = strategy_name
        st.session_state.current_parameters = parameters.copy()

        strategy_class = strategy_info['class']

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
                    st.error(f"Failed to run backtest for {ticker}")

            except Exception as e:
                st.error(f"Error backtesting {ticker}: {str(e)}")

        progress_bar.empty()
        status_text.empty()

        if st.session_state.backtest_results:
            st.success(f"Backtesting completed for {len(st.session_state.backtest_results)} stock(s)")
            st.session_state.selected_stock = list(st.session_state.backtest_results.keys())[0]

    if st.session_state.backtest_results:
        st.markdown("---")
        st.header("Backtest Results")

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
                st.success(f"Saved to database (ID: {backtest_id})")
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
                st.success(f"Added to live monitoring (Monitor ID: {monitor_id})")
            except Exception as e:
                st.error(f"Failed to add to monitoring: {str(e)}")

    st.markdown("---")

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

    st.subheader("Price Chart with Trade Signals")

    with st.spinner("Loading chart..."):
        fig = create_backtest_chart(
            ticker=results['ticker'],
            start_date=results['start_date'],
            end_date=results['end_date'],
            interval=results['interval'],
            trades=results.get('trades', []),
            strategy_name=st.session_state.current_strategy,
            strategy_params=st.session_state.current_parameters
        )

    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Unable to load chart data")

    st.markdown("---")

    trades = results.get('trades', [])
    if trades:
        st.subheader("Performance Analysis")

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

        st.subheader("Trade Details")

        trades_df = create_trades_table(trades)

        if not trades_df.empty:
            def highlight_pnl(val):
                if isinstance(val, str) and val.startswith('$'):
                    try:
                        numeric_val = float(val.replace('$', '').replace(',', '').replace('+', ''))
                        color = 'background-color: #d4edda' if numeric_val > 0 else 'background-color: #f8d7da'
                        return color
                    except:
                        return ''
                return ''

            try:
                styled_df = trades_df.style.map(highlight_pnl, subset=['P&L'])
            except AttributeError:
                styled_df = trades_df.style.applymap(highlight_pnl, subset=['P&L'])

            st.dataframe(styled_df, use_container_width=True, height=400)

            csv = trades_df.to_csv(index=False)
            st.download_button(
                label="💾 Download Trade Data (CSV)",
                data=csv,
                file_name=f"{ticker}_trades.csv",
                mime="text/csv"
            )
        else:
            st.info("No trades executed during this backtest")
    else:
        st.info("No trades executed during this backtest")
