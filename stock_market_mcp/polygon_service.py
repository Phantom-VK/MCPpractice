import os
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from massive import RESTClient

load_dotenv(override=True)

polygon_api_key = os.getenv("POLYGON_API_KEY")
polygon_plan = (os.getenv("POLYGON_PLAN") or "").strip().lower()

is_paid_polygon = polygon_plan == "paid"
is_realtime_polygon = polygon_plan == "realtime"


def _get_client() -> RESTClient:
    if not polygon_api_key:
        raise ValueError("POLYGON_API_KEY is not set")
    return RESTClient(api_key=polygon_api_key)


def _normalize_symbol(symbol: str) -> str:
    if not symbol or not symbol.strip():
        raise ValueError("symbol is required")
    return symbol.strip().upper()


def _safe_getattr(obj: Any, *path: str) -> Any:
    cur = obj
    for part in path:
        if cur is None:
            return None
        cur = getattr(cur, part, None)
    return cur


def is_market_open() -> bool:
    client = _get_client()
    market_status = client.get_market_status()
    return getattr(market_status, "market", "").lower() == "open"


def get_all_share_prices_polygon_eod() -> dict[str, float]:
    """
    Returns latest available grouped daily close prices for the market.
    Uses SPY previous close timestamp to infer the latest completed market day.
    """
    client = _get_client()

    prev = client.get_previous_close_agg("SPY")
    prev_bar = prev[0] if isinstance(prev, list) else prev

    ts = getattr(prev_bar, "timestamp", None)
    if ts is None:
        raise ValueError("Could not determine previous close timestamp from SPY")

    market_date = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).date()
    results = client.get_grouped_daily_aggs(market_date, adjusted=True, include_otc=False)

    prices: dict[str, float] = {}
    for row in results:
        ticker = getattr(row, "ticker", None)
        close = getattr(row, "close", None)
        if ticker and close is not None:
            prices[ticker] = float(close)
    return prices


def get_previous_close_price(symbol: str) -> float | None:
    client = _get_client()
    symbol = _normalize_symbol(symbol)

    result = client.get_previous_close_agg(symbol)
    bar = result[0] if isinstance(result, list) else result
    close = getattr(bar, "close", None)
    return float(close) if close is not None else None


def get_daily_open_close(symbol: str, date_str: str) -> dict[str, float | str | None]:
    """
    date_str format: YYYY-MM-DD
    """
    client = _get_client()
    symbol = _normalize_symbol(symbol)

    result = client.get_daily_open_close_agg(symbol, date_str)

    return {
        "symbol": symbol,
        "date": date_str,
        "open": getattr(result, "open", None),
        "high": getattr(result, "high", None),
        "low": getattr(result, "low", None),
        "close": getattr(result, "close", None),
        "volume": getattr(result, "volume", None),
        "after_hours": getattr(result, "after_hours", None),
        "pre_market": getattr(result, "pre_market", None),
    }


def get_recent_daily_bars(symbol: str, from_date: str, to_date: str, limit: int = 30) -> list[dict]:
    """
    Returns recent daily OHLCV bars.
    date format: YYYY-MM-DD
    """
    client = _get_client()
    symbol = _normalize_symbol(symbol)

    bars = client.list_aggs(
        ticker=symbol,
        multiplier=1,
        timespan="day",
        from_=from_date,
        to=to_date,
        adjusted=True,
        limit=limit,
    )

    output = []
    for bar in bars:
        output.append(
            {
                "timestamp": getattr(bar, "timestamp", None),
                "open": getattr(bar, "open", None),
                "high": getattr(bar, "high", None),
                "low": getattr(bar, "low", None),
                "close": getattr(bar, "close", None),
                "volume": getattr(bar, "volume", None),
            }
        )
    return output


def get_share_price_polygon(symbol: str) -> float | None:
    """
    Best-effort latest stock price from snapshot data.
    Falls back through minute/day/prev_day style fields because snapshot payloads
    can vary by endpoint/client version.
    """
    client = _get_client()
    symbol = _normalize_symbol(symbol)

    snapshot = client.get_snapshot_ticker("stocks", symbol)

    candidates = [
        _safe_getattr(snapshot, "min", "close"),
        _safe_getattr(snapshot, "day", "close"),
        _safe_getattr(snapshot, "prev_day", "close"),
        _safe_getattr(snapshot, "prevDay", "close"),
    ]

    for value in candidates:
        if value is not None:
            return float(value)

    return None


def get_share_price(symbol: str) -> float:
    price = get_share_price_polygon(symbol)
    if price is None:
        raise ValueError(f"No price available for symbol={symbol}")
    return price