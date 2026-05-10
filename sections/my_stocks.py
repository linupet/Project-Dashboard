import streamlit as st
from sections._common import get_price_history, build_sparkline

def render():
    st.header("My stocks")

    # Get stocks from session state
    stocks_to_show = st.session_state.get("my_stocks", {})

    if not stocks_to_show:
        st.info("Your watchlist is empty. Search and pin stocks from the sidebar!")
        return

    # Create columns dynamically based on the number of pinned stocks
    stock_items = list(stocks_to_show.items())
    cols = st.columns(len(stock_items))

    for col, (name, info) in zip(cols, stock_items):
        hist = get_price_history(info["ticker"])
        currency = info["currency"]

        with col:
            if hist is not None:
                # Day-over-day change logic
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
                change = current_price - previous_close
                change_pct = (change / previous_close) * 100

                st.metric(
                    label=name,
                    value=f"{current_price:,.2f} {currency}",
                    delta=f"{change:,.2f} ({change_pct:.2f}%)"
                )

                # Render sparkline using shared helper
                st.plotly_chart(
                    build_sparkline(hist),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
                
                # Unpin button - 'size' removed for maximum compatibility
                if st.button(f"Unpin {info['ticker']}", key=f"unpin_{info['ticker']}"):
                    del st.session_state.my_stocks[name]
                    st.rerun()
            else:
                st.error(f"Unavailable: {name}")

    st.caption("Graphs show performance over the last 30 days.")
    st.caption("Data: Yahoo Finance.")