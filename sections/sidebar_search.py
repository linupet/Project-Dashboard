"""Sidebar quick-search for any stock."""

import streamlit as st
import yfinance as yf

from sections._common import get_price_history


# Cached so the dropdown stays stable across reruns — Yahoo can otherwise
# return slightly different result sets and the selectbox loses its pick.
@st.cache_data(ttl=300)
def _search(query):
    return yf.Search(query, max_results=5).quotes


def render():
    """Search box + a compact card showing the picked ticker's price."""
    st.subheader("Quick search")

    query = st.text_input(
        "Search name or ticker",
        placeholder="e.g. Tesla",
        key="sidebar_search_query",
    )

    if not query:
        return

    try:
        results = _search(query)
    except Exception:
        st.error("Search unavailable.")
        return

    # Keep only equities — indexes, ETFs and funds clutter the dropdown
    # and don't all behave well with our card rendering.
    stocks = [r for r in results if r.get("quoteType") == "EQUITY" and "symbol" in r]

    # Label → result map so the selectbox shows readable names but we
    # can still recover the underlying symbol. `or` (not dict-default)
    # handles results where shortname is present but None.
    options = {
        f"{(r.get('shortname') or r['symbol'])} ({r['symbol']})": r
        for r in stocks
    }

    if not options:
        st.caption("No matches.")
        return

    label = st.selectbox(
        "Results",
        list(options.keys()),
        key="sidebar_search_pick",
    )
    selected = options[label]
    ticker = selected["symbol"]
    name = selected.get("shortname") or ticker

    _render_mini_card(ticker, name)


def _render_mini_card(ticker, name):
    """Compact price + day-change card for the sidebar."""
    hist = get_price_history(ticker)
    if hist is None:
        st.error(f"Unavailable: {name}")
        return

    # Day-over-day change from the two most recent closes.
    current_price = hist["Close"].iloc[-1]
    previous_close = hist["Close"].iloc[-2]
    change = current_price - previous_close
    change_pct = (change / previous_close) * 100

    # fast_info occasionally returns no currency — fall back to a blank.
    currency = ""
    try:
        currency = yf.Ticker(ticker).fast_info.get("currency") or ""
    except Exception:
        pass

    st.metric(
        label=name,
        value=f"{current_price:,.2f} {currency}".strip(),
        delta=f"{change:,.2f} ({change_pct:.2f}%)",
    )
