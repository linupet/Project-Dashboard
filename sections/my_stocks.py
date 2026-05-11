"""Personal watchlist section.

Renders the user's saved stocks, persisted to `data/my_stocks.json`,
and lets the user search Yahoo Finance to pin new tickers or remove
existing ones.
"""

import streamlit as st
import yfinance as yf

from sections._common import render_metric_card
from sections._watchlist import load, add, remove

# Cap how many cards share a row so sparklines stay readable as the
# watchlist grows. Extra stocks wrap onto the next row in groups of this size.
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

    # Lay out cards in rows of CARDS_PER_ROW so the grid wraps instead of
    # shrinking each card when the watchlist grows past one row.
    # `on_remove` is only wired up in editable mode so Overview stays read-only.
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
    """Yahoo Finance search box that lets the user pin a stock to the watchlist."""
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

    # Build a label → result map so the selectbox shows readable names
    # but we can still look up the underlying symbol.
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
