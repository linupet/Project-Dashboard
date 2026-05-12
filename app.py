"""App entry point: sidebar navigation and view dispatcher."""

import streamlit as st
from sections import popular_markets, popular_stocks, my_stocks, sidebar_search

st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide",
)

with st.sidebar:
    st.title("Stock Dashboard")

    if "view" not in st.session_state:
        st.session_state.view = "Overview"

    with st.container():
        for name in ["Overview", "Popular markets", "Popular stocks", "My stocks"]:
            btn_type = "primary" if st.session_state.view == name else "secondary"
            if st.button(name, use_container_width=True, type=btn_type):
                st.session_state.view = name
                st.rerun()

    st.divider()
    sidebar_search.render()

view = st.session_state.view
st.title("Stock Dashboard")

if view == "Overview":
    popular_markets.render()
    st.divider()
    popular_stocks.render()
    st.divider()
    my_stocks.render(editable=False)
elif view == "Popular markets":
    popular_markets.render()
elif view == "Popular stocks":
    popular_stocks.render()
elif view == "My stocks":
    my_stocks.render()