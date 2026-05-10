import streamlit as st
from sections._common import get_price_history, build_sparkline

def render(most_popular, local_stocks):
    # --- Category 1: Most Popular ---
    st.header("Most Popular Stocks")
    render_stock_row(most_popular)

    st.divider()

    # --- Category 2: Local Stocks ---
    st.header("Local Stocks")
    render_stock_row(local_stocks)

    st.divider()

    # --- Category 3: User Pinned Stocks ---
    st.header("My Favorite Stocks")
    pinned = st.session_state.get("my_stocks", {})
    if pinned:
        render_stock_row(pinned, can_unpin=True)
    else:
        st.info("Search and pin stocks in the sidebar to see them here.")

def render_stock_row(stock_map, can_unpin=False):
    cols = st.columns(len(stock_map))
    for col, (name, info) in zip(cols, stock_map.items()):
        hist = get_price_history(info["ticker"])
        with col:
            if hist is not None:
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = curr - prev
                pcnt = (change / prev) * 100
                
                st.metric(label=name, value=f"{curr:,.2f} {info['currency']}", 
                          delta=f"{change:,.2f} ({pcnt:.2f}%)")
                st.plotly_chart(build_sparkline(hist), use_container_width=True, 
                                config={"displayModeBar": False})
                
                if can_unpin:
                    if st.button(f"Unpin {info['ticker']}", key=f"un_{info['ticker']}"):
                        del st.session_state.my_stocks[name]
                        st.rerun()
            else:
                st.error(f"Error: {name}")