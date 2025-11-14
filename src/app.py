"""StrategyBuilder Pro - Streamlit GUI Application"""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from ui.styles import DARK_MODE_CSS
from ui.backtest_tab import run_backtest_tab
from ui.grid_search_tab import run_grid_search_tab
from ui.live_trading_tab import run_live_trading_tab
from utils.database import TradingDatabase

st.set_page_config(
    page_title="StrategyBuilder Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(DARK_MODE_CSS, unsafe_allow_html=True)


@st.cache_resource
def init_database():
    """Initialize trading database"""
    return TradingDatabase()


if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = {}
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None
if 'current_strategy' not in st.session_state:
    st.session_state.current_strategy = None
if 'current_parameters' not in st.session_state:
    st.session_state.current_parameters = None
if 'grid_search_results' not in st.session_state:
    st.session_state.grid_search_results = []
if 'selected_grid_result' not in st.session_state:
    st.session_state.selected_grid_result = 0


def main():
    """Main application"""
    db = init_database()

    st.markdown('<h1 class="main-header">StrategyBuilder Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Professional Algorithmic Trading Platform</p>', unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["Backtest", "Grid Search", "Live Trading"])

    with tab1:
        run_backtest_tab(db)

    with tab2:
        run_grid_search_tab(db)

    with tab3:
        run_live_trading_tab(db)


if __name__ == "__main__":
    main()
