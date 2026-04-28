import streamlit as st
import yfinance as yf

# Mapping market names to Yahoo Finance tickers
MARKETS = {
    "NASDAQ": "^IXIC",
    "SPY (S&P 500)": "SPY",
    "Hong Kong (HSI)": "^HSI",
    "OMX 30": "^OMX"
}

@st.cache_data(ttl=600)
def get_market_data(ticker_symbol):
    """Fetches price history for metrics and charting."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Fetching 1 month of history for the graph
        hist = ticker.history(period="1mo")
        
        if hist.empty or len(hist) < 2:
            return None, None
        
        return hist, ticker_symbol
    except Exception:
        return None, None

def render():
    st.header("Popular Markets")
    
    # Create columns for the layout
    cols = st.columns(len(MARKETS))
    
    for col, (name, ticker_symbol) in zip(cols, MARKETS.items()):
        hist, symbol = get_market_data(ticker_symbol)
        
        with col:
            if hist is not None:
                # Calculate metric values
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / (current_price - change)) * 100
                
                # 1. Display the Metric
                st.metric(
                    label=name,
                    value=f"{current_price:,.2f}",
                    delta=f"{change:,.2f} ({change_pct:.2f}%)"
                )
                
                # 2. Display the Graph (Sparkline style)
                # We only plot the 'Close' price and remove the legend/labels for a cleaner look
                st.line_chart(
                    hist['Close'], 
                    height=100, 
                    use_container_width=True
                )
            else:
                st.error(f"Unavailable: {name}")

    st.caption("Graphs show performance over the last 30 days.")
    st.caption("Data: Yahoo Finance. Currencies: USD (NASDAQ/SPY), HKD (HSI), SEK (OMX 30).")