import streamlit as st

# Shared helpers — see sections/_common.py.
# Refactored: get_price_history and build_sparkline used to live here,
# but they were identical to the ones in popular_markets.py, so they've
# been moved to a shared module.
from sections._common import get_price_history, build_sparkline

# Mapping personal stock names to Yahoo Finance tickers.
# each entry carries both ticker and currency,
# so the price can be shown as e.g. "563.40 SEK" or "424.17 USD".
MY_STOCKS = {
    "Saab":      {"ticker": "SAAB-B.ST", "currency": "SEK"},
    "Spotify":   {"ticker": "SPOT",      "currency": "USD"},
    "Microsoft": {"ticker": "MSFT",      "currency": "USD"},
}


def render():
    # Header for the personal stocks section.
    st.header("My stocks")

    # Create one column per personal stock
    cols = st.columns(len(MY_STOCKS))

    # Iterate over (column, (name, info)) pairs and render
    # a metric + sparkline in each column.
    # info is a dict with both ticker and currency.
    for col, (name, info) in zip(cols, MY_STOCKS.items()):
        hist, symbol = get_price_history(info["ticker"])
        currency = info["currency"]

        with col:
            if hist is not None:
                # Calculate metric values from the last two closes.
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / (current_price - change)) * 100

                # Display the Metric (price + absolute/percent change)
                # value includes the currency suffix.
                st.metric(
                    label=name,
                    value=f"{current_price:,.2f} {currency}",
                    delta=f"{change:,.2f} ({change_pct:.2f}%)"
                )

                # Plotly area sparkline (shared helper).
                # config={"displayModeBar": False} hides the floating Plotly toolbar.
                st.plotly_chart(
                    build_sparkline(hist),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                # error fallback message
                st.error(f"Unavailable: {name}")

    # Captions explaining the chart window and data source.
    st.caption("Graphs show performance over the last 30 days.")
    # dropped the explicit currency list since it's now shown per stock.
    st.caption("Data: Yahoo Finance.")
