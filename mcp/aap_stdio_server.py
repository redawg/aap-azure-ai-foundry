#!/usr/bin/env python3
"""Minimal MCP stdio server — AAP Controller API tools (no native /mcp required)."""
from __future__ import annotations

import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

AAP_BASE = os.environ.get("AAP_BASE", "https://172.16.1.23").rstrip("/")
AAP_USER = os.environ.get("AAP_USER", "admin")
AAP_PASSWORD = os.environ.get("AAP_PASSWORD", "")


def api_get(path: str, query: dict | None = None) -> dict:
    if not AAP_PASSWORD:
        raise RuntimeError("Set AAP_PASSWORD")
    q = f"?{urllib.parse.urlencode(query)}" if query else ""
    url = f"{AAP_BASE}{path}{q}"
    auth = base64.b64encode(f"{AAP_USER}:{AAP_PASSWORD}".encode()).decode()
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "Authorization": f"Basic {auth}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"HTTP {e.code} {url}: {body[:400]}") from e


TOOLS = [
    {
        "name": "aap_list_recent_jobs",
        "description": "List the most recently finished jobs on AAP (unified_jobs, sorted by -finished).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of jobs to return (default 10)",
                    "default": 10,
                }
            },
        },
    },
    {
        "name": "aap_list_job_templates",
        "description": "List job templates from AAP Controller.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
            },
        },
    },
    {
        "name": "aap_get_job",
        "description": "Get one job by ID (playbook job or system/management job).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {"type": "integer"},
                "job_type": {
                    "type": "string",
                    "description": "job | system_job | unified (auto-detect if unified)",
                    "enum": ["job", "system_job", "unified"],
                },
            },
            "required": ["job_id"],
        },
    },
]


def tool_result_text(data: object) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(data, indent=2)}],
    }


def call_tool(name: str, arguments: dict) -> dict:
    if name == "aap_list_recent_jobs":
        limit = int(arguments.get("limit", 10))
        data = api_get(
            "/api/controller/v2/unified_jobs/",
            {"order_by": "-finished", "page_size": limit},
        )
        rows = [
            {
                "id": j.get("id"),
                "name": j.get("name"),
                "status": j.get("status"),
                "type": j.get("type"),
                "finished": j.get("finished"),
                "started": j.get("started"),
                "url": j.get("url"),
            }
            for j in data.get("results", [])
        ]
        return tool_result_text({"count": data.get("count"), "jobs": rows})

    if name == "aap_list_job_templates":
        limit = int(arguments.get("limit", 50))
        data = api_get("/api/controller/v2/job_templates/", {"page_size": limit})
        rows = [
            {
                "id": t.get("id"),
                "name": t.get("name"),
                "org": (t.get("summary_fields") or {})
                .get("organization", {})
                .get("name"),
            }
            for t in data.get("results", [])
        ]
        return tool_result_text({"count": data.get("count"), "templates": rows})

    if name == "aap_get_job":
        job_id = int(arguments["job_id"])
        kind = arguments.get("job_type", "unified")
        if kind == "unified":
            u = api_get(f"/api/controller/v2/unified_jobs/{job_id}/")
            jtype = u.get("type", "")
            if jtype == "job":
                kind = "job"
            elif jtype in ("system_job", "cleanup_job"):
                kind = "system_job"
            else:
                return tool_result_text(u)
        path = (
            f"/api/controller/v2/jobs/{job_id}/"
            if kind == "job"
            else f"/api/controller/v2/system_jobs/{job_id}/"
        )
        return tool_result_text(api_get(path))

    raise ValueError(f"Unknown tool: {name}")


def send(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle(msg: dict) -> None:
    mid = msg.get("id")
    method = msg.get("method")
    params = msg.get("params") or {}

    if method == "initialize":
        send(
            {
                "jsonrpc": "2.0",
                "id": mid,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "aap-api-mcp",
                        "version": "1.0.0",
                    },
                },
            }
        )
        return

    if method == "notifications/initialized":
        return

    if method == "tools/list":
        send({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}})
        return

    if method == "tools/call":
        try:
            result = call_tool(params.get("name", ""), params.get("arguments") or {})
            send({"jsonrpc": "2.0", "id": mid, "result": result})
        except Exception as e:
            send(
                {
                    "jsonrpc": "2.0",
                    "id": mid,
                    "error": {"code": -32000, "message": str(e)},
                }
            )
        return

    if mid is not None:
        send(
            {
                "jsonrpc": "2.0",
                "id": mid,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        )


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            handle(json.loads(line))
        except json.JSONDecodeError:
            continue


if __name__ == "__main__":
    main()
