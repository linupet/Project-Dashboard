import streamlit as st
import yfinance as yf

# Mapping market names to Yahoo Finance tickers
MARKETS = {
    "NASDAQ": "^IXIC",
    "SPY (S&P 500)": "SPY",
    "Hong Kong (HSI)": "^HSI",
    "OMX 30": "^OMX"
}

@st.cache_data(ttl=600)  # Cache data for 10 minutes to improve performance
def get_market_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Fetching the last 2 days of data to calculate change
        hist = ticker.history(period="2d")
        if len(hist) < 2:
            return None, None
        
        current_price = hist['Close'].iloc[-1]
        previous_close = hist['Close'].iloc[-2]
        change = current_price - previous_close
        return current_price, change
    except Exception as e:
        return None, None

def render():
    st.header("Popular Markets")
    
    # Create four columns for the cards
    cols = st.columns(len(MARKETS))
    
    for col, (name, ticker) in zip(cols, MARKETS.items()):
        price, change = get_market_data(ticker)
        
        with col:
            if price is not None:
                # Format change as a percentage for better context
                change_pct = (change / (price - change)) * 100
                st.metric(
                    label=name,
                    value=f"{price:,.2f}",
                    delta=f"{change:,.2f} ({change_pct:.2f}%)"
                )
            else:
                st.error(f"Error loading {name}")

    st.caption("Data provided by Yahoo Finance. Prices are delayed.")