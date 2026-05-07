import streamlit as st
import yfinance as yf

from sections import news, popular_markets, my_stocks

st.set_page_config(
    page_title = "Stock Dashboard",
    page_icon = "📈",
    layout = "wide",
)

# Sidebar 
with st.sidebar:
    st.title("Stock Dashboard")
    
    ## Add a search bar for tickers
    ## Display info about the seached ticker in the sidebar
    ticker_input = st.text_input("Search Stock Ticker", value="Write your ticker here").upper()
    if ticker_input:
        try:
            ticker_data = yf.Ticker(ticker_input)
            info = ticker_data.info
            st.write(f"**Current Price:** ${info.get('currentPrice', 'N/A')}")
        except Exception:
            st.error("Invalid Ticker")

    view = st.radio(
        "Navigate",
        ["Overview", "News", "Popular markets", "My stocks"],
    )

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