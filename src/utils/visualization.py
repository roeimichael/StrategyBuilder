"""
Visualization utilities for StrategyBuilder
Creates interactive charts with entry/exit signals
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
from typing import List, Dict, Any
import streamlit as st
import numpy as np


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average"""
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average"""
    return data.ewm(span=period, adjust=False).mean()


def calculate_bollinger_bands(data: pd.Series, period: int = 20, devfactor: float = 2.0):
    """Calculate Bollinger Bands"""
    sma = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()
    upper = sma + (std * devfactor)
    lower = sma - (std * devfactor)
    return upper, sma, lower


def calculate_tema(data: pd.Series, period: int) -> pd.Series:
    """Calculate Triple Exponential Moving Average"""
    ema1 = data.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    tema = 3 * ema1 - 3 * ema2 + ema3
    return tema


def calculate_keltner_channel(data: pd.DataFrame, ema_period: int = 20,
                              atr_period: int = 10, atr_multiplier: float = 2.0):
    """Calculate Keltner Channels"""
    # EMA as middle line
    middle = data['Close'].ewm(span=ema_period, adjust=False).mean()

    # ATR calculation
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(atr_period).mean()

    upper = middle + (atr * atr_multiplier)
    lower = middle - (atr * atr_multiplier)

    return upper, middle, lower


def add_strategy_indicators(fig, data: pd.DataFrame, strategy_name: str,
                           params: Dict[str, Any], row: int, col: int):
    """Add strategy-specific indicators to the chart"""

    if strategy_name == 'Bollinger Bands':
        # Calculate Bollinger Bands
        period = params.get('period', 20)
        devfactor = params.get('devfactor', 2.0)
        upper, middle, lower = calculate_bollinger_bands(data['Close'], period, devfactor)

        # Add upper band
        fig.add_trace(
            go.Scatter(
                x=data.index, y=upper,
                name=f'BB Upper ({period}, {devfactor})',
                line=dict(color='#94a3b8', width=1, dash='dash'),
                opacity=0.7
            ),
            row=row, col=col
        )

        # Add middle band (SMA)
        fig.add_trace(
            go.Scatter(
                x=data.index, y=middle,
                name=f'BB Middle (SMA {period})',
                line=dict(color='#fbbf24', width=2),
                opacity=0.8
            ),
            row=row, col=col
        )

        # Add lower band
        fig.add_trace(
            go.Scatter(
                x=data.index, y=lower,
                name=f'BB Lower ({period}, {devfactor})',
                line=dict(color='#94a3b8', width=1, dash='dash'),
                opacity=0.7
            ),
            row=row, col=col
        )

    elif strategy_name == 'TEMA Crossover':
        # TEMA 20/60 crossover
        tema20 = calculate_tema(data['Close'], 20)
        tema60 = calculate_tema(data['Close'], 60)

        fig.add_trace(
            go.Scatter(
                x=data.index, y=tema20,
                name='TEMA 20',
                line=dict(color='#3b82f6', width=2),
                opacity=0.8
            ),
            row=row, col=col
        )

        fig.add_trace(
            go.Scatter(
                x=data.index, y=tema60,
                name='TEMA 60',
                line=dict(color='#f59e0b', width=2),
                opacity=0.8
            ),
            row=row, col=col
        )

    elif strategy_name == 'TEMA + MACD':
        # Show TEMA lines
        tema_period = 30  # Default TEMA period for this strategy
        tema = calculate_tema(data['Close'], tema_period)

        fig.add_trace(
            go.Scatter(
                x=data.index, y=tema,
                name=f'TEMA {tema_period}',
                line=dict(color='#3b82f6', width=2),
                opacity=0.8
            ),
            row=row, col=col
        )

    elif strategy_name == 'Alligator':
        # Bill Williams Alligator with 3 SMAs
        jaw = calculate_sma(data['Close'], 13).shift(8)  # Blue line
        teeth = calculate_sma(data['Close'], 8).shift(5)  # Red line
        lips = calculate_sma(data['Close'], 5).shift(3)  # Green line

        fig.add_trace(
            go.Scatter(
                x=data.index, y=jaw,
                name='Alligator Jaw (13)',
                line=dict(color='#3b82f6', width=2),
                opacity=0.7
            ),
            row=row, col=col
        )

        fig.add_trace(
            go.Scatter(
                x=data.index, y=teeth,
                name='Alligator Teeth (8)',
                line=dict(color='#ef4444', width=2),
                opacity=0.7
            ),
            row=row, col=col
        )

        fig.add_trace(
            go.Scatter(
                x=data.index, y=lips,
                name='Alligator Lips (5)',
                line=dict(color='#10b981', width=2),
                opacity=0.7
            ),
            row=row, col=col
        )

    elif strategy_name == 'Keltner Channel':
        # Calculate Keltner Channels
        ema_period = params.get('ema_period', 20)
        atr_period = params.get('atr_period', 10)
        atr_multiplier = params.get('atr_multiplier', 2.0)

        upper, middle, lower = calculate_keltner_channel(
            data, ema_period, atr_period, atr_multiplier
        )

        # Add upper channel
        fig.add_trace(
            go.Scatter(
                x=data.index, y=upper,
                name=f'Keltner Upper ({ema_period}, {atr_multiplier}x)',
                line=dict(color='#94a3b8', width=1, dash='dash'),
                opacity=0.7
            ),
            row=row, col=col
        )

        # Add middle line (EMA)
        fig.add_trace(
            go.Scatter(
                x=data.index, y=middle,
                name=f'Keltner Middle (EMA {ema_period})',
                line=dict(color='#fbbf24', width=2),
                opacity=0.8
            ),
            row=row, col=col
        )

        # Add lower channel
        fig.add_trace(
            go.Scatter(
                x=data.index, y=lower,
                name=f'Keltner Lower ({ema_period}, {atr_multiplier}x)',
                line=dict(color='#94a3b8', width=1, dash='dash'),
                opacity=0.7
            ),
            row=row, col=col
        )

    elif strategy_name == 'ADX Adaptive':
        # Show EMA for trend mode
        ema_fast = calculate_ema(data['Close'], 10)
        ema_slow = calculate_ema(data['Close'], 30)

        fig.add_trace(
            go.Scatter(
                x=data.index, y=ema_fast,
                name='EMA 10 (Fast)',
                line=dict(color='#3b82f6', width=1.5),
                opacity=0.7
            ),
            row=row, col=col
        )

        fig.add_trace(
            go.Scatter(
                x=data.index, y=ema_slow,
                name='EMA 30 (Slow)',
                line=dict(color='#f59e0b', width=1.5),
                opacity=0.7
            ),
            row=row, col=col
        )


def create_backtest_chart(ticker: str, start_date, end_date, interval: str,
                         trades: List[Dict[str, Any]], strategy_name: str = None,
                         strategy_params: Dict[str, Any] = None) -> go.Figure:
    """
    Create interactive chart with price action, entry/exit signals, and strategy indicators

    Args:
        ticker: Stock symbol
        start_date: Start date for data
        end_date: End date for data
        interval: Time interval
        trades: List of trade dictionaries with entry/exit info
        strategy_name: Name of the strategy used
        strategy_params: Parameters used for the strategy

    Returns:
        Plotly figure object
    """
    # Download price data
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)

        if data.empty:
            st.error(f"No data available for {ticker}")
            return None

        # Fix for yfinance 0.2.31+ which returns MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Ensure all column names are strings
        if len(data.columns) > 0 and isinstance(data.columns[0], tuple):
            data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

        # Create figure with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{ticker} Price Action with Trade Signals', 'Volume'),
            row_heights=[0.7, 0.3]
        )

        # Add candlestick chart (Dark mode colors)
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price',
                increasing_line_color='#10b981',
                decreasing_line_color='#ef4444'
            ),
            row=1, col=1
        )

        # Add strategy indicators based on strategy type
        if strategy_name and strategy_params:
            add_strategy_indicators(fig, data, strategy_name, strategy_params, row=1, col=1)

        # Add entry and exit markers
        if trades:
            entry_dates = []
            entry_prices = []
            exit_dates = []
            exit_prices = []
            colors_entry = []
            colors_exit = []

            for trade in trades:
                entry_dates.append(trade['entry_date'])
                entry_prices.append(trade['entry_price'])
                exit_dates.append(trade['exit_date'])
                exit_prices.append(trade['exit_price'])

                # Color based on profit/loss (Dark mode colors)
                if trade['pnl'] > 0:
                    colors_entry.append('#10b981')
                    colors_exit.append('#10b981')
                else:
                    colors_entry.append('#ef4444')
                    colors_exit.append('#ef4444')

            # Add buy signals (triangles pointing up)
            fig.add_trace(
                go.Scatter(
                    x=entry_dates,
                    y=entry_prices,
                    mode='markers',
                    name='Entry (Buy)',
                    marker=dict(
                        symbol='triangle-up',
                        size=15,
                        color=colors_entry,
                        line=dict(width=2, color='#1e293b')
                    ),
                    hovertemplate='<b>Entry</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )

            # Add sell signals (triangles pointing down)
            fig.add_trace(
                go.Scatter(
                    x=exit_dates,
                    y=exit_prices,
                    mode='markers',
                    name='Exit (Sell)',
                    marker=dict(
                        symbol='triangle-down',
                        size=15,
                        color=colors_exit,
                        line=dict(width=2, color='#1e293b')
                    ),
                    hovertemplate='<b>Exit</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )

        # Add volume bars (Dark mode colors)
        colors = ['#ef4444' if close < open_ else '#10b981'
                 for close, open_ in zip(data['Close'], data['Open'])]

        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=colors,
                showlegend=False,
                opacity=0.6
            ),
            row=2, col=1
        )

        # Update layout (Dark mode template)
        fig.update_layout(
            title=f'{ticker} Backtest Visualization',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            xaxis2_title='Date',
            yaxis2_title='Volume',
            hovermode='x unified',
            height=800,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            template='plotly_dark',
            paper_bgcolor='#101420',
            plot_bgcolor='#101420',
            font=dict(color='#e2e8f0')
        )

        # Minimize gridlines for clean look
        fig.update_xaxes(showgrid=False, gridcolor='#2D3748', gridwidth=0.5)
        fig.update_yaxes(showgrid=True, gridcolor='#2D3748', gridwidth=0.5)

        # Remove rangeslider
        fig.update_xaxes(rangeslider_visible=False, row=1, col=1)

        return fig

    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None


def create_trades_table(trades: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create a formatted DataFrame of trade details

    Args:
        trades: List of trade dictionaries

    Returns:
        Pandas DataFrame with trade details
    """
    if not trades:
        return pd.DataFrame()

    df = pd.DataFrame(trades)

    # Format columns
    df['Entry Date'] = pd.to_datetime(df['entry_date']).dt.strftime('%Y-%m-%d')
    df['Exit Date'] = pd.to_datetime(df['exit_date']).dt.strftime('%Y-%m-%d')
    df['Entry Price'] = df['entry_price'].apply(lambda x: f'${x:.2f}')
    df['Exit Price'] = df['exit_price'].apply(lambda x: f'${x:.2f}')
    df['Size'] = df['size'].apply(lambda x: f'{int(x)}')
    df['P&L'] = df['pnl'].apply(lambda x: f'${x:+,.2f}')
    df['Return %'] = df['pnl_pct'].apply(lambda x: f'{x:+.2f}%')

    # Select and reorder columns
    result_df = df[[
        'Entry Date', 'Exit Date', 'Entry Price', 'Exit Price',
        'Size', 'P&L', 'Return %'
    ]]

    # Add trade number
    result_df.insert(0, 'Trade #', range(1, len(result_df) + 1))

    return result_df


def create_performance_metrics_chart(trades: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a chart showing cumulative P&L over time

    Args:
        trades: List of trade dictionaries

    Returns:
        Plotly figure showing cumulative returns
    """
    if not trades:
        return None

    df = pd.DataFrame(trades)
    df['cumulative_pnl'] = df['pnl'].cumsum()
    df['exit_date'] = pd.to_datetime(df['exit_date'])

    fig = go.Figure()

    # Add cumulative P&L line (Dark mode)
    fig.add_trace(
        go.Scatter(
            x=df['exit_date'],
            y=df['cumulative_pnl'],
            mode='lines+markers',
            name='Cumulative P&L',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8, color='#3b82f6'),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.2)',
            hovertemplate='<b>Date:</b> %{x}<br><b>Cumulative P&L:</b> $%{y:,.2f}<extra></extra>'
        )
    )

    # Add zero line
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#94a3b8",
        annotation_text="Break Even",
        annotation_position="right",
        annotation_font_color="#94a3b8"
    )

    fig.update_layout(
        title='Cumulative Profit & Loss',
        xaxis_title='Date',
        yaxis_title='Cumulative P&L ($)',
        hovermode='x',
        height=400,
        template='plotly_dark',
        paper_bgcolor='#101420',
        plot_bgcolor='#101420',
        font=dict(color='#e2e8f0')
    )

    # Minimize gridlines
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#2D3748', gridwidth=0.5)

    return fig


def create_trade_distribution_chart(trades: List[Dict[str, Any]]) -> go.Figure:
    """
    Create histogram showing distribution of trade returns

    Args:
        trades: List of trade dictionaries

    Returns:
        Plotly figure showing return distribution
    """
    if not trades:
        return None

    df = pd.DataFrame(trades)

    fig = go.Figure()

    # Separate winning and losing trades
    winning_trades = df[df['pnl'] > 0]['pnl_pct']
    losing_trades = df[df['pnl'] < 0]['pnl_pct']

    # Add histogram for winning trades (Dark mode)
    fig.add_trace(
        go.Histogram(
            x=winning_trades,
            name='Winning Trades',
            marker_color='#10b981',
            opacity=0.7,
            xbins=dict(size=1)
        )
    )

    # Add histogram for losing trades (Dark mode)
    fig.add_trace(
        go.Histogram(
            x=losing_trades,
            name='Losing Trades',
            marker_color='#ef4444',
            opacity=0.7,
            xbins=dict(size=1)
        )
    )

    fig.update_layout(
        title='Trade Return Distribution',
        xaxis_title='Return (%)',
        yaxis_title='Number of Trades',
        barmode='overlay',
        height=400,
        template='plotly_dark',
        paper_bgcolor='#101420',
        plot_bgcolor='#101420',
        font=dict(color='#e2e8f0'),
        showlegend=True
    )

    # Minimize gridlines
    fig.update_xaxes(showgrid=True, gridcolor='#2D3748', gridwidth=0.5)
    fig.update_yaxes(showgrid=True, gridcolor='#2D3748', gridwidth=0.5)

    return fig
