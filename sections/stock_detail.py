"""Per-stock page for watchlist stocks: price chart, key data, Monte Carlo and news."""

import logging
from datetime import datetime, timezone

import streamlit as st
import yfinance as yf

from sections import monte_carlo
from sections._common import build_sparkline, get_price_history
from sections._watchlist import load

logger = logging.getLogger(__name__)

# Label → yfinance period for the price chart.
PERIODS = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "5Y": "5y"}

NEWS_COUNT = 8


def open_stock(name):
    """Switch the app to the detail page for watchlist stock `name`."""
    st.session_state.selected_stock = name
    st.session_state.view = "Stock"


def render():
    name = st.session_state.get("selected_stock")
    info = load().get(name)

    if st.button("← Back to My stocks"):
        st.session_state.view = "My stocks"
        st.rerun()

    # The stock may have been removed from the watchlist since it was opened.
    if info is None:
        st.info("This stock is no longer in your watchlist.")
        return

    ticker = info["ticker"]
    st.header(f"{name} ({ticker})")

    _render_price(name, info)
    st.divider()
    _render_key_data(info)
    st.divider()
    monte_carlo.render_for_stock(name, info)
    st.divider()
    _render_news(ticker)

    st.caption("Data: Yahoo Finance.")


def _render_price(name, info):
    period_label = st.segmented_control(
        "Period", list(PERIODS.keys()), default="1M",
        key=f"detail_period_{info['ticker']}",
    ) or "1M"  # Clicking the selected option again deselects it.

    hist = get_price_history(info["ticker"], period=PERIODS[period_label])
    if hist is None:
        st.error(f"Unavailable: {name}")
        return

    # Day-over-day change, plus the change over the whole chosen period.
    current_price = hist["Close"].iloc[-1]
    previous_close = hist["Close"].iloc[-2]
    change = current_price - previous_close
    change_pct = (change / previous_close) * 100
    period_change_pct = (current_price / hist["Close"].iloc[0] - 1) * 100

    c1, c2 = st.columns(2)
    c1.metric(
        "Price",
        f"{current_price:,.2f} {info['currency']}",
        delta=f"{change:,.2f} ({change_pct:.2f}%)",
    )
    c2.metric(f"Change over {period_label}", f"{period_change_pct:+.2f}%")

    st.plotly_chart(
        build_sparkline(hist, height=280),
        use_container_width=True,
        config={"displayModeBar": False},
        key=f"detail_chart_{info['ticker']}",
    )


# Cached like price data — company info changes slowly.
@st.cache_data(ttl=600)
def get_stock_info(ticker_symbol):
    """Return the yfinance info dict, or {} if unavailable."""
    try:
        return yf.Ticker(ticker_symbol).info or {}
    except Exception:
        logger.exception("Failed to fetch info for %s", ticker_symbol)
        return {}


def _render_key_data(info):
    st.subheader("Key data")

    data = get_stock_info(info["ticker"])
    if not data:
        st.warning("Key data is unavailable right now. Try again in a moment.")
        return

    currency = info["currency"]
    recommendation = data.get("recommendationKey")

    # yfinance already reports dividendYield as a percentage (0.76 = 0.76%).
    fields = [
        ("Market cap", _fmt_big(data.get("marketCap"), currency)),
        ("P/E (trailing)", _fmt_num(data.get("trailingPE"))),
        ("P/E (forward)", _fmt_num(data.get("forwardPE"))),
        ("EPS (trailing)", _fmt_num(data.get("trailingEps"), currency)),
        ("Dividend yield", _fmt_num(data.get("dividendYield"), "%", space=False)),
        ("Beta", _fmt_num(data.get("beta"))),
        ("52-week high", _fmt_num(data.get("fiftyTwoWeekHigh"), currency)),
        ("52-week low", _fmt_num(data.get("fiftyTwoWeekLow"), currency)),
        ("Avg. volume", _fmt_big(data.get("averageVolume"))),
        ("Analyst target", _fmt_num(data.get("targetMeanPrice"), currency)),
        ("Analyst rating", recommendation.replace("_", " ").title() if recommendation else "–"),
        ("Employees", f"{data['fullTimeEmployees']:,}" if data.get("fullTimeEmployees") else "–"),
    ]

    for start in range(0, len(fields), 4):
        cols = st.columns(4)
        for col, (label, value) in zip(cols, fields[start:start + 4]):
            col.metric(label, value)

    profile = " · ".join(
        v for v in (data.get("sector"), data.get("industry"), data.get("country")) if v
    )
    if profile:
        st.caption(profile)

    summary = data.get("longBusinessSummary")
    if summary:
        with st.expander("About the company"):
            st.write(summary)
            if data.get("website"):
                st.markdown(f"[{data['website']}]({data['website']})")


def _fmt_num(value, unit="", space=True):
    if value is None:
        return "–"
    sep = " " if space and unit else ""
    return f"{value:,.2f}{sep}{unit}"


def _fmt_big(value, unit=""):
    """Abbreviate large numbers: 3.81T, 28.77M."""
    if value is None:
        return "–"
    for threshold, suffix in [(1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(value) >= threshold:
            return f"{value / threshold:,.2f}{suffix} {unit}".strip()
    return f"{value:,.0f} {unit}".strip()


# Cached so the news list stays stable across reruns.
@st.cache_data(ttl=600)
def get_news(ticker_symbol):
    """Return up to NEWS_COUNT articles as dicts with title, link,
    publisher, published (datetime or None) and thumbnail (url or None).

    Ticker.get_news often comes back empty, so Yahoo's search endpoint is
    used as a fallback. The two return differently shaped items.
    """
    items = []
    try:
        items = yf.Ticker(ticker_symbol).get_news(count=NEWS_COUNT)
    except Exception:
        logger.exception("Failed to fetch news for %s", ticker_symbol)

    if not items:
        try:
            items = yf.Search(ticker_symbol, max_results=0, news_count=NEWS_COUNT).news
        except Exception:
            logger.exception("Failed to search news for %s", ticker_symbol)
            return []

    articles = [_normalize_article(item) for item in items]
    return [a for a in articles if a["title"] and a["link"]][:NEWS_COUNT]


def _normalize_article(item):
    # Ticker.get_news nests everything under "content".
    if "content" in item:
        c = item["content"]
        published = None
        if c.get("pubDate"):
            try:
                published = datetime.fromisoformat(c["pubDate"].replace("Z", "+00:00"))
            except ValueError:
                pass
        thumb = c.get("thumbnail") or {}
        return {
            "title": c.get("title"),
            "link": (c.get("canonicalUrl") or c.get("clickThroughUrl") or {}).get("url"),
            "publisher": (c.get("provider") or {}).get("displayName"),
            "published": published,
            "thumbnail": _pick_thumbnail(thumb.get("resolutions")),
        }

    # yf.Search news is flat.
    ts = item.get("providerPublishTime")
    return {
        "title": item.get("title"),
        "link": item.get("link"),
        "publisher": item.get("publisher"),
        "published": datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None,
        "thumbnail": _pick_thumbnail((item.get("thumbnail") or {}).get("resolutions")),
    }


def _pick_thumbnail(resolutions):
    """Prefer the small square thumbnail; fall back to whatever exists."""
    if not resolutions:
        return None
    for r in resolutions:
        if r.get("tag") == "140x140":
            return r.get("url")
    return resolutions[-1].get("url")


def _render_news(ticker):
    st.subheader("News")

    articles = get_news(ticker)
    if not articles:
        st.info("No recent news found.")
        return

    for article in articles:
        with st.container(border=True):
            if article["thumbnail"]:
                col_img, col_text = st.columns([1, 6])
                col_img.image(article["thumbnail"], use_container_width=True)
            else:
                col_text = st.container()

            col_text.markdown(f"**[{article['title']}]({article['link']})**")
            meta = " · ".join(
                v for v in (article["publisher"], _time_ago(article["published"])) if v
            )
            if meta:
                col_text.caption(meta)


def _time_ago(published):
    if published is None:
        return None
    seconds = (datetime.now(timezone.utc) - published).total_seconds()
    if seconds < 3600:
        return f"{max(int(seconds // 60), 1)} min ago"
    if seconds < 86400:
        return f"{int(seconds // 3600)} h ago"
    return published.strftime("%b %d, %Y")
