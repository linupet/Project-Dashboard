"""Curated stock categories shown read-only.

Holds two static lists — the most-followed global stocks and a set of
local Swedish picks — and renders them as side-by-side cards.
"""

import streamlit as st

from sections._common import get_price_history, build_sparkline

MOST_POPULAR = {
    "Apple":     {"ticker": "AAPL",  "currency": "USD"},
    "Microsoft": {"ticker": "MSFT",  "currency": "USD"},
    "Google":    {"ticker": "GOOGL", "currency": "USD"},
    "Nvidia":    {"ticker": "NVDA",  "currency": "USD"},
}

LOCAL_STOCKS = {
    "Investor AB": {"ticker": "INVE-B.ST", "currency": "SEK"},
    "Atlas Copco": {"ticker": "ATCO-B.ST", "currency": "SEK"},
    "Volvo B":     {"ticker": "VOLV-B.ST", "currency": "SEK"},
    "Ericsson B":  {"ticker": "ERIC-B.ST", "currency": "SEK"},
}


def render():
    st.header("Global Popular Stocks")
    _render_row(MOST_POPULAR)

    st.divider()

    st.header("Local Popular Stocks")
    _render_row(LOCAL_STOCKS)

    st.caption("Graphs show performance over the last 30 days.")
    st.caption("Data: Yahoo Finance.")


def _render_row(stock_map):
    cols = st.columns(len(stock_map))
    for col, (name, info) in zip(cols, stock_map.items()):
        hist = get_price_history(info["ticker"])
        with col:
            if hist is not None:
                # Day-over-day change based on the two most recent closes.
                current_price = hist["Close"].iloc[-1]
                previous_close = hist["Close"].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / previous_close) * 100

                st.metric(
                    label=name,
                    value=f"{current_price:,.2f} {info['currency']}",
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
