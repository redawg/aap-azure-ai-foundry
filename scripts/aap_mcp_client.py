#!/usr/bin/env python3
"""Shared AAP MCP HTTP client (Bearer session + tools/list + tools/call)."""
from __future__ import annotations

import base64
import json
import os
import ssl
from http.client import HTTPSConnection
from urllib.parse import urlparse

AAP_USER = os.environ.get("AAP_USER", "admin")
AAP_PASSWORD = os.environ.get("AAP_PASSWORD", "")
AAP_GATEWAY_TOKEN = os.environ.get("AAP_GATEWAY_TOKEN", "").strip()
AAP_BASE_URL = os.environ.get(
    "AAP_BASE_URL",
    "https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io",
).rstrip("/")
MCP_BASE = os.environ.get(
    "AAP_MCP_BASE_URL",
    "https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io",
).rstrip("/")
MCP_PATH = os.environ.get("AAP_MCP_SERVER_PATH", "/mcp")


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


def gateway_token() -> str:
    if AAP_GATEWAY_TOKEN:
        return AAP_GATEWAY_TOKEN
    if not AAP_PASSWORD:
        raise RuntimeError("Set AAP_PASSWORD or AAP_GATEWAY_TOKEN")
    parsed = urlparse(AAP_BASE_URL)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    conn = HTTPSConnection(parsed.hostname or "", port, context=ctx, timeout=60)
    payload = json.dumps(
        {"description": "aap-mcp-client", "application": "", "scope": "write"}
    ).encode()
    auth = base64.b64encode(f"{AAP_USER}:{AAP_PASSWORD}".encode()).decode()
    conn.request(
        "POST",
        "/api/gateway/v1/tokens/",
        body=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Basic {auth}"},
    )
    resp = conn.getresponse()
    body = resp.read().decode()
    conn.close()
    if resp.status >= 400:
        raise RuntimeError(f"Gateway token HTTP {resp.status}: {body[:400]}")
    return json.loads(body)["token"]


class McpClient:
    def __init__(self, url: str | None = None, *, token: str | None = None) -> None:
        self.url = url or f"{MCP_BASE}{MCP_PATH}"
        parsed = urlparse(self.url)
        self.host = parsed.hostname or ""
        self.path = parsed.path or "/"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.conn = HTTPSConnection(self.host, port, context=ctx, timeout=120)
        tok = token or gateway_token()
        self.auth_header = f"Bearer {tok}"
        self.session_id: str | None = None
        self._req_id = 0

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def _request(self, body_obj: dict, *, include_session: bool = True) -> str:
        payload = json.dumps(body_obj).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": self.auth_header,
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
        sid = resp_headers.get("Mcp-Session-Id") or resp_headers.get("mcp-session-id")
        if sid:
            self.session_id = sid
        return body

    def rpc(self, method: str, params: dict | None = None) -> list[dict]:
        msg: dict = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        if method != "notifications/initialized":
            msg["id"] = self._next_id()
        body = self._request(msg, include_session=method != "initialize")
        return parse_sse(body)

    def connect(self) -> dict:
        msgs = self.rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "aap-mcp-or-navigator", "version": "1.0"},
            },
        )
        result = msgs[-1].get("result", {}) if msgs else {}
        try:
            self.rpc("notifications/initialized")
        except RuntimeError:
            pass
        return result.get("serverInfo", {})

    def list_tools(self) -> list[dict]:
        tools: list[dict] = []
        for msg in self.rpc("tools/list"):
            tools.extend(msg.get("result", {}).get("tools", []))
        return tools

    def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        msgs = self.rpc(
            "tools/call",
            {"name": name, "arguments": arguments or {}},
        )
        for msg in msgs:
            if msg.get("error"):
                err = msg["error"]
                if err.get("code") == -32603 and "Unknown tool" in str(err.get("message", "")):
                    raise ToolNotAvailableError(name)
                raise RuntimeError(json.dumps(err))
            if "result" in msg:
                return msg["result"]
        raise RuntimeError(f"No result from tools/call {name}")

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass


class ToolNotAvailableError(RuntimeError):
    pass


def tool_result_json(result: dict) -> dict:
    for block in result.get("content", []):
        text = block.get("text", "")
        if text:
            return json.loads(text)
    return result
