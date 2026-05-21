#!/usr/bin/env python3
"""Print AAP projects via MCP projects_list."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aap_mcp_client import McpClient, tool_result_json


def main() -> int:
    client = McpClient()
    try:
        client.connect()
        data = tool_result_json(client.call_tool("projects_list", {"page_size": 50}))
        for p in data.get("results", []):
            print(f"  [{p.get('id')}] {p.get('name')}  {p.get('scm_url', '-')}")
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
