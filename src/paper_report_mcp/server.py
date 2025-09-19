"""
Paper Report MCP Server
===============

This module implements an MCP server for interacting with paper report.
"""
import asyncio
from typing import Dict, Any, List

import mcp.types
from mcp.server import NotificationOptions
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from paper_report_mcp.config import Settings
from paper_report_mcp.logger import logger
from paper_report_mcp.utils import get_exception_error
from paper_report_mcp.tools.search import search_tool, handle_search
from paper_report_mcp.tools.download import download_tool, handle_download
from paper_report_mcp.tools.list_papers import list_tool, handle_list_papers
from paper_report_mcp.tools.read_paper import read_tool, handle_read_paper

settings = Settings()
server = Server(settings.APP_NAME)


@server.list_tools()
async def list_tools() -> List[mcp.types.Tool]:
    """List available paper report tools."""
    return [search_tool, download_tool, list_tool, read_tool]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    """Handle tool calls for paper report functionality."""
    logger.debug(f"Calling tool {name} with arguments {arguments}")
    try:
        if name == "search_papers":
            return await handle_search(arguments)
        elif name == "download_paper":
            return await handle_download(arguments)
        elif name == "list_papers":
            return await handle_list_papers(arguments)
        elif name == "read_paper":
            return await handle_read_paper(arguments)
        else:
            return [mcp.types.TextContent(type="text", text=f"Error: Unknown tool {name}")]
    except Exception as e:
        error_msg = get_exception_error()
        logger.error(f"Calling tool error: {error_msg}")
        return [mcp.types.TextContent(type="text", text=f"Error:\n{error_msg}")]


async def main():
    """Run the server async context."""
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name=settings.APP_NAME,
                server_version=settings.APP_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(resources_changed=True),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
