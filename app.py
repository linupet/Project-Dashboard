import streamlit as st
import yfinance as yf

from sections import news, popular_markets, my_stocks

st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide",
)


def render_overview():
    """The Overview view stacks every section with dividers between them."""
    news.render()
    st.divider()
    popular_markets.render()
    st.divider()
    my_stocks.render()


# Maps the sidebar radio labels to the function that renders that view.
# Adding a new view = add one entry here.
VIEWS = {
    "Overview": render_overview,
    "News": news.render,
    "Popular markets": popular_markets.render,
    "My stocks": my_stocks.render,
}

# Sidebar
with st.sidebar:
    st.title("Stock Dashboard")

    # Search bar for an arbitrary ticker; shows its current price below.
    ticker_input = st.text_input("Search Stock Ticker", value="Write your ticker here").upper()
    if ticker_input:
        try:
            ticker_data = yf.Ticker(ticker_input)
            info = ticker_data.info
            st.write(f"**Current Price:** ${info.get('currentPrice', 'N/A')}")
        except Exception:
            st.error("Invalid Ticker")

    view = st.radio("Navigate", list(VIEWS.keys()))

# Main view
st.title("Stock Dashboard")

# Look up the renderer for the selected view and call it.
VIEWS[view]()