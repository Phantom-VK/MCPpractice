import asyncio
import sys
from pathlib import Path

from agents.mcp import MCPServerStdio


async def polygon_mcp():
    server_path = Path(__file__).with_name("polygon_mcp_server.py")
    params = {"command": sys.executable, "args": [str(server_path)]}
    async with MCPServerStdio(params=params, client_session_timeout_seconds=60) as server:
        mcp_tools = await server.list_tools()
    for tool in mcp_tools:
        print(tool)


if __name__ == "__main__":
    asyncio.run(polygon_mcp())
