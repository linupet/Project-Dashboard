import streamlit as st
import yfinance as yf

# Mapping market names to Yahoo Finance tickers.
# each entry carries both ticker and currency,
# so the price can be shown as e.g. "24,586.17 USD" or "3,037.47 SEK".
MARKETS = {
    "NASDAQ":          {"ticker": "^IXIC", "currency": "USD"},
    "SPY (S&P 500)":   {"ticker": "SPY",   "currency": "USD"},
    "Hong Kong (HSI)": {"ticker": "^HSI",  "currency": "HKD"},
    "OMX 30":          {"ticker": "^OMX",  "currency": "SEK"},
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
    
    # info is a dict with both ticker and currency.
    for col, (name, info) in zip(cols, MARKETS.items()):
        hist, symbol = get_market_data(info["ticker"])
        currency = info["currency"]
        
        with col:
            if hist is not None:
                # Calculate metric values
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / (current_price - change)) * 100
                
                # 1. Display the Metric
                # value includes the currency suffix.
                st.metric(
                    label=name,
                    value=f"{current_price:,.2f} {currency}",
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
    # dropped the explicit currency list since it's now shown per market.
    st.caption("Data: Yahoo Finance.")