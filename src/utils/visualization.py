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


def create_backtest_chart(ticker: str, start_date, end_date, interval: str,
                         trades: List[Dict[str, Any]]) -> go.Figure:
    """
    Create interactive chart with price action and entry/exit signals

    Args:
        ticker: Stock symbol
        start_date: Start date for data
        end_date: End date for data
        interval: Time interval
        trades: List of trade dictionaries with entry/exit info

    Returns:
        Plotly figure object
    """
    # Download price data
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)

        if data.empty:
            st.error(f"No data available for {ticker}")
            return None

        # Create figure with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{ticker} Price Action with Trade Signals', 'Volume'),
            row_heights=[0.7, 0.3]
        )

        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ),
            row=1, col=1
        )

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

                # Color based on profit/loss
                if trade['pnl'] > 0:
                    colors_entry.append('green')
                    colors_exit.append('green')
                else:
                    colors_entry.append('red')
                    colors_exit.append('red')

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
                        line=dict(width=2, color='white')
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
                        line=dict(width=2, color='white')
                    ),
                    hovertemplate='<b>Exit</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )

        # Add volume bars
        colors = ['red' if row['Close'] < row['Open'] else 'green'
                 for index, row in data.iterrows()]

        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=colors,
                showlegend=False
            ),
            row=2, col=1
        )

        # Update layout
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
            template='plotly_white'
        )

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

    # Add cumulative P&L line
    fig.add_trace(
        go.Scatter(
            x=df['exit_date'],
            y=df['cumulative_pnl'],
            mode='lines+markers',
            name='Cumulative P&L',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)',
            hovertemplate='<b>Date:</b> %{x}<br><b>Cumulative P&L:</b> $%{y:,.2f}<extra></extra>'
        )
    )

    # Add zero line
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        annotation_text="Break Even",
        annotation_position="right"
    )

    fig.update_layout(
        title='Cumulative Profit & Loss',
        xaxis_title='Date',
        yaxis_title='Cumulative P&L ($)',
        hovermode='x',
        height=400,
        template='plotly_white'
    )

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

    # Add histogram for winning trades
    fig.add_trace(
        go.Histogram(
            x=winning_trades,
            name='Winning Trades',
            marker_color='green',
            opacity=0.7,
            xbins=dict(size=1)
        )
    )

    # Add histogram for losing trades
    fig.add_trace(
        go.Histogram(
            x=losing_trades,
            name='Losing Trades',
            marker_color='red',
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
        template='plotly_white',
        showlegend=True
    )

    return fig
