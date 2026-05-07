import streamlit as st
import yfinance as yf
# Added: Plotly is used to render filled, colored sparklines
# without visible axes — replaces the default st.line_chart look.
import plotly.graph_objects as go

# Mapping market names to Yahoo Finance tickers.
# each entry carries both ticker and currency,
# so the price can be shown as e.g. "24,586.17 USD" or "3,037.47 SEK".
MARKETS = {
    "NASDAQ":          {"ticker": "^IXIC", "currency": "USD"},
    "SPY (S&P 500)":   {"ticker": "SPY",   "currency": "USD"},
    "Hong Kong (HSI)": {"ticker": "^HSI",  "currency": "HKD"},
    "OMX 30":          {"ticker": "^OMX",  "currency": "SEK"},
}

@st.cache_data(ttl=600)
def get_market_data(ticker_symbol):
    """Fetches price history for metrics and charting."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Fetching 1 month of history for the graph
        hist = ticker.history(period="1mo")

        if hist.empty or len(hist) < 2:
            return None, None

        return hist, ticker_symbol
    except Exception:
        return None, None


# Added: Helper that builds a clean Plotly area-chart sparkline.
# Uses a single blue color for all markets regardless of direction,
# with a vertical gradient fill that fades downward to transparent.
def build_sparkline(hist):
    # Fixed blue color for the line itself.
    color_line = "#3b82f6"

    # Tight y-axis range so the line fills the visible plot area.
    y_min = hist["Close"].min() * 0.98
    y_max = hist["Close"].max() * 1.02

    fig = go.Figure()

    # Added: Invisible baseline trace at the bottom of the visible chart.
    # The price trace fills "tonexty" down to this baseline, which makes
    # the gradient span the whole visible area instead of from y=0 (which
    # is far below the visible window with our tight y-range).
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=[y_min] * len(hist),
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Price line — fills DOWN to the baseline trace above with a vertical
    # gradient: 40% opacity blue at the top, fully transparent at the bottom.
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["Close"],
        mode="lines",
        line=dict(color=color_line, width=2),
        fill="tonexty",
        fillgradient=dict(
            type="vertical",
            colorscale=[
                [0.0, "rgba(59,130,246,0)"],     # bottom: transparent
                [1.0, "rgba(59,130,246,0.4)"],   # top: 40% opacity blue
            ],
        ),
        # Hover shows date + price; <extra></extra> hides the trace name box.
        hovertemplate="%{x|%b %d}<br>%{y:,.2f}<extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        height=120,
        # Zero margins so the sparkline fills the column edge to edge.
        margin=dict(l=0, r=0, t=0, b=0),
        # Transparent backgrounds so the Streamlit dark theme shows through.
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, range=[y_min, y_max]),
        showlegend=False,
    )
    return fig


def render():
    st.header("Popular Markets")
    
    # Create columns for the layout
    cols = st.columns(len(MARKETS))
    
    # info is a dict with both ticker and currency.
    for col, (name, info) in zip(cols, MARKETS.items()):
        hist, symbol = get_market_data(info["ticker"])
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
                
                # Changed: replaced st.line_chart with a Plotly area sparkline.
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