"""Visualization utilities for StrategyBuilder - Creates interactive charts with strategy indicators"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import yfinance as yf
import numpy as np
import streamlit as st
from typing import List, Dict, Any, Tuple


# Technical Indicator Calculations
def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    return data.ewm(span=period, adjust=False).mean()


def calculate_bollinger_bands(data: pd.Series, period: int = 20, devfactor: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    sma = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()
    return sma + (std * devfactor), sma, sma - (std * devfactor)


def calculate_tema(data: pd.Series, period: int) -> pd.Series:
    ema1 = data.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    ema3 = ema2.ewm(span=period, adjust=False).mean()
    return 3 * ema1 - 3 * ema2 + ema3


def calculate_keltner_channel(data: pd.DataFrame, ema_period: int = 20,
                             atr_period: int = 10, atr_multiplier: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    middle = data['Close'].ewm(span=ema_period, adjust=False).mean()
    ranges = pd.concat([
        data['High'] - data['Low'],
        np.abs(data['High'] - data['Close'].shift()),
        np.abs(data['Low'] - data['Close'].shift())
    ], axis=1)
    atr = np.max(ranges, axis=1).rolling(atr_period).mean()
    return middle + (atr * atr_multiplier), middle, middle - (atr * atr_multiplier)


# Chart Styling Constants
COLORS = {
    'green': '#10b981',
    'red': '#ef4444',
    'blue': '#3b82f6',
    'orange': '#f59e0b',
    'yellow': '#fbbf24',
    'gray': '#94a3b8',
    'dark_bg': '#101420'
}

CHART_LAYOUT = {
    'template': 'plotly_dark',
    'paper_bgcolor': COLORS['dark_bg'],
    'plot_bgcolor': COLORS['dark_bg'],
    'font': {'color': '#e2e8f0'},
    'hovermode': 'x unified'
}


def add_indicator_line(fig, x, y, name: str, color: str, width: int = 2,
                       dash: str = 'solid', opacity: float = 0.8, row: int = 1, col: int = 1):
    """Helper to add indicator line to chart"""
    fig.add_trace(go.Scatter(
        x=x, y=y, name=name,
        line={'color': color, 'width': width, 'dash': dash},
        opacity=opacity
    ), row=row, col=col)


def add_strategy_indicators(fig, data: pd.DataFrame, strategy_name: str,
                           params: Dict[str, Any], row: int, col: int):
    """Add strategy-specific indicators to chart"""

    if strategy_name == 'Bollinger Bands':
        period, devfactor = params.get('period', 20), params.get('devfactor', 2.0)
        upper, middle, lower = calculate_bollinger_bands(data['Close'], period, devfactor)
        add_indicator_line(fig, data.index, upper, f'BB Upper ({period}, {devfactor})',
                          COLORS['gray'], 1, 'dash', 0.7, row, col)
        add_indicator_line(fig, data.index, middle, f'BB Middle (SMA {period})',
                          COLORS['yellow'], 2, 'solid', 0.8, row, col)
        add_indicator_line(fig, data.index, lower, f'BB Lower ({period}, {devfactor})',
                          COLORS['gray'], 1, 'dash', 0.7, row, col)

    elif strategy_name == 'TEMA Crossover':
        tema20 = calculate_tema(data['Close'], 20)
        tema60 = calculate_tema(data['Close'], 60)
        add_indicator_line(fig, data.index, tema20, 'TEMA 20', COLORS['blue'], 2, 'solid', 0.8, row, col)
        add_indicator_line(fig, data.index, tema60, 'TEMA 60', COLORS['orange'], 2, 'solid', 0.8, row, col)

    elif strategy_name == 'TEMA + MACD':
        tema = calculate_tema(data['Close'], 30)
        add_indicator_line(fig, data.index, tema, 'TEMA 30', COLORS['blue'], 2, 'solid', 0.8, row, col)

    elif strategy_name == 'Alligator':
        jaw = calculate_sma(data['Close'], 13).shift(8)
        teeth = calculate_sma(data['Close'], 8).shift(5)
        lips = calculate_sma(data['Close'], 5).shift(3)
        add_indicator_line(fig, data.index, jaw, 'Alligator Jaw (13)', COLORS['blue'], 2, 'solid', 0.7, row, col)
        add_indicator_line(fig, data.index, teeth, 'Alligator Teeth (8)', COLORS['red'], 2, 'solid', 0.7, row, col)
        add_indicator_line(fig, data.index, lips, 'Alligator Lips (5)', COLORS['green'], 2, 'solid', 0.7, row, col)

    elif strategy_name == 'Keltner Channel':
        ema_period = params.get('ema_period', 20)
        atr_period = params.get('atr_period', 10)
        atr_multiplier = params.get('atr_multiplier', 2.0)
        upper, middle, lower = calculate_keltner_channel(data, ema_period, atr_period, atr_multiplier)
        add_indicator_line(fig, data.index, upper, f'Keltner Upper ({ema_period}, {atr_multiplier}x)',
                          COLORS['gray'], 1, 'dash', 0.7, row, col)
        add_indicator_line(fig, data.index, middle, f'Keltner Middle (EMA {ema_period})',
                          COLORS['yellow'], 2, 'solid', 0.8, row, col)
        add_indicator_line(fig, data.index, lower, f'Keltner Lower ({ema_period}, {atr_multiplier}x)',
                          COLORS['gray'], 1, 'dash', 0.7, row, col)

    elif strategy_name == 'ADX Adaptive':
        ema_fast = calculate_ema(data['Close'], 10)
        ema_slow = calculate_ema(data['Close'], 30)
        add_indicator_line(fig, data.index, ema_fast, 'EMA 10 (Fast)', COLORS['blue'], 1.5, 'solid', 0.7, row, col)
        add_indicator_line(fig, data.index, ema_slow, 'EMA 30 (Slow)', COLORS['orange'], 1.5, 'solid', 0.7, row, col)


def create_backtest_chart(ticker: str, start_date, end_date, interval: str,
                         trades: List[Dict[str, Any]], strategy_name: str = None,
                         strategy_params: Dict[str, Any] = None) -> go.Figure:
    """Create interactive chart with price action, signals, and strategy indicators"""
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        if data.empty:
            st.error(f"No data available for {ticker}")
            return None

        # Handle MultiIndex columns from yfinance
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03,
            subplot_titles=(f'{ticker} Price Action with Trade Signals', 'Volume'),
            row_heights=[0.7, 0.3]
        )

        # Add candlestick
        fig.add_trace(go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'],
            low=data['Low'], close=data['Close'], name='Price',
            increasing_line_color=COLORS['green'], decreasing_line_color=COLORS['red']
        ), row=1, col=1)

        # Add strategy indicators
        if strategy_name and strategy_params:
            add_strategy_indicators(fig, data, strategy_name, strategy_params, 1, 1)

        # Add trade markers
        if trades:
            entry_dates, entry_prices, exit_dates, exit_prices = [], [], [], []
            colors_entry, colors_exit = [], []

            for trade in trades:
                entry_dates.append(trade['entry_date'])
                entry_prices.append(trade['entry_price'])
                exit_dates.append(trade['exit_date'])
                exit_prices.append(trade['exit_price'])
                color = COLORS['green'] if trade['pnl'] > 0 else COLORS['red']
                colors_entry.append(color)
                colors_exit.append(color)

            fig.add_trace(go.Scatter(
                x=entry_dates, y=entry_prices, mode='markers', name='Entry (Buy)',
                marker={'symbol': 'triangle-up', 'size': 15, 'color': colors_entry,
                       'line': {'width': 2, 'color': '#1e293b'}},
                hovertemplate='<b>Entry</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=exit_dates, y=exit_prices, mode='markers', name='Exit (Sell)',
                marker={'symbol': 'triangle-down', 'size': 15, 'color': colors_exit,
                       'line': {'width': 2, 'color': '#1e293b'}},
                hovertemplate='<b>Exit</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
            ), row=1, col=1)

        # Add volume bars
        colors = [COLORS['red'] if c < o else COLORS['green']
                 for c, o in zip(data['Close'], data['Open'])]
        fig.add_trace(go.Bar(
            x=data.index, y=data['Volume'], name='Volume',
            marker_color=colors, showlegend=False, opacity=0.6
        ), row=2, col=1)

        # Update layout
        fig.update_layout(
            title=f'{ticker} Backtest Visualization',
            xaxis_title='Date', yaxis_title='Price ($)',
            xaxis2_title='Date', yaxis2_title='Volume',
            height=800, showlegend=True,
            legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1},
            **CHART_LAYOUT
        )

        fig.update_xaxes(showgrid=False, rangeslider_visible=False)
        fig.update_yaxes(showgrid=True, gridcolor='#2D3748', gridwidth=0.5)

        return fig

    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return None


def create_trades_table(trades: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create formatted DataFrame of trade details"""
    if not trades:
        return pd.DataFrame()

    df = pd.DataFrame(trades)
    df['Entry Date'] = pd.to_datetime(df['entry_date']).dt.strftime('%Y-%m-%d')
    df['Exit Date'] = pd.to_datetime(df['exit_date']).dt.strftime('%Y-%m-%d')
    df['Entry Price'] = df['entry_price'].apply(lambda x: f'${x:.2f}')
    df['Exit Price'] = df['exit_price'].apply(lambda x: f'${x:.2f}')
    df['Size'] = df['size'].apply(lambda x: f'{int(x)}')
    df['P&L'] = df['pnl'].apply(lambda x: f'${x:+,.2f}')
    df['Return %'] = df['pnl_pct'].apply(lambda x: f'{x:+.2f}%')

    result = df[['Entry Date', 'Exit Date', 'Entry Price', 'Exit Price', 'Size', 'P&L', 'Return %']]
    result.insert(0, 'Trade #', range(1, len(result) + 1))
    return result


def create_performance_metrics_chart(trades: List[Dict[str, Any]]) -> go.Figure:
    """Create cumulative P&L chart"""
    if not trades:
        return None

    df = pd.DataFrame(trades)
    df['cumulative_pnl'] = df['pnl'].cumsum()
    df['exit_date'] = pd.to_datetime(df['exit_date'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['exit_date'], y=df['cumulative_pnl'], mode='lines+markers',
        name='Cumulative P&L', line={'color': COLORS['blue'], 'width': 3},
        marker={'size': 8, 'color': COLORS['blue']},
        fill='tozeroy', fillcolor='rgba(59, 130, 246, 0.2)',
        hovertemplate='<b>Date:</b> %{x}<br><b>Cumulative P&L:</b> $%{y:,.2f}<extra></extra>'
    ))

    fig.add_hline(y=0, line_dash='dash', line_color=COLORS['gray'],
                 annotation_text='Break Even', annotation_position='right',
                 annotation_font_color=COLORS['gray'])

    fig.update_layout(
        title='Cumulative Profit & Loss',
        xaxis_title='Date', yaxis_title='Cumulative P&L ($)',
        height=400, **CHART_LAYOUT
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#2D3748', gridwidth=0.5)

    return fig


def create_trade_distribution_chart(trades: List[Dict[str, Any]]) -> go.Figure:
    """Create histogram of trade return distribution"""
    if not trades:
        return None

    df = pd.DataFrame(trades)
    winning_trades = df[df['pnl'] > 0]['pnl_pct']
    losing_trades = df[df['pnl'] < 0]['pnl_pct']

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=winning_trades, name='Winning Trades',
        marker_color=COLORS['green'], opacity=0.7, xbins={'size': 1}
    ))
    fig.add_trace(go.Histogram(
        x=losing_trades, name='Losing Trades',
        marker_color=COLORS['red'], opacity=0.7, xbins={'size': 1}
    ))

    fig.update_layout(
        title='Trade Return Distribution',
        xaxis_title='Return (%)', yaxis_title='Number of Trades',
        barmode='overlay', height=400, showlegend=True, **CHART_LAYOUT
    )
    fig.update_xaxes(showgrid=True, gridcolor='#2D3748', gridwidth=0.5)
    fig.update_yaxes(showgrid=True, gridcolor='#2D3748', gridwidth=0.5)

    return fig
