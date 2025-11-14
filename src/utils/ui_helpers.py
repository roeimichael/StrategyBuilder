"""UI/UX helpers for Streamlit applications

This module provides enhanced UI components including:
- Progress bars for long operations
- Loading spinners
- Tooltips for complex metrics
- Status indicators
- Interactive elements
"""

import streamlit as st
import time
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
import pandas as pd


# Metric tooltips/explanations
METRIC_TOOLTIPS = {
    'sharpe_ratio': """
    **Sharpe Ratio** measures risk-adjusted return.

    - Values > 1.0 are good
    - Values > 2.0 are very good
    - Values > 3.0 are excellent

    Formula: (Return - Risk Free Rate) / Standard Deviation
    """,

    'sortino_ratio': """
    **Sortino Ratio** is similar to Sharpe but only considers downside volatility.

    - Focuses on harmful volatility (losses)
    - Better measure for asymmetric return distributions
    - Higher values indicate better risk-adjusted returns
    """,

    'calmar_ratio': """
    **Calmar Ratio** measures return relative to maximum drawdown.

    - Higher values are better
    - Values > 1.0 indicate returns exceed maximum drawdown

    Formula: Annual Return / Maximum Drawdown
    """,

    'max_drawdown': """
    **Maximum Drawdown** is the largest peak-to-trough decline.

    - Measures worst-case loss from a peak
    - Lower percentages are better
    - Important for risk management
    """,

    'win_rate': """
    **Win Rate** is the percentage of profitable trades.

    - 50% = break-even win rate for equal profit/loss
    - Higher is generally better
    - Should be considered with payoff ratio
    """,

    'profit_factor': """
    **Profit Factor** is gross profit divided by gross loss.

    - Values > 1.0 are profitable
    - Values > 1.5 are good
    - Values > 2.0 are excellent

    Formula: Gross Profit / Gross Loss
    """,

    'payoff_ratio': """
    **Payoff Ratio** is average win divided by average loss.

    - Measures risk/reward per trade
    - Values > 1.0 mean avg win > avg loss
    - Higher values are better

    Formula: Average Win / Average Loss
    """,

    'expectancy': """
    **Expectancy** is the expected value per trade.

    - Positive values indicate profitable strategy
    - Measured in currency (e.g., dollars)
    - Accounts for both win rate and payoff ratio

    Formula: (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
    """
}


def show_metric_with_tooltip(label: str, value: Any, metric_key: Optional[str] = None,
                             delta: Optional[Any] = None, help_text: Optional[str] = None):
    """
    Display metric with tooltip

    Args:
        label: Metric label
        value: Metric value
        metric_key: Key for predefined tooltip (e.g., 'sharpe_ratio')
        delta: Optional delta value
        help_text: Custom help text (overrides predefined tooltip)
    """
    # Get tooltip text
    tooltip = help_text or METRIC_TOOLTIPS.get(metric_key, None)

    if tooltip:
        col1, col2 = st.columns([0.95, 0.05])
        with col1:
            st.metric(label=label, value=value, delta=delta)
        with col2:
            st.markdown("ℹ️", help=tooltip)
    else:
        st.metric(label=label, value=value, delta=delta)


def with_spinner(message: str = "Loading..."):
    """
    Decorator to show spinner during function execution

    Args:
        message: Loading message to display

    Example:
        @with_spinner("Running backtest...")
        def run_backtest():
            # Long operation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with st.spinner(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def progress_bar_wrapper(func: Callable, total_steps: int,
                         description: str = "Processing...") -> Callable:
    """
    Wrapper to show progress bar during operation

    Args:
        func: Function to execute
        total_steps: Total number of steps
        description: Progress description

    Returns:
        Wrapped function that updates progress bar
    """
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(current_step: int, status: str = ""):
        progress = current_step / total_steps
        progress_bar.progress(progress)
        status_text.text(f"{description} ({current_step}/{total_steps}) {status}")

    return update_progress


def show_grid_search_progress(param_grid: List[Dict[str, Any]],
                              current_index: int,
                              current_params: Dict[str, Any],
                              current_result: Optional[Dict[str, Any]] = None):
    """
    Show grid search progress with detailed information

    Args:
        param_grid: List of parameter combinations
        current_index: Current parameter index
        current_params: Current parameters being tested
        current_result: Optional current result
    """
    total = len(param_grid)
    progress = (current_index + 1) / total

    # Progress bar
    st.progress(progress)

    # Status information
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Progress", f"{current_index + 1}/{total}")

    with col2:
        st.metric("Completion", f"{progress * 100:.1f}%")

    with col3:
        if current_result:
            st.metric("Current Return", f"{current_result.get('return_pct', 0):.2f}%")

    # Current parameters
    with st.expander("Current Parameters"):
        st.json(current_params)


def create_status_indicator(status: str, message: str = ""):
    """
    Create colored status indicator

    Args:
        status: Status type ('success', 'error', 'warning', 'info')
        message: Status message
    """
    icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }

    colors = {
        'success': 'green',
        'error': 'red',
        'warning': 'orange',
        'info': 'blue'
    }

    icon = icons.get(status, '•')
    color = colors.get(status, 'gray')

    st.markdown(
        f"<span style='color: {color}; font-weight: bold;'>{icon} {message}</span>",
        unsafe_allow_html=True
    )


def show_performance_badge(return_pct: float):
    """
    Show performance badge based on return percentage

    Args:
        return_pct: Return percentage
    """
    if return_pct > 20:
        st.success(f"🚀 Excellent: {return_pct:.2f}%")
    elif return_pct > 10:
        st.success(f"✅ Good: {return_pct:.2f}%")
    elif return_pct > 0:
        st.info(f"📈 Positive: {return_pct:.2f}%")
    elif return_pct > -10:
        st.warning(f"📉 Negative: {return_pct:.2f}%")
    else:
        st.error(f"❌ Poor: {return_pct:.2f}%")


def create_comparison_table(results_list: List[Dict[str, Any]],
                           names: List[str],
                           highlight_best: bool = True):
    """
    Create comparison table with highlighting

    Args:
        results_list: List of result dictionaries
        names: List of strategy/configuration names
        highlight_best: Whether to highlight best values
    """
    # Build comparison data
    data = []
    for name, result in zip(names, results_list):
        row = {
            'Strategy': name,
            'Return %': result.get('return_pct', 0),
            'Sharpe': result.get('sharpe_ratio', 0),
            'Max DD %': result.get('max_drawdown', 0),
            'Trades': result.get('total_trades', 0)
        }

        # Add advanced metrics if available
        advanced = result.get('advanced_metrics', {})
        if advanced:
            row['Win Rate %'] = advanced.get('win_rate', 0)
            row['Profit Factor'] = advanced.get('profit_factor', 0)

        data.append(row)

    df = pd.DataFrame(data)

    if highlight_best:
        # Style the dataframe
        def highlight_max(s, props=''):
            return np.where(s == np.nanmax(s.values), props, '')

        def highlight_min_dd(s, props=''):
            return np.where(s == np.nanmin(s.values), props, '')

        styled_df = df.style.apply(
            highlight_max,
            props='background-color: #90EE90',
            subset=['Return %', 'Sharpe', 'Win Rate %', 'Profit Factor']
        ).apply(
            highlight_min_dd,
            props='background-color: #90EE90',
            subset=['Max DD %']
        )

        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)


def create_interactive_filter(data: pd.DataFrame,
                              column: str,
                              label: str = "Filter") -> pd.DataFrame:
    """
    Create interactive filter for dataframe

    Args:
        data: DataFrame to filter
        column: Column to filter on
        label: Filter label

    Returns:
        Filtered DataFrame
    """
    if column in data.columns:
        unique_values = data[column].unique()
        selected_values = st.multiselect(
            label,
            options=unique_values,
            default=unique_values
        )
        return data[data[column].isin(selected_values)]
    return data


def show_trade_analysis_tabs(trades: List[Dict[str, Any]]):
    """
    Show trade analysis in tabs

    Args:
        trades: List of trade dictionaries
    """
    if not trades:
        st.info("No trades to analyze")
        return

    tab1, tab2, tab3 = st.tabs(["All Trades", "Winners", "Losers"])

    df = pd.DataFrame(trades)
    winners = df[df['pnl'] > 0]
    losers = df[df['pnl'] < 0]

    with tab1:
        st.subheader(f"All Trades ({len(df)})")
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.subheader(f"Winning Trades ({len(winners)})")
        if len(winners) > 0:
            st.dataframe(winners, use_container_width=True)
            st.metric("Avg Win", f"${winners['pnl'].mean():.2f}")
        else:
            st.info("No winning trades")

    with tab3:
        st.subheader(f"Losing Trades ({len(losers)})")
        if len(losers) > 0:
            st.dataframe(losers, use_container_width=True)
            st.metric("Avg Loss", f"${losers['pnl'].mean():.2f}")
        else:
            st.info("No losing trades")


def create_download_button(data: Any, filename: str, file_label: str,
                           mime_type: str = "text/csv"):
    """
    Create download button for data

    Args:
        data: Data to download (str, bytes, or DataFrame)
        filename: Download filename
        file_label: Button label
        mime_type: MIME type
    """
    if isinstance(data, pd.DataFrame):
        data = data.to_csv(index=False)
        mime_type = "text/csv"

    st.download_button(
        label=file_label,
        data=data,
        file_name=filename,
        mime=mime_type
    )


def show_loading_animation(duration: float = 2.0, message: str = "Processing..."):
    """
    Show loading animation for a specific duration

    Args:
        duration: Duration in seconds
        message: Loading message
    """
    with st.spinner(message):
        time.sleep(duration)


# Import numpy only if needed for styling
try:
    import numpy as np
except ImportError:
    np = None


# Example usage in a Streamlit app
if __name__ == "__main__":
    st.title("UI/UX Helpers Demo")

    # Show metrics with tooltips
    st.header("Metrics with Tooltips")
    col1, col2, col3 = st.columns(3)

    with col1:
        show_metric_with_tooltip(
            "Sharpe Ratio",
            1.85,
            metric_key='sharpe_ratio'
        )

    with col2:
        show_metric_with_tooltip(
            "Max Drawdown",
            -15.3,
            metric_key='max_drawdown',
            delta="+2.1%"
        )

    with col3:
        show_metric_with_tooltip(
            "Win Rate",
            "65.2%",
            metric_key='win_rate'
        )

    # Show status indicators
    st.header("Status Indicators")
    create_status_indicator('success', "Backtest completed successfully")
    create_status_indicator('warning', "High volatility detected")
    create_status_indicator('error', "Insufficient data")
    create_status_indicator('info', "Processing 1000 parameter combinations")

    # Show performance badge
    st.header("Performance Badges")
    show_performance_badge(25.5)
    show_performance_badge(-8.3)
