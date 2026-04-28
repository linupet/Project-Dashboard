import streamlit as st

from sections import news, popular_markets, my_stocks

st.set_page_config(
    page_title = "Stock Dashboard",
    page_icon = "📈",
    layout = "wide",
)

# Sidebar 
with st.sidebar:
    st.title("Stock Dashboard")
    view = st.radio(
        "Navigate",
        ["Overview", "News", "Popular markets", "My stocks"],
    )

# Main view
st.title("Stock Dashboard")

if view == "Overview":
    news.render()
    st.divider()
    popular_markets.render()
    st.divider()
    my_stocks.render()
elif view == "News":
    news.render()
elif view == "Popular markets":
    popular_markets.render()
elif view == "My stocks":
    my_stocks.render()