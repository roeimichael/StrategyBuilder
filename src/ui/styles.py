"""Dark mode FinTech professional CSS styles for StrategyBuilder Pro"""

DARK_MODE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Dark Mode Foundation */
    .main {
        background-color: #101420;
        color: #e2e8f0;
        padding: 2rem;
    }

    [data-testid="stSidebar"] {
        background-color: #1A202C;
        padding: 1.5rem 1rem;
        border-right: 1px solid #2D3748;
    }

    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Typography - Financial Data */
    .financial-data {
        font-family: 'Roboto Mono', monospace !important;
        font-weight: 600;
    }

    /* Header Transformation */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
    }

    .sub-header {
        text-align: center;
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
        margin-bottom: 2rem;
    }

    /* Tab Navigation - Minimalist */
    .stTabs [data-baseweb="tab-list"] {
        gap: 32px;
        background-color: transparent;
        border-bottom: 1px solid #2D3748;
        padding: 0 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 0;
        color: #94a3b8;
        font-weight: 500;
        padding: 0 8px;
        border-bottom: 2px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #3b82f6 !important;
        border-bottom: 2px solid #3b82f6;
    }

    /* Primary Buttons - Flat Blue Accent */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        font-weight: 600;
        padding: 0.875rem 1.5rem;
        border-radius: 10px;
        border: none;
        box-shadow: none;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.875rem;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #2563eb;
        transform: translateY(-1px);
    }

    /* Secondary Buttons */
    .stButton > button {
        background-color: #1e293b;
        color: #e2e8f0;
        font-weight: 500;
        padding: 0.625rem 1rem;
        border-radius: 8px;
        border: 1px solid #334155;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #334155;
        border-color: #475569;
    }

    /* Metric Cards - Floating Effect */
    [data-testid="stMetricValue"] {
        font-family: 'Roboto Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        font-weight: 300;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    [data-testid="metric-container"] {
        background-color: #1e293b;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
        border: 1px solid #334155;
    }

    /* Positive/Negative Deltas - High Contrast */
    [data-testid="stMetricDelta"] svg[fill*="green"],
    [data-testid="stMetricDelta"] svg[fill*="#09ab3b"] {
        fill: #10b981 !important;
    }

    [data-testid="stMetricDelta"] svg[fill*="red"],
    [data-testid="stMetricDelta"] svg[fill*="#ff2b2b"] {
        fill: #ef4444 !important;
    }

    [data-testid="stMetricDelta"] {
        background-color: transparent;
        font-family: 'Roboto Mono', monospace;
        font-weight: 600;
    }

    /* Input Fields - Professional */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        font-family: 'Roboto Mono', monospace !important;
        font-weight: 400 !important;
        padding: 0.625rem !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6 !important;
    }

    /* Progress Bar */
    .stProgress > div > div > div {
        background-color: #3b82f6;
    }

    .stProgress > div > div {
        background-color: #1e293b;
    }

    /* Headers */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #f1f5f9;
    }

    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background-color: #2D3748;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    [data-testid="stExpander"] summary {
        color: #e2e8f0;
        font-weight: 500;
    }

    /* Data Tables */
    .stDataFrame {
        background-color: #1e293b;
    }

    .stDataFrame table {
        color: #e2e8f0;
    }

    .stDataFrame thead tr th {
        background-color: #0f172a !important;
        color: #94a3b8 !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #334155;
    }

    .stDataFrame tbody tr {
        border-bottom: 1px solid #334155;
    }

    .stDataFrame tbody tr:nth-child(even) {
        background-color: #1A202C;
    }

    .stDataFrame tbody tr:nth-child(odd) {
        background-color: #1e293b;
    }

    /* Right-align financial columns */
    .stDataFrame td:has(.financial-data),
    .stDataFrame th:has(.financial-data) {
        text-align: right;
    }

    /* Sidebar Headers */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f1f5f9;
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    /* Info/Warning/Error Boxes */
    .stAlert {
        background-color: #1e293b;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        color: #e2e8f0;
    }

    [data-baseweb="notification"] {
        background-color: #1e293b;
        border: 1px solid #334155;
    }

    /* Multiselect */
    .stMultiSelect > div > div {
        background-color: #0f172a;
        border: 1px solid #334155;
    }

    /* Radio Buttons */
    .stRadio > div {
        background-color: transparent;
    }

    .stRadio label {
        color: #e2e8f0;
    }

    /* Checkbox */
    .stCheckbox label {
        color: #e2e8f0;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }

    /* Download Button */
    .stDownloadButton > button {
        background-color: #1e293b;
        color: #3b82f6;
        border: 1px solid #3b82f6;
        font-weight: 500;
    }

    .stDownloadButton > button:hover {
        background-color: #3b82f6;
        color: white;
    }

    /* Spacing - 8-point grid */
    .block-container {
        padding: 2rem 3rem;
    }

    /* Card styling for metric containers */
    div[data-testid="column"] > div {
        padding: 0.5rem;
    }
</style>
"""
