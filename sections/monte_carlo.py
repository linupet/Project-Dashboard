"""Monte Carlo price simulations, run on demand from a stock's detail page.

The future price is simulated with geometric Brownian motion, calibrated
on the stock's daily log returns over the last year. Results are drawn in
the dashboard's chart style: a fan chart continuing the recent price line
and a histogram of the simulated final prices.
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from sections._common import get_price_history

# Trading days shown before the simulated part of the fan chart.
HISTORY_DAYS = 60

# Horizon label → number of trading days.
HORIZONS = {
    "1 month": 21,
    "3 months": 63,
    "6 months": 126,
    "1 year": 252,
}

COLOR_LINE = "#3b82f6"


def render_for_stock(name, info):
    """Controls, Run button and results for one stock."""
    st.subheader("Monte Carlo simulation")

    ticker = info["ticker"]
    col_horizon, col_sims = st.columns(2)
    with col_horizon:
        horizon_label = st.selectbox(
            "Horizon", list(HORIZONS.keys()), index=1,
            key=f"mc_horizon_{ticker}",
        )
    with col_sims:
        n_sims = st.select_slider(
            "Simulations", options=[500, 1000, 5000, 10000], value=1000,
            key=f"mc_sims_{ticker}",
        )

    # The last run's settings live in session state so the results stay on
    # screen when other widgets on the page trigger a rerun.
    run_key = f"mc_run_{ticker}"
    if st.button("Run Monte Carlo", type="primary", key=f"mc_btn_{ticker}"):
        st.session_state[run_key] = (horizon_label, n_sims)

    if run_key not in st.session_state:
        st.caption(
            "Simulates possible price paths based on the last year of daily "
            "returns. Pick a horizon and press Run."
        )
        return

    run_horizon, run_sims = st.session_state[run_key]
    with st.spinner("Running simulations..."):
        result = simulate_paths(ticker, HORIZONS[run_horizon], run_sims)
    if result is None:
        st.error(f"Not enough price history to simulate {name}.")
        return

    hist, paths = result
    _render_results(info, hist, paths, run_horizon, run_sims)


def _render_results(info, hist, paths, horizon_label, n_sims):
    currency = info["currency"]
    current_price = paths[0, 0]
    final_prices = paths[:, -1]
    p5, p50, p95 = np.percentile(final_prices, [5, 50, 95])
    change = p50 - current_price
    change_pct = (change / current_price) * 100
    prob_up = (final_prices > current_price).mean() * 100

    st.caption(f"{n_sims:,} simulations over {horizon_label}.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Median price", f"{p50:,.2f} {currency}",
        delta=f"{change:,.2f} ({change_pct:.2f}%)",
    )
    c2.metric("5th percentile", f"{p5:,.2f} {currency}")
    c3.metric("95th percentile", f"{p95:,.2f} {currency}")
    c4.metric("Chance of gain", f"{prob_up:.0f}%")

    col_fan, col_hist = st.columns(2)
    with col_fan:
        st.markdown("**Simulated price paths**")
        st.plotly_chart(
            build_fan_chart(hist, paths, height=280),
            use_container_width=True,
            config={"displayModeBar": False},
            key=f"mc_fan_{info['ticker']}",
        )
    with col_hist:
        st.markdown("**Final price distribution**")
        st.plotly_chart(
            build_histogram(final_prices, current_price, height=280),
            use_container_width=True,
            config={"displayModeBar": False},
            key=f"mc_hist_{info['ticker']}",
        )

    st.caption(
        "Dark band: 25th–75th percentile. Light band: 5th–95th. Dotted "
        "line: median. The dashed line in the histogram is today's price."
    )
    st.caption(
        "Simulations assume past volatility continues and are not a "
        "forecast or investment advice."
    )


# Cached so reruns don't resimulate; the fixed seed keeps results stable
# across reruns with the same inputs.
@st.cache_data(ttl=600)
def simulate_paths(ticker_symbol, horizon, n_sims, seed=42):
    """Return (history, paths) or None if there isn't enough data.

    `paths` has shape (n_sims, horizon + 1); column 0 is the latest close.
    """
    hist = get_price_history(ticker_symbol, period="1y")
    if hist is None or len(hist) < 30:
        return None

    closes = hist["Close"].to_numpy()
    log_returns = np.diff(np.log(closes))
    mu = log_returns.mean()
    sigma = log_returns.std(ddof=1)

    rng = np.random.default_rng(seed)
    shocks = rng.normal(mu, sigma, size=(n_sims, horizon))
    log_paths = np.cumsum(shocks, axis=1)
    paths = closes[-1] * np.exp(np.hstack([np.zeros((n_sims, 1)), log_paths]))

    return hist, paths


def build_fan_chart(hist, paths, height=160):
    """Recent closes followed by percentile bands of the simulated paths.

    Styled like the sparklines in `_common.build_sparkline`: blue line,
    transparent background, no axes.
    """
    recent = hist["Close"].iloc[-HISTORY_DAYS:]
    x_hist = list(range(-len(recent) + 1, 1))
    x_sim = list(range(paths.shape[1]))

    p5, p25, p50, p75, p95 = np.percentile(paths, [5, 25, 50, 75, 95], axis=0)

    fig = go.Figure()

    # Each band is a lower trace plus an upper trace filling down to it.
    for lower, upper, alpha in [(p5, p95, 0.15), (p25, p75, 0.3)]:
        fig.add_trace(go.Scatter(
            x=x_sim, y=lower, mode="lines", line=dict(width=0),
            hoverinfo="skip", showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=x_sim, y=upper, mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor=f"rgba(59,130,246,{alpha})",
            hoverinfo="skip", showlegend=False,
        ))

    fig.add_trace(go.Scatter(
        x=x_hist,
        y=recent,
        mode="lines",
        line=dict(color=COLOR_LINE, width=2),
        hovertemplate="Day %{x}<br>%{y:,.2f}<extra></extra>",
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=x_sim,
        y=p50,
        mode="lines",
        line=dict(color=COLOR_LINE, width=2, dash="dot"),
        hovertemplate="Day +%{x}<br>Median %{y:,.2f}<extra></extra>",
        showlegend=False,
    ))

    # Pad the y-range so the bands don't touch the chart edges.
    y_min = min(recent.min(), p5.min()) * 0.98
    y_max = max(recent.max(), p95.max()) * 1.02

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, range=[y_min, y_max]),
        showlegend=False,
    )
    return fig


def build_histogram(final_prices, current_price, height=160):
    """Distribution of simulated final prices, with today's price marked."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=final_prices,
        nbinsx=50,
        marker=dict(color="rgba(59,130,246,0.6)", line=dict(width=0)),
        hovertemplate="%{x}<br>%{y} simulations<extra></extra>",
        showlegend=False,
    ))
    fig.add_vline(
        x=current_price, line=dict(color="#e5e7eb", width=1, dash="dash"),
    )

    # Keep the price axis so the distribution can be read; drop the counts.
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        bargap=0.05,
        xaxis=dict(showgrid=False, tickformat=",.0f"),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig
