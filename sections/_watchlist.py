"""Persisted personal watchlist storage.

Reads and writes the user's My-stocks selection to a JSON file so
customisations survive across sessions.
"""

import json
from pathlib import Path

# Path resolved relative to this file so it works wherever the app is launched.
WATCHLIST_PATH = Path(__file__).parent.parent / "data" / "my_stocks.json"


def load():
    """Return the saved watchlist, or an empty dict if no file exists yet."""
    if not WATCHLIST_PATH.exists():
        return {}
    return json.loads(WATCHLIST_PATH.read_text())


def save(data):
    WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    WATCHLIST_PATH.write_text(json.dumps(data, indent=2))


def add(name, ticker, currency):
    data = load()
    data[name] = {"ticker": ticker, "currency": currency}
    save(data)


def remove(name):
    data = load()
    data.pop(name, None)
    save(data)
