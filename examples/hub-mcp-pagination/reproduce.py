"""Offline end-to-end reproducer: python reproduce-hub-mcp-pagination.py."""

import asyncio
import sys

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from huggingface_hub import MCPClient


async def main():
    if sys.argv[-1] == "server":
        server = Server("paginated-tools")

        async def list_tools(request: types.ListToolsRequest) -> types.ServerResult:
            cursor = request.params.cursor if request.params else None
            name = "search_docs" if cursor is None else "fetch_doc"
            return types.ServerResult(
                types.ListToolsResult(
                    tools=[types.Tool(name=name, inputSchema={"type": "object"})],
                    nextCursor="second-page" if cursor is None else None,
                )
            )

        server.request_handlers[types.ListToolsRequest] = list_tools

        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
        return

    async with MCPClient(model="unused-offline-model") as client:
        await client.add_mcp_server("stdio", command=sys.executable, args=[__file__, "server"])
        names = [tool.function.name for tool in client.available_tools]
        print(f"tools={names}")
        assert names == ["search_docs", "fetch_doc"]


if __name__ == "__main__":
    asyncio.run(main())
