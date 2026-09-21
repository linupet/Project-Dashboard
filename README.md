# Stock Market Dashboard

A small Streamlit app for keeping an eye on the stock market. It shows a few major indices, a set of popular US and Swedish stocks, and a personal watchlist where you can pin the stocks you want to follow. All data comes from Yahoo Finance through the [yfinance](https://github.com/ranaroussi/yfinance) library.

Built by [Linus Pettersson](https://github.com/linupet) and [Somya Tanwar](https://github.com/tanwarsomya) in spring 2026.

## Features

- Overview: indices, popular stocks and your watchlist on one page.
- Popular markets: S&P 500, NASDAQ, Dow Jones and DAX.
- Popular stocks: Apple, Microsoft, Google and Nvidia, plus Investor, Atlas Copco, Volvo and Ericsson from Nasdaq Stockholm.
- My stocks: search by company name or ticker, pin stocks to your watchlist and remove them again. The list is saved to `data/my_stocks.json`, so it's still there the next time you start the app.
- Quick search: look up any stock from the sidebar and see its price without leaving the page you're on.

Each index and stock is shown as a card with the latest price, the change since the previous close and a chart of the last month.

## Getting started

You need Python 3.10 or later.

```bash
git clone https://github.com/linupet/Project-Dashboard.git
cd Project-Dashboard
```

Create and activate a virtual environment.

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install the dependencies and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser at http://localhost:8501.

## How it works

- `app.py` is the entry point. It builds the sidebar and decides which page to show.
- `sections/_common.py` fetches price history and draws the cards and charts that every page uses.
- `sections/_watchlist.py` reads and writes the watchlist file.
- The rest of `sections/` has one file per page, plus the sidebar search.
- `.streamlit/config.toml` sets the dark theme.

Streamlit reruns the whole script every time you click something, so price data is cached for 10 minutes and search results for 5 minutes with `st.cache_data`. Without it, every click would fetch everything from Yahoo again.

If a ticker can't be loaded, its card says "Unavailable" and the error is logged in the terminal instead of breaking the page.

## Limitations

- yfinance is an unofficial library, not an official Yahoo API. Prices can be delayed, and requests sometimes fail or get rate-limited.
- The watchlist is a local file, so it isn't shared between computers or users.

## Built with

Python, Streamlit, Plotly and yfinance.
