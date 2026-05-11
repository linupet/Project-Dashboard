"""Shared helpers used by the dashboard sections.

Provides the cached price-history fetch, the Plotly sparkline builder,
and the metric-card renderer that every section uses to draw a ticker.
"""

import logging

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


# Cache for 10 minutes — Streamlit reruns on every interaction.
@st.cache_data(ttl=600)
def get_price_history(ticker_symbol, period="1mo"):
    """Return the price history DataFrame, or None if unavailable.

    Fewer than 2 rows counts as unavailable since callers compute a
    day-over-day change from the last two closes.
    """
    try:
        hist = yf.Ticker(ticker_symbol).history(period=period)
    except Exception:
        # Log with traceback for the terminal, return None to keep the UI clean.
        logger.exception("Failed to fetch history for %s", ticker_symbol)
        return None

    if hist.empty or len(hist) < 2:
        return None

    return hist


def render_metric_card(col, name, info, on_remove=None):
    """Render one ticker card (metric + sparkline) inside `col`.

    `info` must contain `ticker` and `currency` keys. If `on_remove` is
    provided, a Remove button calls `on_remove(name)` and reruns the app.
    """
    hist = get_price_history(info["ticker"])
    with col:
        if hist is None:
            st.error(f"Unavailable: {name}")
            return

        # Day-over-day change from the two most recent closes.
        current_price = hist["Close"].iloc[-1]
        previous_close = hist["Close"].iloc[-2]
        change = current_price - previous_close
        change_pct = (change / previous_close) * 100

        st.metric(
            label=name,
            value=f"{current_price:,.2f} {info['currency']}",
            delta=f"{change:,.2f} ({change_pct:.2f}%)",
        )

        # Hide Plotly's floating toolbar — it's noise on a sparkline.
        st.plotly_chart(
            build_sparkline(hist),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        if on_remove is not None and st.button(
            "Remove", key=f"rm_{name}", use_container_width=True
        ):
            on_remove(name)
            st.rerun()


def build_sparkline(hist):
    """Minimal Plotly area chart: blue line, gradient fill, no axes."""
    color_line = "#3b82f6"

    # Pad the y-range so the line doesn't touch the chart edges.
    y_min = hist["Close"].min() * 0.98
    y_max = hist["Close"].max() * 1.02

    fig = go.Figure()

    # Invisible baseline at y_min. The price trace fills "tonexty" down
    # to this trace so the gradient spans only the visible y-range
    # instead of stretching from y=0.
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=[y_min] * len(hist),
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
    ))

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
        # <extra></extra> drops the default trace label from the hover box.
        hovertemplate="%{x|%b %d}<br>%{y:,.2f}<extra></extra>",
        showlegend=False,
    ))

    # Edge-to-edge, transparent so the chart blends into the column.
    fig.update_layout(
        height=120,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, range=[y_min, y_max]),
        showlegend=False,
    )
    return fig
