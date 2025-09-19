"""Tool definitions for the arXiv MCP server."""

from paper_report_mcp.tools.search import search_tool, handle_search
from paper_report_mcp.tools.download import download_tool, handle_download
from paper_report_mcp.tools.list_papers import list_tool, handle_list_papers
from paper_report_mcp.tools.read_paper import read_tool, handle_read_paper


__all__ = [
    "search_tool",
    "handle_search",
    "download_tool",
    "handle_download",
    "list_tool",
    "handle_list_papers",
    "read_tool",
    "handle_read_paper"
]
