"""Shared helpers for the dashboard sections.

Both my_stocks.py and popular_markets.py used to define their own
near-identical fetch function and sparkline builder. They now import
from this module instead, so the logic only lives in one place.
"""

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go


# Cached fetch of price history for a single ticker.
# 10 minute TTL so we avoid hammering Yahoo on every rerun.
@st.cache_data(ttl=600)
def get_price_history(ticker_symbol):
    """Fetches 1 month of price history for metrics and charting."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1mo")

        if hist.empty or len(hist) < 2:
            return None, None

        return hist, ticker_symbol
    except Exception:
        return None, None


# Builds a clean Plotly area-chart sparkline.
# Uses a single blue color regardless of direction, with a vertical
# gradient fill that fades downward to transparent.
def build_sparkline(hist):
    # Fixed blue color for the line itself.
    color_line = "#3b82f6"

    # Tight y-axis range so the line fills the visible plot area.
    y_min = hist["Close"].min() * 0.98
    y_max = hist["Close"].max() * 1.02

    fig = go.Figure()

    # Invisible baseline trace at the bottom of the visible chart.
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
