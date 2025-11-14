"""Advanced charting with Plotly for TradingView-style visualizations

This module provides professional charting capabilities including:
- OHLCV candlestick charts
- Multiple indicator overlays
- Interactive zoom and pan
- Volume analysis
- Trade markers
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime


class AdvancedChartBuilder:
    """Build professional TradingView-style charts with Plotly"""

    def __init__(self, data: pd.DataFrame, title: str = "Strategy Backtest"):
        """
        Initialize chart builder

        Args:
            data: DataFrame with OHLCV data (columns: Open, High, Low, Close, Volume)
            title: Chart title
        """
        self.data = data.copy()
        self.title = title
        self.fig = None

    def create_candlestick_chart(self, show_volume: bool = True,
                                height: int = 800) -> go.Figure:
        """
        Create candlestick chart with optional volume subplot

        Args:
            show_volume: Whether to show volume subplot
            height: Chart height in pixels

        Returns:
            Plotly Figure object
        """
        if show_volume:
            # Create subplot with volume
            self.fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                row_heights=[0.7, 0.3],
                subplot_titles=(self.title, 'Volume')
            )

            # Add candlestick
            candlestick = go.Candlestick(
                x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name='OHLC',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            )
            self.fig.add_trace(candlestick, row=1, col=1)

            # Add volume bars
            colors = ['#26a69a' if close >= open else '#ef5350'
                     for close, open in zip(self.data['Close'], self.data['Open'])]

            volume_bars = go.Bar(
                x=self.data.index,
                y=self.data['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.5
            )
            self.fig.add_trace(volume_bars, row=2, col=1)

        else:
            # Create single candlestick chart
            self.fig = go.Figure()

            candlestick = go.Candlestick(
                x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name='OHLC',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            )
            self.fig.add_trace(candlestick)

        # Update layout
        self.fig.update_layout(
            title=self.title,
            yaxis_title='Price',
            xaxis_title='Date',
            height=height,
            template='plotly_dark',
            hovermode='x unified',
            xaxis_rangeslider_visible=False,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        return self.fig

    def add_sma(self, period: int, name: Optional[str] = None, color: str = '#2196F3',
                row: int = 1, col: int = 1):
        """
        Add Simple Moving Average indicator

        Args:
            period: SMA period
            name: Indicator name
            color: Line color
            row: Subplot row
            col: Subplot column
        """
        if self.fig is None:
            self.create_candlestick_chart()

        sma = self.data['Close'].rolling(window=period).mean()
        name = name or f'SMA({period})'

        self.fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=sma,
                name=name,
                line=dict(color=color, width=1.5),
                opacity=0.7
            ),
            row=row, col=col
        )

    def add_ema(self, period: int, name: Optional[str] = None, color: str = '#FF6F00',
                row: int = 1, col: int = 1):
        """
        Add Exponential Moving Average indicator

        Args:
            period: EMA period
            name: Indicator name
            color: Line color
            row: Subplot row
            col: Subplot column
        """
        if self.fig is None:
            self.create_candlestick_chart()

        ema = self.data['Close'].ewm(span=period, adjust=False).mean()
        name = name or f'EMA({period})'

        self.fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=ema,
                name=name,
                line=dict(color=color, width=1.5),
                opacity=0.7
            ),
            row=row, col=col
        )

    def add_bollinger_bands(self, period: int = 20, std_dev: float = 2.0,
                           color: str = '#9C27B0', row: int = 1, col: int = 1):
        """
        Add Bollinger Bands indicator

        Args:
            period: Moving average period
            std_dev: Standard deviation multiplier
            color: Band color
            row: Subplot row
            col: Subplot column
        """
        if self.fig is None:
            self.create_candlestick_chart()

        sma = self.data['Close'].rolling(window=period).mean()
        std = self.data['Close'].rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        # Add upper band
        self.fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=upper_band,
                name=f'BB Upper({period},{std_dev})',
                line=dict(color=color, width=1, dash='dash'),
                opacity=0.5
            ),
            row=row, col=col
        )

        # Add middle band (SMA)
        self.fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=sma,
                name=f'BB Middle({period})',
                line=dict(color=color, width=1.5),
                opacity=0.6
            ),
            row=row, col=col
        )

        # Add lower band with fill
        self.fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=lower_band,
                name=f'BB Lower({period},{std_dev})',
                line=dict(color=color, width=1, dash='dash'),
                fill='tonexty',
                fillcolor=f'rgba(156, 39, 176, 0.1)',
                opacity=0.5
            ),
            row=row, col=col
        )

    def add_rsi(self, period: int = 14, overbought: float = 70,
               oversold: float = 30):
        """
        Add RSI indicator as a subplot

        Args:
            period: RSI period
            overbought: Overbought level
            oversold: Oversold level
        """
        # Calculate RSI
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # Create new subplot if needed
        if not hasattr(self.fig, 'data') or len(self.fig.data) == 0:
            self.create_candlestick_chart(show_volume=False)

        # Add RSI subplot
        self.fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=rsi,
                name=f'RSI({period})',
                line=dict(color='#FFC107', width=2)
            )
        )

        # Add overbought/oversold lines
        self.fig.add_hline(y=overbought, line_dash="dash", line_color="red",
                          opacity=0.5, annotation_text="Overbought")
        self.fig.add_hline(y=oversold, line_dash="dash", line_color="green",
                          opacity=0.5, annotation_text="Oversold")

    def add_trade_markers(self, trades: List[Dict[str, Any]], row: int = 1, col: int = 1):
        """
        Add buy/sell trade markers to the chart

        Args:
            trades: List of trade dictionaries with entry_date, exit_date, entry_price, exit_price, pnl
            row: Subplot row
            col: Subplot column
        """
        if self.fig is None:
            self.create_candlestick_chart()

        # Extract buy and sell points
        buy_dates = []
        buy_prices = []
        sell_dates = []
        sell_prices = []
        hover_texts_buy = []
        hover_texts_sell = []

        for trade in trades:
            entry_date = trade.get('entry_date')
            exit_date = trade.get('exit_date')
            entry_price = trade.get('entry_price')
            exit_price = trade.get('exit_price')
            pnl = trade.get('pnl', 0)

            if entry_date and entry_price:
                buy_dates.append(entry_date)
                buy_prices.append(entry_price)
                hover_texts_buy.append(f"Buy: ${entry_price:.2f}")

            if exit_date and exit_price:
                sell_dates.append(exit_date)
                sell_prices.append(exit_price)
                color = "green" if pnl > 0 else "red"
                hover_texts_sell.append(f"Sell: ${exit_price:.2f}<br>P&L: ${pnl:.2f}")

        # Add buy markers
        if buy_dates:
            self.fig.add_trace(
                go.Scatter(
                    x=buy_dates,
                    y=buy_prices,
                    mode='markers',
                    name='Buy',
                    marker=dict(
                        symbol='triangle-up',
                        size=12,
                        color='#4CAF50',
                        line=dict(color='white', width=1)
                    ),
                    text=hover_texts_buy,
                    hovertemplate='%{text}<extra></extra>'
                ),
                row=row, col=col
            )

        # Add sell markers
        if sell_dates:
            self.fig.add_trace(
                go.Scatter(
                    x=sell_dates,
                    y=sell_prices,
                    mode='markers',
                    name='Sell',
                    marker=dict(
                        symbol='triangle-down',
                        size=12,
                        color='#F44336',
                        line=dict(color='white', width=1)
                    ),
                    text=hover_texts_sell,
                    hovertemplate='%{text}<extra></extra>'
                ),
                row=row, col=col
            )

    def add_equity_curve(self, equity_curve: pd.Series):
        """
        Add equity curve as a subplot

        Args:
            equity_curve: Pandas Series with equity values
        """
        # This would typically be added as a separate chart
        # For now, we'll create a new figure
        equity_fig = go.Figure()

        equity_fig.add_trace(
            go.Scatter(
                x=equity_curve.index,
                y=equity_curve.values,
                name='Equity',
                line=dict(color='#2196F3', width=2),
                fill='tozeroy',
                fillcolor='rgba(33, 150, 243, 0.1)'
            )
        )

        equity_fig.update_layout(
            title='Equity Curve',
            yaxis_title='Portfolio Value ($)',
            xaxis_title='Date',
            template='plotly_dark',
            hovermode='x unified'
        )

        return equity_fig

    def get_figure(self) -> go.Figure:
        """Get the current figure"""
        return self.fig


def create_performance_chart(results: Dict[str, Any],
                            show_trades: bool = True) -> go.Figure:
    """
    Create comprehensive performance chart from backtest results

    Args:
        results: Backtest results dictionary
        show_trades: Whether to show trade markers

    Returns:
        Plotly Figure object
    """
    # This is a convenience function that can be imported and used directly
    # Extract data from results if available
    ticker = results.get('ticker', 'Strategy')
    trades = results.get('trades', [])

    # Create a simple equity curve visualization
    fig = go.Figure()

    if 'equity_curve' in results:
        equity_curve = results['equity_curve']
        if isinstance(equity_curve, pd.Series):
            fig.add_trace(
                go.Scatter(
                    x=equity_curve.index if hasattr(equity_curve, 'index') else list(range(len(equity_curve))),
                    y=equity_curve.values if hasattr(equity_curve, 'values') else equity_curve,
                    name='Equity',
                    line=dict(color='#2196F3', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(33, 150, 243, 0.1)'
                )
            )

    fig.update_layout(
        title=f'{ticker} - Equity Curve',
        yaxis_title='Portfolio Value ($)',
        xaxis_title='Date',
        template='plotly_dark',
        hovermode='x unified',
        height=500
    )

    return fig


def create_metrics_dashboard(results: Dict[str, Any]) -> go.Figure:
    """
    Create metrics dashboard with key performance indicators

    Args:
        results: Backtest results dictionary

    Returns:
        Plotly Figure object with metrics
    """
    # Extract metrics
    return_pct = results.get('return_pct', 0)
    sharpe_ratio = results.get('sharpe_ratio', 0)
    max_drawdown = results.get('max_drawdown', 0)
    total_trades = results.get('total_trades', 0)

    advanced_metrics = results.get('advanced_metrics', {})
    win_rate = advanced_metrics.get('win_rate', 0)
    profit_factor = advanced_metrics.get('profit_factor', 0)

    # Create figure with indicators
    fig = make_subplots(
        rows=2, cols=3,
        specs=[[{"type": "indicator"}] * 3,
               [{"type": "indicator"}] * 3],
        subplot_titles=('Return %', 'Sharpe Ratio', 'Max Drawdown %',
                       'Win Rate %', 'Profit Factor', 'Total Trades')
    )

    # Add indicators
    indicators = [
        (return_pct, 'Return %', 1, 1, "#4CAF50" if return_pct > 0 else "#F44336"),
        (sharpe_ratio, 'Sharpe', 1, 2, "#2196F3"),
        (max_drawdown, 'Max DD %', 1, 3, "#FF9800"),
        (win_rate, 'Win Rate %', 2, 1, "#9C27B0"),
        (profit_factor or 0, 'Profit Factor', 2, 2, "#00BCD4"),
        (total_trades, 'Trades', 2, 3, "#607D8B")
    ]

    for value, title, row, col, color in indicators:
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=value,
                title={'text': title},
                number={'font': {'size': 40}},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=row, col=col
        )

    fig.update_layout(
        height=400,
        template='plotly_dark',
        showlegend=False
    )

    return fig
