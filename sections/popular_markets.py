import streamlit as st

from sections._common import render_metric_card

# Popular markets to display, each with its Yahoo Finance ticker and
# the currency the index is quoted in.
MARKETS = {
    "S&P 500":   {"ticker": "^GSPC",  "currency": "USD"},
    "NASDAQ":    {"ticker": "^IXIC",  "currency": "USD"},
    "Dow Jones": {"ticker": "^DJI",   "currency": "USD"},
    "DAX":       {"ticker": "^GDAXI", "currency": "EUR"},
}


def render():
    st.header("Popular Markets")

    # One column per market, side by side.
    cols = st.columns(len(MARKETS))
    for col, (name, info) in zip(cols, MARKETS.items()):
        render_metric_card(col, name, info)

    st.caption("Graphs show performance over the last 30 days.")
    st.caption("Data: Yahoo Finance.")
