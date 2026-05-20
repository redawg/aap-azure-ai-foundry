#!/usr/bin/env python3
"""List job templates via AAP MCP with persistent HTTP connection (session affinity)."""
from __future__ import annotations

import json
import os
import ssl
import sys
import base64
from http.client import HTTPSConnection
from urllib.parse import urlparse

USER = os.environ.get("AAP_USER", "admin")
PASSWORD = os.environ.get("AAP_PASSWORD")
MCP_BASE = os.environ.get(
    "MCP_BASE",
    "https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io",
)
MCP_URLS = [
    f"{MCP_BASE.rstrip('/')}/job_management/mcp",
    f"{MCP_BASE.rstrip('/')}/mcp",
]


def parse_sse(body: str) -> list[dict]:
    messages: list[dict] = []
    for line in body.splitlines():
        if line.startswith("data:"):
            payload = line[5:].strip()
            if payload:
                try:
                    messages.append(json.loads(payload))
                except json.JSONDecodeError:
                    pass
    if not messages and body.strip().startswith("{"):
        messages.append(json.loads(body))
    return messages


class McpClient:
    def __init__(self, url: str) -> None:
        self.url = url
        parsed = urlparse(url)
        self.host = parsed.hostname or ""
        self.path = parsed.path or "/"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.conn = HTTPSConnection(self.host, port, context=ctx, timeout=90)
        self.auth = base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
        self.session_id: str | None = None

    def _request(
        self,
        body_obj: dict,
        *,
        include_session: bool = True,
    ) -> tuple[int, dict[str, str], str]:
        payload = json.dumps(body_obj).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Basic {self.auth}",
            "Connection": "keep-alive",
        }
        if include_session and self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        self.conn.request("POST", self.path, body=payload, headers=headers)
        resp = self.conn.getresponse()
        resp_headers = {k: v for k, v in resp.getheaders()}
        body = resp.read().decode()
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status}: {body[:600]}")
        # Capture session from initialize response
        sid = resp_headers.get("Mcp-Session-Id") or resp_headers.get("mcp-session-id")
        if sid:
            self.session_id = sid
        return resp.status, resp_headers, body

    def rpc(self, method: str, params: dict, req_id: int | None) -> list[dict]:
        msg: dict = {"jsonrpc": "2.0", "method": method, "params": params}
        if req_id is not None:
            msg["id"] = req_id
        _, _, body = self._request(msg, include_session=method != "initialize")
        return parse_sse(body)

    def notify_initialized(self) -> None:
        # JSON-RPC notification — no "id" field
        msg = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        try:
            self._request(msg, include_session=True)
        except RuntimeError:
            pass  # optional on some deployments

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass


def run_on_endpoint(url: str) -> bool:
    print(f"\n--- Endpoint: {url} ---")
    client = McpClient(url)
    try:
        print("== MCP initialize ==")
        init_msgs = client.rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-list-templates", "version": "1.0"},
            },
            1,
        )
        if not init_msgs:
            print("FAIL: no initialize response")
            return False
        server = init_msgs[-1].get("result", {}).get("serverInfo", {})
        print(f"OK: server={server.get('name')} version={server.get('version')}")
        print(f"Session: {client.session_id}")

        print("\n== MCP notifications/initialized ==")
        client.notify_initialized()
        print("sent (or skipped)")

        print("\n== MCP tools/list ==")
        list_msgs = []
        try:
            list_msgs = client.rpc("tools/list", {}, 2)
            for msg in list_msgs:
                for t in msg.get("result", {}).get("tools", []):
                    if "job_template" in t.get("name", ""):
                        print(f"  - {t['name']}")
        except RuntimeError as e:
            print(f"tools/list: {e}")

        print("\n== MCP tools/call: controller.job_templates_list ==")
        call_msgs = client.rpc(
            "tools/call",
            {"name": "controller.job_templates_list", "arguments": {}},
            3,
        )
        for msg in call_msgs:
            if msg.get("error"):
                print("ERROR:", json.dumps(msg["error"], indent=2))
                return False
            for block in msg.get("result", {}).get("content", []):
                text = block.get("text", "")
                if not text:
                    continue
                data = json.loads(text)
                if isinstance(data, dict) and "results" in data:
                    count = data.get("count", len(data["results"]))
                    print(f"\nJob templates: {count}")
                    for t in data["results"]:
                        org = (t.get("summary_fields") or {}).get("organization") or {}
                        print(
                            f"  [{t.get('id')}] {t.get('name')}  (org: {org.get('name', '-')})"
                        )
                    return True
                print(json.dumps(data, indent=2)[:4000])
        return False
    finally:
        client.close()


def main() -> int:
    if not PASSWORD:
        print("Set AAP_PASSWORD", file=sys.stderr)
        return 1
    for url in MCP_URLS:
        try:
            if run_on_endpoint(url):
                return 0
        except Exception as e:
            print(f"Endpoint error: {e}")
    print("\nAll endpoints failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
