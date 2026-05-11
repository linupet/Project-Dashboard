"""Personal watchlist — pin and remove stocks, persisted to data/my_stocks.json."""

import streamlit as st
import yfinance as yf

from sections._common import render_metric_card
from sections._watchlist import load, add, remove

# Wrap to a new row after this many cards so sparklines stay readable.
CARDS_PER_ROW = 4


def render(editable=True):
    """Render the watchlist.

    When `editable` is False the Search & Pin block and per-card Remove
    buttons are hidden — used on the Overview page so add/remove is only
    available on the dedicated My stocks page.
    """
    st.header("My stocks")

    if editable:
        _render_search_and_pin()
        st.divider()

    my_stocks = load()

    if not my_stocks:
        if editable:
            st.info(
                "Your watchlist is empty. "
                "Search above to pin stocks and start tracking them here."
            )
        else:
            st.info(
                "Your watchlist is empty. "
                "Go to My stocks in the sidebar to add some."
            )
        return

    # Only editable mode wires up Remove — Overview stays read-only.
    items = list(my_stocks.items())
    on_remove = remove if editable else None
    for start in range(0, len(items), CARDS_PER_ROW):
        chunk = items[start:start + CARDS_PER_ROW]
        cols = st.columns(CARDS_PER_ROW)
        for col, (name, info) in zip(cols, chunk):
            render_metric_card(col, name, info, on_remove=on_remove)

    st.caption("Graphs show performance over the last 30 days.")
    st.caption("Data: Yahoo Finance.")


def _render_search_and_pin():
    """Yahoo Finance search box for pinning new stocks to the watchlist."""
    st.subheader("Add a stock")
    search_query = st.text_input(
        "Search name or ticker",
        placeholder="e.g. Tesla",
        key="my_stocks_search",
    )

    if not search_query:
        return

    try:
        search = yf.Search(search_query, max_results=5)
        results = search.quotes
    except Exception:
        st.error("Could not perform search. Try again in a moment.")
        return

    # Label → result map so the selectbox shows readable names but we
    # can still recover the underlying symbol.
    options = {
        f"{r.get('shortname', r['symbol'])} ({r['symbol']})": r
        for r in results
        if "symbol" in r
    }

    if not options:
        st.warning("No matches found.")
        return

    selected_label = st.selectbox("Results", list(options.keys()))
    selected = options[selected_label]
    ticker = selected["symbol"]
    display_name = selected.get("shortname", ticker)

    if st.button("Pin to My stocks", use_container_width=True):
        # fast_info is a cheap call that gives us the trading currency.
        info = yf.Ticker(ticker).fast_info
        currency = info.get("currency", "USD")
        add(display_name, ticker, currency)
        st.success(f"Added {display_name}")
        st.rerun()
