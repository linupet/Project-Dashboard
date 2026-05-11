"""Popular markets section — static list of major index tickers."""

import streamlit as st

from sections._common import render_metric_card

# Each value holds the Yahoo Finance ticker and the index's quote currency.
MARKETS = {
    "S&P 500":   {"ticker": "^GSPC",  "currency": "USD"},
    "NASDAQ":    {"ticker": "^IXIC",  "currency": "USD"},
    "Dow Jones": {"ticker": "^DJI",   "currency": "USD"},
    "DAX":       {"ticker": "^GDAXI", "currency": "EUR"},
}


def render():
    st.header("Popular Markets")

    cols = st.columns(len(MARKETS))
    for col, (name, info) in zip(cols, MARKETS.items()):
        render_metric_card(col, name, info)

    st.caption("Graphs show performance over the last 30 days.")
    st.caption("Data: Yahoo Finance.")
