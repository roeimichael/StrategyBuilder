"""Grid search parameter optimization tab for StrategyBuilder Pro"""
import streamlit as st
import datetime
import pandas as pd

from config import STRATEGIES
from utils.visualization import create_backtest_chart, create_trades_table
from utils.database import TradingDatabase
from utils.grid_search import GridSearchOptimizer, create_parameter_ranges


def run_grid_search_tab(db: TradingDatabase):
    """Grid search parameter optimization tab"""

    st.header(" Grid Search - Parameter Optimization")
    st.markdown("Systematically test parameter combinations to find optimal strategy settings")
    st.markdown("---")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙ Grid Search Configuration")

        # Stock selection
        st.subheader("Stock")
        ticker = st.text_input("Ticker:", value="AAPL", help="Single stock for optimization")

        st.markdown("---")

        # Strategy selection
        st.subheader("Strategy")
        strategy_name = st.selectbox(
            "Select strategy to optimize:",
            list(STRATEGIES.keys()),
            help="Choose strategy to find best parameters"
        )

        strategy_info = STRATEGIES[strategy_name]

        st.markdown("---")

        # Date range
        st.subheader("Test Period")
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Start",
                value=datetime.date.today() - datetime.timedelta(days=365),
                max_value=datetime.date.today()
            )

        with col2:
            end_date = st.date_input(
                "End",
                value=datetime.date.today(),
                max_value=datetime.date.today()
            )

        interval = st.selectbox("Interval:", ["1d", "1h", "30m"], index=0)

        st.markdown("---")

        # Capital settings
        st.subheader("Capital")
        starting_cash = st.number_input("Starting capital ($):", value=10000, min_value=1000, step=1000)

        st.markdown("---")

        # Sort metric
        st.subheader("Optimization Metric")
        sort_metric = st.selectbox(
            "Optimize for:",
            ["return_pct", "sharpe_ratio", "win_rate"],
            format_func=lambda x: {
                'return_pct': 'Total Return %',
                'sharpe_ratio': 'Sharpe Ratio',
                'win_rate': 'Win Rate %'
            }[x],
            help="Metric to optimize"
        )

    # Main content
    st.subheader("⚙ Parameter Ranges")
    st.markdown("Define the range of values to test for each parameter")

    # Get default parameter ranges for this strategy
    default_ranges = create_parameter_ranges(strategy_name)

    # Create parameter range inputs
    param_ranges = {}

    if strategy_name == 'Bollinger Bands':
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Period** (MA window)")
            period_values = st.multiselect(
                "Select values:",
                [5, 10, 15, 20, 25, 30, 35, 40],
                default=[10, 15, 20, 25, 30],
                key="period_range"
            )
            if period_values:
                param_ranges['period'] = period_values

        with col2:
            st.markdown("**Deviation Factor** (Band width)")
            devfactor_values = st.multiselect(
                "Select values:",
                [1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
                default=[1.5, 2.0, 2.5, 3.0],
                key="devfactor_range"
            )
            if devfactor_values:
                param_ranges['devfactor'] = devfactor_values

    elif strategy_name == 'TEMA + MACD':
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**MACD Fast**")
            macd1_values = st.multiselect(
                "Values:",
                [8, 10, 12, 14, 16],
                default=[8, 12, 16],
                key="macd1_range"
            )
            if macd1_values:
                param_ranges['macd1'] = macd1_values

        with col2:
            st.markdown("**MACD Slow**")
            macd2_values = st.multiselect(
                "Values:",
                [20, 24, 26, 28, 32],
                default=[20, 26, 32],
                key="macd2_range"
            )
            if macd2_values:
                param_ranges['macd2'] = macd2_values

        with col3:
            st.markdown("**MACD Signal**")
            macdsig_values = st.multiselect(
                "Values:",
                [7, 9, 11, 13],
                default=[7, 9, 11],
                key="macdsig_range"
            )
            if macdsig_values:
                param_ranges['macdsig'] = macdsig_values

    elif strategy_name == 'ADX Adaptive':
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**ATR Period**")
            atr_values = st.multiselect(
                "Values:",
                [10, 12, 14, 16, 18, 20],
                default=[10, 14, 18],
                key="atr_range"
            )
            if atr_values:
                param_ranges['atrperiod'] = atr_values

        with col2:
            st.markdown("**ATR Distance**")
            atrdist_values = st.multiselect(
                "Values:",
                [1.0, 1.5, 2.0, 2.5, 3.0],
                default=[1.5, 2.0, 2.5],
                key="atrdist_range"
            )
            if atrdist_values:
                param_ranges['atrdist'] = atrdist_values

    else:
        st.info(f"Parameter ranges for {strategy_name} not yet configured. Using default backtest.")

    # Show total combinations
    if param_ranges:
        import itertools
        total_combinations = 1
        for values in param_ranges.values():
            total_combinations *= len(values)

        st.info(f"📊 Total combinations to test: **{total_combinations}**")

        if total_combinations > 100:
            st.warning("! Large number of combinations may take a while. Consider reducing parameter ranges.")

    st.markdown("---")

    # Run grid search button
    run_search = st.button("⚙ Run Grid Search", type="primary", disabled=not param_ranges)

    if run_search and param_ranges:
        # Base parameters
        base_params = {
            'cash': starting_cash,
            'order_pct': 1.0,
            'macd1': 12,
            'macd2': 26,
            'macdsig': 9,
            'atrperiod': 14,
            'atrdist': 2.0,
        }

        # Initialize optimizer
        optimizer = GridSearchOptimizer(strategy_info['class'], base_params)

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        current_params_text = st.empty()

        def progress_callback(current, total, params):
            progress_bar.progress(current / total)
            status_text.text(f"Testing combination {current}/{total}...")
            # Show current parameters being tested
            param_str = ", ".join([f"{k}={v}" for k, v in params.items() if k in param_ranges])
            current_params_text.text(f"Current: {param_str}")

        # Run grid search
        with st.spinner("Running grid search..."):
            results = optimizer.run_grid_search(
                ticker=ticker.upper(),
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                param_ranges=param_ranges,
                progress_callback=progress_callback
            )

        progress_bar.empty()
        status_text.empty()
        current_params_text.empty()

        if results:
            st.session_state.grid_search_results = results
            st.session_state.selected_grid_result = 0
            st.success(f"• Grid search complete! Found {len(results)} valid combinations")
        else:
            st.error("× No valid results from grid search")

    # Display results
    if st.session_state.grid_search_results:
        st.markdown("---")
        st.header(" Grid Search Results")

        results = st.session_state.grid_search_results

        # Get top 5
        top_results = results[:5]

        # Selection sidebar
        col1, col2 = st.columns([1, 3])

        with col1:
            st.subheader("🏆 Top 5 Results")

            for idx, result in enumerate(top_results):
                # Create button for each result
                rank = idx + 1
                return_pct = result['return_pct']
                sharpe = result.get('sharpe_ratio', 0) if result.get('sharpe_ratio') else 0

                button_label = f"#{rank}: {return_pct:+.2f}% | Sharpe: {sharpe:.2f}"

                if st.button(button_label, key=f"select_{idx}", use_container_width=True):
                    st.session_state.selected_grid_result = idx

            # Highlight selected
            selected_idx = st.session_state.selected_grid_result
            st.markdown(f"**Currently viewing: #{selected_idx + 1}**")

        with col2:
            # Display selected result
            selected_result = top_results[st.session_state.selected_grid_result]

            st.subheader(f"🥇 Rank #{st.session_state.selected_grid_result + 1} Configuration")

            # Metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric("Return", f"{selected_result['return_pct']:+.2f}%")

            with metric_col2:
                sharpe = selected_result.get('sharpe_ratio', 0) if selected_result.get('sharpe_ratio') else 0
                st.metric("Sharpe Ratio", f"{sharpe:.3f}")

            with metric_col3:
                st.metric("Total Trades", selected_result['total_trades'])

            with metric_col4:
                st.metric("Win Rate", f"{selected_result.get('win_rate', 0):.1f}%")

            # Parameters
            st.markdown("### ⚙️ Optimal Parameters")
            param_cols = st.columns(min(len(param_ranges), 4))

            for idx, (param_name, param_value) in enumerate(selected_result['parameters'].items()):
                if param_name in param_ranges:
                    with param_cols[idx % len(param_cols)]:
                        st.metric(param_name.capitalize(), param_value)

            # Action buttons
            st.markdown("---")
            action_col1, action_col2 = st.columns(2)

            with action_col1:
                if st.button("💾 Save to Database", key="save_grid_result"):
                    try:
                        backtest_id = db.save_backtest(
                            results=selected_result,
                            strategy=strategy_name,
                            parameters=selected_result['parameters'],
                            notes=f"Grid search optimized (Rank #{st.session_state.selected_grid_result + 1})"
                        )
                        st.success(f"• Saved configuration to database (ID: {backtest_id})")
                    except Exception as e:
                        st.error(f"Failed to save: {str(e)}")

            with action_col2:
                if st.button("📡 Add to Monitoring", key="monitor_grid_result"):
                    try:
                        monitor_id = db.add_to_monitoring(
                            ticker=selected_result['ticker'],
                            strategy=strategy_name,
                            interval=selected_result['interval'],
                            parameters=selected_result['parameters']
                        )
                        st.success(f"• Added to monitoring (ID: {monitor_id})")
                    except Exception as e:
                        st.error(f"Failed to add: {str(e)}")

            # Chart
            st.markdown("---")
            st.subheader("📊 Performance Chart")

            with st.spinner("Loading chart..."):
                fig = create_backtest_chart(
                    ticker=selected_result['ticker'],
                    start_date=selected_result['start_date'],
                    end_date=selected_result['end_date'],
                    interval=selected_result['interval'],
                    trades=selected_result.get('trades', []),
                    strategy_name=strategy_name,
                    strategy_params=selected_result['parameters']
                )

            if fig:
                st.plotly_chart(fig, use_container_width=True)

            # Trades table
            if selected_result.get('trades'):
                st.markdown("---")
                st.subheader("📋 Trade Details")

                trades_df = create_trades_table(selected_result['trades'])
                if not trades_df.empty:
                    st.dataframe(trades_df, use_container_width=True, height=300)

        # Comparison table
        st.markdown("---")
        st.subheader("📊 Top 5 Comparison")

        comparison_data = []
        for idx, result in enumerate(top_results):
            row = {
                'Rank': idx + 1,
                'Return %': f"{result['return_pct']:+.2f}",
                'Sharpe': f"{result.get('sharpe_ratio', 0):.3f}" if result.get('sharpe_ratio') else "N/A",
                'Trades': result['total_trades'],
                'Win Rate %': f"{result.get('win_rate', 0):.1f}",
                'Final Value': f"${result['end_value']:,.2f}"
            }

            # Add parameter values
            for param_name in param_ranges.keys():
                row[param_name.capitalize()] = result['parameters'].get(param_name, '')

            comparison_data.append(row)

        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
