import streamlit as st
import yfinance as yf

# Mapping personal stock names to Yahoo Finance tickers.

MY_STOCKS = {
    "Saab": "SAAB-B.ST",
    "Spotify": "SPOT",
    "Microsoft": "MSFT",
}

# Cached fetch of price history for each personal stock.
# Mirrors get_market_data() in popular_markets.py — same TTL (10 min)
@st.cache_data(ttl=600)
def get_stock_data(ticker_symbol):
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
    # Header for the personal stocks section.
    st.header("My stocks")

    # Create one column per personal stock 
    cols = st.columns(len(MY_STOCKS))

    # Iterate over (column, (name, ticker)) pairs and render
    # a metric + sparkline in each column.
    for col, (name, ticker_symbol) in zip(cols, MY_STOCKS.items()):
        hist, symbol = get_stock_data(ticker_symbol)

        with col:
            if hist is not None:
                # Calculate metric values from the last two closes.
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / (current_price - change)) * 100

                # Display the Metric (price + absolute/percent change)
                st.metric(
                    label=name,
                    value=f"{current_price:,.2f}",
                    delta=f"{change:,.2f} ({change_pct:.2f}%)"
                )

                # Display the Graph (Sparkline style)
                # Only the 'Close' price is plotted, no legend/labels for a clean look.
                st.line_chart(
                    hist['Close'],
                    height=100,
                    use_container_width=True
                )
            else:
                # error fallback message 
                st.error(f"Unavailable: {name}")

    # Captions explaining the chart window and data source/currencies.
    st.caption("Graphs show performance over the last 30 days.")
    st.caption("Data: Yahoo Finance. Currencies: SEK (Saab), USD (Spotify, Microsoft).")
