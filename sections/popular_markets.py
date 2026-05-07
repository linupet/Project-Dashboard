import streamlit as st

# Shared helpers — see sections/_common.py.
# Refactored: get_market_data and build_sparkline used to live here,
# but they were identical to the ones in my_stocks.py, so they've
# been moved to a shared module.
from sections._common import get_price_history, build_sparkline

# Mapping market names to Yahoo Finance tickers.
# each entry carries both ticker and currency,
# so the price can be shown as e.g. "24,586.17 USD" or "3,037.47 SEK".
MARKETS = {
    "NASDAQ":          {"ticker": "^IXIC", "currency": "USD"},
    "SPY (S&P 500)":   {"ticker": "SPY",   "currency": "USD"},
    "Hong Kong (HSI)": {"ticker": "^HSI",  "currency": "HKD"},
    "OMX 30":          {"ticker": "^OMX",  "currency": "SEK"},
}


def render():
    st.header("Popular Markets")

    # Create columns for the layout
    cols = st.columns(len(MARKETS))

    # info is a dict with both ticker and currency.
    for col, (name, info) in zip(cols, MARKETS.items()):
        hist, symbol = get_price_history(info["ticker"])
        currency = info["currency"]

        with col:
            if hist is not None:
                # Calculate metric values
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / (current_price - change)) * 100

                # 1. Display the Metric
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
                st.error(f"Unavailable: {name}")

    st.caption("Graphs show performance over the last 30 days.")
    # dropped the explicit currency list since it's now shown per market.
    st.caption("Data: Yahoo Finance.")
