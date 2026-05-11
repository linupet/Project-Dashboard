"""Curated stock lists (global + Swedish) shown read-only."""

import streamlit as st

from sections._common import render_metric_card

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
        render_metric_card(col, name, info)
