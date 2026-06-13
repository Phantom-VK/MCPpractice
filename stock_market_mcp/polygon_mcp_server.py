from mcp.server.fastmcp import FastMCP

from polygon_service import (
    get_all_share_prices_polygon_eod,
    get_daily_open_close,
    get_previous_close_price,
    get_recent_daily_bars,
    get_share_price,
    is_market_open,
)

mcp = FastMCP("polygon_market_server")


@mcp.tool()
async def market_status() -> bool:
    """Return whether the US market is currently open."""
    return is_market_open()


@mcp.tool()
async def lookup_share_price(symbol: str) -> float:
    """Return the latest available stock price for a ticker symbol.

    Args:
        symbol: Stock ticker symbol, for example AAPL or MSFT.
    """
    return get_share_price(symbol)


@mcp.tool()
async def lookup_previous_close(symbol: str) -> float | None:
    """Return the previous market close price for a ticker symbol.

    Args:
        symbol: Stock ticker symbol, for example AAPL or NVDA.
    """
    return get_previous_close_price(symbol)


@mcp.tool()
async def lookup_daily_open_close(symbol: str, date: str) -> dict:
    """Return OHLC and related session data for one ticker on one date.

    Args:
        symbol: Stock ticker symbol.
        date: Trading date in YYYY-MM-DD format.
    """
    return get_daily_open_close(symbol, date)


@mcp.tool()
async def lookup_recent_daily_bars(
    symbol: str,
    from_date: str,
    to_date: str,
    limit: int = 30,
) -> list[dict]:
    """Return recent daily OHLCV bars for a ticker in a date range.

    Args:
        symbol: Stock ticker symbol.
        from_date: Start date in YYYY-MM-DD format.
        to_date: End date in YYYY-MM-DD format.
        limit: Maximum number of bars to return.
    """
    return get_recent_daily_bars(symbol, from_date, to_date, limit)


@mcp.tool()
async def lookup_market_eod_snapshot() -> dict[str, float]:
    """Return grouped end-of-day close prices for the latest completed market day."""
    return get_all_share_prices_polygon_eod()


if __name__ == "__main__":
    mcp.run(transport="stdio")