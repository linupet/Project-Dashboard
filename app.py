import streamlit as st
import yfinance as yf
from sections import news, popular_markets, my_stocks

st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide",
)

# Initialize Session State
if "view" not in st.session_state:
    st.session_state.view = "Overview"

if "my_stocks" not in st.session_state:
    # Initialize with your default list
    st.session_state.my_stocks = {
        "AppLovin":    {"ticker": "APP",    "currency": "USD"},
        "Palantir":    {"ticker": "PLTR",   "currency": "USD"},
        "Nvidia":      {"ticker": "NVDA",   "currency": "USD"},
        "Rheinmetall": {"ticker": "RHM.DE", "currency": "EUR"},
    }

# Style the sidebar
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        gap: 0;
    }
    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

VIEW_NAMES = ["Overview", "News", "Popular markets", "My stocks"]

# Sidebar
with st.sidebar:
    st.title("Stock Dashboard")

    # --- Improved Search Section ---
    st.subheader("Search & Pin")
    search_query = st.text_input("Search Stock (Name or Ticker)", placeholder="e.g. Apple or AAPL")
    
    if search_query:
        # Search for matches using yfinance
        search = yf.Search(search_query, max_results=5)
        results = search.quotes
        
        if results:
            # Create a dictionary of display names to ticker info
            options = {f"{r.get('shortname', 'Unknown')} ({r['symbol']})": r for r in results if 'symbol' in r}
            selected_display = st.selectbox("Select match", options.keys())
            
            if selected_display:
                selected_stock = options[selected_display]
                ticker = selected_stock['symbol']
                name = selected_stock.get('shortname', ticker)
                
                # Display price and Pin button
                try:
                    t = yf.Ticker(ticker)
                    # Note: .info can be slow; price fetching is best-effort here
                    price_info = t.fast_info
                    current_price = price_info.get('last_price', 'N/A')
                    currency = price_info.get('currency', 'USD')
                    
                    st.write(f"**Price:** {current_price:,.2f} {currency}" if isinstance(current_price, (int, float)) else f"**Price:** {current_price}")
                    
                    if st.button("📌 Pin to My Stocks", use_container_width=True):
                        st.session_state.my_stocks[name] = {
                            "ticker": ticker,
                            "currency": currency
                        }
                        st.success(f"Pinned {name}!")
                        st.rerun()
                except Exception:
                    st.error("Select a result to see details.")
        else:
            st.warning("No matches found.")
    
    st.divider()

    # Sidebar Navigation
    with st.container():
        for name in VIEW_NAMES:
            button_type = "primary" if st.session_state.view == name else "secondary"
            if st.button(name, use_container_width=True, type=button_type):
                st.session_state.view = name
                st.rerun()

view = st.session_state.view

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