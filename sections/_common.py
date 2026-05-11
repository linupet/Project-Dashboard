"""Shared helpers used by the dashboard sections.

Provides the cached price-history fetch and the Plotly sparkline
builder that both my_stocks and popular_markets render with.
"""

import logging

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

logger = logging.getLogger(__name__)


# Cached for 10 minutes so Streamlit reruns don't refetch on every interaction.
@st.cache_data(ttl=600)
def get_price_history(ticker_symbol, period="1mo"):
    """Returns the price history DataFrame, or None if unavailable.

    A history of fewer than 2 rows is treated as unavailable since the
    callers compute a day-over-day change from the last two closes.
    """
    try:
        hist = yf.Ticker(ticker_symbol).history(period=period)
    except Exception:
        # Log with traceback so failures are visible in the terminal,
        # but keep the UI clean by returning None.
        logger.exception("Failed to fetch history for %s", ticker_symbol)
        return None

    if hist.empty or len(hist) < 2:
        return None

    return hist


def render_metric_card(col, name, info, on_remove=None):
    """Render one ticker card (metric + sparkline) inside `col`.

    `info` must contain `ticker` and `currency` keys. If `on_remove` is
    provided, a Remove button is rendered below the chart that calls
    `on_remove(name)` and reruns the app. This is the single place all
    sections (popular_markets, popular_stocks, my_stocks) use to render
    a card, so any formatting tweak applies everywhere.
    """
    hist = get_price_history(info["ticker"])
    with col:
        if hist is None:
            st.error(f"Unavailable: {name}")
            return

        # Day-over-day change based on the two most recent closes.
        current_price = hist["Close"].iloc[-1]
        previous_close = hist["Close"].iloc[-2]
        change = current_price - previous_close
        change_pct = (change / previous_close) * 100

        st.metric(
            label=name,
            value=f"{current_price:,.2f} {info['currency']}",
            delta=f"{change:,.2f} ({change_pct:.2f}%)",
        )

        # displayModeBar=False hides Plotly's floating toolbar.
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


# Returns a minimal Plotly area chart: blue line with a vertical gradient
# fill that fades to transparent at the bottom, no axes or legend.
def build_sparkline(hist):
    color_line = "#3b82f6"

    # Slightly padded y-range so the line doesn't touch the chart edges.
    y_min = hist["Close"].min() * 0.98
    y_max = hist["Close"].max() * 1.02

    fig = go.Figure()

    # Invisible baseline at y_min. The price trace fills "tonexty" down to
    # this trace, which makes the gradient span the visible chart area
    # instead of stretching from y=0 (far below the padded y-range).
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=[y_min] * len(hist),
        mode="lines",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Price line with a vertical gradient fill down to the baseline above.
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
        # <extra></extra> removes the default trace label from the hover box.
        hovertemplate="%{x|%b %d}<br>%{y:,.2f}<extra></extra>",
        showlegend=False,
    ))

    # Edge-to-edge layout with hidden axes and a transparent background
    # so the chart blends into the surrounding Streamlit column.
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
