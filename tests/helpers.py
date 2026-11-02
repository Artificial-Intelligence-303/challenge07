"""Call the server's tools the way an agent's program would."""

import asyncio

from mcp.types import Tool

import server


def tools() -> dict[str, Tool]:
    """Return the tools the server offers, by name."""
    offered = asyncio.run(server.server.list_tools())
    return {tool.name: tool for tool in offered}


def call(tool: str, **arguments: object) -> str:
    """Send one call to the server and return the text it sends back."""
    result = asyncio.run(server.server.call_tool(tool, arguments))
    return "".join(block.text for block in result.content)
