import streamlit as st
import yfinance as yf
from sections import news, popular_markets, my_stocks

st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide",
)

# Intializing a session state
if "view" not in st.session_state:
    st.session_state.view = "Overview"

if "my_stocks" not in st.session_state:
    # Initialize with your default list
    st.session_state.my_stocks = {
        "AppLovin":    {"ticker": "APP",    "currency": "USD"},
        "Palantir":    {"ticker": "PLTR",   "currency": "USD"},
        "Nvidia":      {"ticker": "NVDA",   "currency": "USD"},
        "Rheinmetall": {"ticker": "RHM.DE", "currency": "EUR"},
    }

# Style the sidebar nav buttons: stack edge-to-edge with no vertical gap
# and square corners so consecutive buttons feel like one connected list.
# We target the inner vertical block (created by st.container() below) so
# the rest of the sidebar keeps its normal spacing.
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        gap: 0;
    }
    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

VIEW_NAMES = ["Overview", "News", "Popular markets", "My stocks"]

# Streamlit reruns the whole script on every interaction, so we keep the
# selected view in session_state so it survives across reruns.
if "view" not in st.session_state:
    st.session_state.view = "Overview"

# Sidebar
with st.sidebar:
    st.title("Stock Dashboard")

    # Search bar for an arbitrary ticker; shows its current price below.
    ticker_input = st.text_input(
        "Search Stock Ticker",
        placeholder="Write your ticker here",
    ).upper()
    if ticker_input:
        try:
            ticker_data = yf.Ticker(ticker_input)
            info = ticker_data.info
            st.write(f"**Current Price:** ${info.get('currentPrice', 'N/A')}")
        except Exception:
            st.error("Invalid Ticker")

    # One full-width button per section, wrapped in a container so the CSS
    # above can remove the gap between them. The currently selected view is
    # rendered as a "primary" button so it stands out.
    with st.container():
        for name in VIEW_NAMES:
            button_type = "primary" if st.session_state.view == name else "secondary"
            if st.button(name, use_container_width=True, type=button_type):
                st.session_state.view = name
                st.rerun()

view = st.session_state.view

# Main view
st.title("Stock Dashboard")

if view == "Overview":
    news.render()
    st.divider()
    popular_markets.render()
    st.divider()
    my_stocks.render()
elif view == "News":
    news.render()
elif view == "Popular markets":
    popular_markets.render()
elif view == "My stocks":
    my_stocks.render()