import streamlit as st

from sections._common import get_price_history, build_sparkline

# Personal stocks to display, each with its Yahoo Finance ticker and
# the currency the price should be shown in.
MY_STOCKS = {
    "Saab":      {"ticker": "SAAB-B.ST", "currency": "SEK"},
    "Spotify":   {"ticker": "SPOT",      "currency": "USD"},
    "Microsoft": {"ticker": "MSFT",      "currency": "USD"},
}


def render():
    st.header("My stocks")

    # One column per stock, side by side.
    cols = st.columns(len(MY_STOCKS))

    for col, (name, info) in zip(cols, MY_STOCKS.items()):
        hist = get_price_history(info["ticker"])
        currency = info["currency"]

        with col:
            if hist is not None:
                # Day-over-day change based on the two most recent closes.
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / (current_price - change)) * 100

                st.metric(
                    label=name,
                    value=f"{current_price:,.2f} {currency}",
                    delta=f"{change:,.2f} ({change_pct:.2f}%)"
                )

                # displayModeBar=False hides Plotly's floating toolbar.
                st.plotly_chart(
                    build_sparkline(hist),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.error(f"Unavailable: {name}")

    st.caption("Graphs show performance over the last 30 days.")
    st.caption("Data: Yahoo Finance.")
