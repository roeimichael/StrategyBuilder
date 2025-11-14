"""Live trading and monitoring tab for StrategyBuilder Pro"""
import streamlit as st
import pandas as pd

from config import STRATEGIES
from utils.database import TradingDatabase


def run_live_trading_tab(db: TradingDatabase):
    """Live trading/monitoring tab content"""

    st.header(" Live Trading & Monitoring")
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

    st.subheader("📚 Past Backtest Configurations")
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
                    st.success(f"• Added {backtest['ticker']} to monitoring (Monitor ID: {monitor_id})")
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
                if st.button("× Remove", key=f"remove_{stock['id']}"):
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
