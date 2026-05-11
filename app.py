import streamlit as st
import yfinance as yf
from sections import news, popular_markets, my_stocks

st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide",
)

# Initialize Session State for custom pinned stocks
if "my_stocks" not in st.session_state:
    st.session_state.my_stocks = {}

# Define Static Categories
MOST_POPULAR = {
    "Apple": {"ticker": "AAPL", "currency": "USD"},
    "Microsoft": {"ticker": "MSFT", "currency": "USD"},
    "Google": {"ticker": "GOOGL", "currency": "USD"},
    "Nvidia": {"ticker": "NVDA", "currency": "USD"},
}

LOCAL_STOCKS = {
    "Investor AB": {"ticker": "INVE-B.ST", "currency": "SEK"},
    "Atlas Copco": {"ticker": "ATCO-B.ST", "currency": "SEK"},
    "Volvo B": {"ticker": "VOLV-B.ST", "currency": "SEK"},
    "Ericsson B": {"ticker": "ERIC-B.ST", "currency": "SEK"},
}

# Sidebar Logic
with st.sidebar:
    st.title("Stock Dashboard")
    
    # Navigation
    if "view" not in st.session_state:
        st.session_state.view = "Overview"
    
    with st.container():
        for name in ["Overview", "News", "Popular markets", "My stocks"]:
            btn_type = "primary" if st.session_state.view == name else "secondary"
            if st.button(name, use_container_width=True, type=btn_type):
                st.session_state.view = name
                st.rerun()

    st.divider()
    
    # Search & Pin Logic (Pins to My Stocks but doesn't show list here)
    st.subheader("Search & Pin")
    search_query = st.text_input("Search Name or Ticker", placeholder="e.g. Tesla")
    
    if search_query:
        search = yf.Search(search_query, max_results=3)
        if search.quotes:
            options = {f"{r.get('shortname', r['symbol'])}": r for r in search.quotes if 'symbol' in r}
            selected_name = st.selectbox("Results", options.keys())
            
            if selected_name:
                ticker = options[selected_name]['symbol']
                if st.button("📌 Pin to My Stocks", use_container_width=True):
                    # Fetching currency dynamically
                    info = yf.Ticker(ticker).fast_info
                    st.session_state.my_stocks[selected_name] = {
                        "ticker": ticker, 
                        "currency": info.get('currency', 'USD')
                    }
                    st.success(f"Added {selected_name}")

# Main View Dispatcher
view = st.session_state.view
st.title("Stock Dashboard")

if view == "Overview":
    news.render()
    st.divider()
    popular_markets.render()
    st.divider()
    # Pass the static categories to the renderer
    my_stocks.render(MOST_POPULAR, LOCAL_STOCKS)
elif view == "News":
    news.render()
elif view == "Popular markets":
    popular_markets.render()
elif view == "My stocks":
    my_stocks.render(MOST_POPULAR, LOCAL_STOCKS)