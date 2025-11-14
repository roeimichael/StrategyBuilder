"""
Trading Concepts Glossary

Comprehensive glossary of trading and risk management terms
for educational purposes.
"""

from typing import Dict, List, Optional
import streamlit as st


TRADING_GLOSSARY: Dict[str, Dict[str, str]] = {
    # Performance Metrics
    "Sharpe Ratio": {
        "category": "Performance Metrics",
        "definition": "A measure of risk-adjusted return that compares the excess return of an investment to its volatility.",
        "formula": "(Portfolio Return - Risk-Free Rate) / Standard Deviation of Returns",
        "interpretation": "Higher is better. Values > 1.0 are good, > 2.0 are very good, > 3.0 are excellent.",
        "example": "A Sharpe ratio of 2.0 means you earn 2 units of return for every unit of risk taken."
    },
    "Sortino Ratio": {
        "category": "Performance Metrics",
        "definition": "Similar to Sharpe ratio but only penalizes downside volatility, not upside volatility.",
        "formula": "(Portfolio Return - Risk-Free Rate) / Downside Deviation",
        "interpretation": "Higher is better. More relevant than Sharpe for strategies with asymmetric returns.",
        "example": "A strategy with Sortino 3.0 has excellent risk-adjusted returns considering only downside risk."
    },
    "Calmar Ratio": {
        "category": "Performance Metrics",
        "definition": "Measures return relative to maximum drawdown over a specific period (usually 3 years).",
        "formula": "Annual Return / Maximum Drawdown",
        "interpretation": "Higher is better. Values > 3.0 indicate strong performance with controlled drawdowns.",
        "example": "Calmar ratio of 2.5 means annual return is 2.5x the maximum drawdown."
    },
    "Maximum Drawdown": {
        "category": "Risk Metrics",
        "definition": "The largest peak-to-trough decline in portfolio value during a specific period.",
        "formula": "(Trough Value - Peak Value) / Peak Value",
        "interpretation": "Lower is better (less negative). Measures worst-case loss from peak.",
        "example": "A -25% max drawdown means the portfolio lost 25% from its highest point."
    },
    "Win Rate": {
        "category": "Trade Statistics",
        "definition": "Percentage of trades that resulted in a profit.",
        "formula": "(Number of Winning Trades / Total Number of Trades) × 100",
        "interpretation": "Higher is generally better, but must be considered with profit factor.",
        "example": "60% win rate means 60 out of 100 trades were profitable."
    },
    "Profit Factor": {
        "category": "Trade Statistics",
        "definition": "Ratio of gross profits to gross losses.",
        "formula": "Total Gross Profit / Total Gross Loss",
        "interpretation": "Values > 1.0 are profitable. > 1.5 is good, > 2.0 is excellent.",
        "example": "Profit factor of 2.0 means profits are twice as large as losses."
    },
    "Payoff Ratio": {
        "category": "Trade Statistics",
        "definition": "Average winning trade size divided by average losing trade size.",
        "formula": "Average Win / Average Loss",
        "interpretation": "Higher is better. Shows if winners are larger than losers.",
        "example": "Payoff ratio of 3.0 means average winner is 3x larger than average loser."
    },
    "Expectancy": {
        "category": "Trade Statistics",
        "definition": "Average amount you can expect to win or lose per trade.",
        "formula": "(Win Rate × Average Win) - (Loss Rate × Average Loss)",
        "interpretation": "Positive values indicate profitable strategy. Higher is better.",
        "example": "Expectancy of $50 means you expect to make $50 per trade on average."
    },

    # Risk Management
    "Portfolio Heat": {
        "category": "Risk Management",
        "definition": "Total risk exposure across all open positions as a percentage of portfolio value.",
        "formula": "Sum of (Position Size × Stop Loss Distance) / Portfolio Value",
        "interpretation": "Lower is more conservative. Typical limits: 10-20% of portfolio.",
        "example": "15% portfolio heat means total risk across all positions is 15% of capital."
    },
    "Position Sizing": {
        "category": "Risk Management",
        "definition": "Method of determining how much capital to allocate to each trade.",
        "formula": "Various methods: Fixed %, Risk-based, Volatility-adjusted, Kelly Criterion",
        "interpretation": "Critical for risk management. Should align with risk tolerance.",
        "example": "Risk 2% per trade means if stopped out, you lose 2% of capital."
    },
    "Stop Loss": {
        "category": "Risk Management",
        "definition": "Predetermined price level at which a losing position will be closed to limit losses.",
        "formula": "Entry Price - (Entry Price × Stop Loss %)",
        "interpretation": "Essential risk management tool. Should be set based on volatility.",
        "example": "10% stop loss on $100 entry means exit at $90 if price falls."
    },
    "Risk-Reward Ratio": {
        "category": "Risk Management",
        "definition": "Ratio of potential profit to potential loss on a trade.",
        "formula": "Potential Profit / Potential Loss",
        "interpretation": "Higher is better. Minimum 1:1, ideally 2:1 or 3:1.",
        "example": "3:1 risk-reward means risking $100 to potentially make $300."
    },

    # Technical Indicators
    "ATR (Average True Range)": {
        "category": "Technical Indicators",
        "definition": "Measures market volatility by calculating average range between high and low prices.",
        "formula": "14-period moving average of True Range (max of: High-Low, |High-Close|, |Low-Close|)",
        "interpretation": "Higher values indicate more volatility. Used for stop placement and position sizing.",
        "example": "ATR of $5 suggests daily price swings around $5."
    },
    "RSI (Relative Strength Index)": {
        "category": "Technical Indicators",
        "definition": "Momentum oscillator measuring speed and magnitude of price changes.",
        "formula": "100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss",
        "interpretation": "Range 0-100. > 70 = overbought, < 30 = oversold.",
        "example": "RSI of 75 suggests asset may be overbought and due for pullback."
    },
    "MACD (Moving Average Convergence Divergence)": {
        "category": "Technical Indicators",
        "definition": "Trend-following momentum indicator showing relationship between two moving averages.",
        "formula": "MACD Line = 12-day EMA - 26-day EMA; Signal Line = 9-day EMA of MACD",
        "interpretation": "MACD crossing above signal = bullish; below = bearish.",
        "example": "MACD line crossing above signal line suggests potential buy signal."
    },
    "Bollinger Bands": {
        "category": "Technical Indicators",
        "definition": "Volatility bands placed above and below a moving average.",
        "formula": "Middle Band = 20-day SMA; Upper/Lower = Middle ± (2 × Standard Deviation)",
        "interpretation": "Price touching upper band = potentially overbought; lower = oversold.",
        "example": "Price at upper Bollinger Band may indicate short-term overextension."
    },
    "SMA (Simple Moving Average)": {
        "category": "Technical Indicators",
        "definition": "Average price over a specified number of periods.",
        "formula": "Sum of Closing Prices / Number of Periods",
        "interpretation": "Smooths price data to identify trend. Common periods: 50, 100, 200 days.",
        "example": "50-day SMA above 200-day SMA = bullish 'golden cross' signal."
    },
    "EMA (Exponential Moving Average)": {
        "category": "Technical Indicators",
        "definition": "Weighted moving average that gives more importance to recent prices.",
        "formula": "EMA = (Close - Previous EMA) × Multiplier + Previous EMA",
        "interpretation": "More responsive to recent price changes than SMA.",
        "example": "12-day EMA reacts faster to price changes than 12-day SMA."
    },

    # Trading Concepts
    "Backtesting": {
        "category": "Trading Concepts",
        "definition": "Testing a trading strategy on historical data to evaluate performance.",
        "formula": "N/A",
        "interpretation": "Past performance doesn't guarantee future results. Watch for overfitting.",
        "example": "Testing a moving average crossover strategy on 10 years of S&P 500 data."
    },
    "Overfitting": {
        "category": "Trading Concepts",
        "definition": "Creating a strategy that performs well on historical data but fails in live trading.",
        "formula": "N/A",
        "interpretation": "Occurs when strategy is too complex or optimized for specific dataset.",
        "example": "Strategy with 15 parameters perfectly fit to past data but fails forward."
    },
    "Walk-Forward Analysis": {
        "category": "Trading Concepts",
        "definition": "Optimization technique that tests strategy on out-of-sample data repeatedly.",
        "formula": "N/A",
        "interpretation": "Helps avoid overfitting by validating on unseen data.",
        "example": "Optimize on 2020 data, test on 2021, then optimize on 2021, test on 2022."
    },
    "Slippage": {
        "category": "Trading Concepts",
        "definition": "Difference between expected trade price and actual execution price.",
        "formula": "Actual Execution Price - Expected Price",
        "interpretation": "Reduces actual returns. Higher in illiquid markets or large orders.",
        "example": "Expected to buy at $100, executed at $100.50 = $0.50 slippage."
    },
    "Commission": {
        "category": "Trading Concepts",
        "definition": "Fee charged by broker for executing trades.",
        "formula": "Varies by broker: per trade, per share, or percentage of trade value",
        "interpretation": "Reduces net returns. More impact on frequent trading strategies.",
        "example": "$5 per trade or $0.01 per share."
    },

    # Advanced Concepts
    "Monte Carlo Simulation": {
        "category": "Advanced Concepts",
        "definition": "Statistical technique that randomizes trade sequences to test strategy robustness.",
        "formula": "N/A - uses random sampling of historical trades",
        "interpretation": "Shows range of possible outcomes and worst-case scenarios.",
        "example": "Running 1000 simulations shows 95% confidence interval for returns."
    },
    "Kelly Criterion": {
        "category": "Advanced Concepts",
        "definition": "Mathematical formula for optimal position sizing to maximize long-term growth.",
        "formula": "Kelly % = W - [(1 - W) / R], where W = win rate, R = avg win/avg loss",
        "interpretation": "Full Kelly is aggressive; most traders use fractional Kelly (1/4 or 1/2).",
        "example": "Kelly of 20% suggests allocating 20% of capital to position."
    },
    "Beta": {
        "category": "Advanced Concepts",
        "definition": "Measure of a strategy's volatility relative to overall market.",
        "formula": "Covariance(Strategy, Market) / Variance(Market)",
        "interpretation": "Beta = 1 moves with market; < 1 less volatile; > 1 more volatile.",
        "example": "Beta of 1.5 means strategy moves 1.5x the market's movements."
    },
    "Alpha": {
        "category": "Advanced Concepts",
        "definition": "Excess return of a strategy relative to a benchmark.",
        "formula": "Strategy Return - (Risk-Free Rate + Beta × (Market Return - Risk-Free Rate))",
        "interpretation": "Positive alpha = outperformance; negative = underperformance.",
        "example": "Alpha of 5% means strategy beat benchmark by 5% annually."
    },
    "Value at Risk (VaR)": {
        "category": "Advanced Concepts",
        "definition": "Statistical measure of maximum expected loss over specific time period at given confidence level.",
        "formula": "Various methods: Historical, Parametric, Monte Carlo",
        "interpretation": "1-day 95% VaR of $10,000 means 95% chance loss won't exceed $10,000 in one day.",
        "example": "Daily 99% VaR of $5,000 on $100,000 portfolio."
    },
    "Bootstrapping": {
        "category": "Advanced Concepts",
        "definition": "Resampling technique that randomly samples from historical returns with replacement.",
        "formula": "N/A - statistical resampling method",
        "interpretation": "Creates alternative return scenarios to test strategy robustness.",
        "example": "Generate 1000 simulated equity curves from actual trade returns."
    }
}


def get_glossary_categories() -> List[str]:
    """Get list of all glossary categories."""
    categories = set()
    for term_data in TRADING_GLOSSARY.values():
        categories.add(term_data['category'])
    return sorted(list(categories))


def get_terms_by_category(category: str) -> Dict[str, Dict[str, str]]:
    """Get all terms for a specific category."""
    return {
        term: data for term, data in TRADING_GLOSSARY.items()
        if data['category'] == category
    }


def search_glossary(query: str) -> Dict[str, Dict[str, str]]:
    """Search glossary for terms matching query."""
    query_lower = query.lower()
    results = {}

    for term, data in TRADING_GLOSSARY.items():
        # Search in term name, definition, and category
        if (query_lower in term.lower() or
            query_lower in data['definition'].lower() or
            query_lower in data['category'].lower()):
            results[term] = data

    return results


def display_glossary_streamlit():
    """Display trading glossary in Streamlit app."""
    st.title("Trading Concepts Glossary")

    st.markdown("""
    Welcome to the Trading Concepts Glossary! This comprehensive guide covers essential
    trading terminology, risk management concepts, technical indicators, and advanced topics.
    """)

    # Search functionality
    search_query = st.text_input("Search for a term:", placeholder="e.g., Sharpe, RSI, Risk...")

    if search_query:
        results = search_glossary(search_query)

        if results:
            st.success(f"Found {len(results)} matching term(s)")

            for term, data in results.items():
                with st.expander(f"**{term}** ({data['category']})", expanded=True):
                    st.markdown(f"**Definition:** {data['definition']}")

                    if data['formula'] != "N/A":
                        st.markdown(f"**Formula:** `{data['formula']}`")

                    st.markdown(f"**Interpretation:** {data['interpretation']}")
                    st.markdown(f"**Example:** {data['example']}")
        else:
            st.warning("No terms found. Try a different search term.")
    else:
        # Display by category
        st.markdown("---")
        st.subheader("Browse by Category")

        # Category selection
        categories = get_glossary_categories()
        selected_category = st.selectbox("Select a category:", ["All"] + categories)

        if selected_category == "All":
            # Display all terms
            for category in categories:
                st.markdown(f"### {category}")
                terms = get_terms_by_category(category)

                for term, data in sorted(terms.items()):
                    with st.expander(f"**{term}**"):
                        st.markdown(f"**Definition:** {data['definition']}")

                        if data['formula'] != "N/A":
                            st.markdown(f"**Formula:** `{data['formula']}`")

                        st.markdown(f"**Interpretation:** {data['interpretation']}")
                        st.markdown(f"**Example:** {data['example']}")

                st.markdown("---")
        else:
            # Display selected category
            st.markdown(f"### {selected_category}")
            terms = get_terms_by_category(selected_category)

            for term, data in sorted(terms.items()):
                with st.expander(f"**{term}**", expanded=False):
                    st.markdown(f"**Definition:** {data['definition']}")

                    if data['formula'] != "N/A":
                        st.markdown(f"**Formula:** `{data['formula']}`")

                    st.markdown(f"**Interpretation:** {data['interpretation']}")
                    st.markdown(f"**Example:** {data['example']}")

    # Quick reference
    st.markdown("---")
    st.subheader("Quick Reference")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Top Performance Metrics**")
        st.markdown("- Sharpe Ratio")
        st.markdown("- Sortino Ratio")
        st.markdown("- Calmar Ratio")
        st.markdown("- Maximum Drawdown")

    with col2:
        st.markdown("**Key Risk Metrics**")
        st.markdown("- Portfolio Heat")
        st.markdown("- Position Sizing")
        st.markdown("- Risk-Reward Ratio")
        st.markdown("- Value at Risk (VaR)")

    with col3:
        st.markdown("**Essential Indicators**")
        st.markdown("- ATR (Volatility)")
        st.markdown("- RSI (Momentum)")
        st.markdown("- MACD (Trend)")
        st.markdown("- Bollinger Bands")


def get_term_definition(term: str) -> Optional[Dict[str, str]]:
    """
    Get definition for a specific term.

    Parameters
    ----------
    term : str
        Term to look up

    Returns
    -------
    dict or None
        Term data or None if not found
    """
    return TRADING_GLOSSARY.get(term)


def get_all_terms() -> List[str]:
    """Get list of all terms in glossary."""
    return sorted(list(TRADING_GLOSSARY.keys()))
