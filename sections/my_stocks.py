"""Personal watchlist section.

Renders the user's saved stocks read from `data/my_stocks.json`.
Add/remove UI is added in a later commit.
"""

import streamlit as st

from sections._common import get_price_history, build_sparkline
from sections._watchlist import load


def render():
    st.header("My stocks")

    my_stocks = load()

    if not my_stocks:
        st.info(
            "Your watchlist is empty. "
            "Search and pin stocks to start tracking them here."
        )
        return

    # One column per stock, side by side.
    cols = st.columns(len(my_stocks))
    for col, (name, info) in zip(cols, my_stocks.items()):
        hist = get_price_history(info["ticker"])
        currency = info["currency"]

        with col:
            if hist is not None:
                # Day-over-day change based on the two most recent closes.
                current_price = hist["Close"].iloc[-1]
                previous_close = hist["Close"].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / previous_close) * 100

                st.metric(
                    label=name,
                    value=f"{current_price:,.2f} {currency}",
                    delta=f"{change:,.2f} ({change_pct:.2f}%)",
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
