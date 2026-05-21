#!/usr/bin/env python3
"""Register AAP MCP in Azure AI Foundry: ARM connection + data-plane agent."""
from __future__ import annotations

import base64
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)
from foundry_instructions import build_agent_instructions  # noqa: E402

TENANT = os.environ.get("AZURE_TENANT", "RedHat.com")
CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")
FOUNDRY_ACCOUNT = os.environ.get("FOUNDRY_ACCOUNT", "foundry-wg2cd-1")
FOUNDRY_PROJECT = os.environ.get("FOUNDRY_PROJECT", "foundry-wg2cd-1-project")
FOUNDRY_RG = os.environ.get("FOUNDRY_RG", "openenv-wg2cd-1")
FOUNDRY_SUB = os.environ.get("FOUNDRY_SUB", "9dc2c3d2-35a8-4370-8997-b56a57b5778d")
FOUNDRY_PROJECT_ENDPOINT = os.environ.get(
    "FOUNDRY_PROJECT_ENDPOINT",
    f"https://{FOUNDRY_ACCOUNT}.services.ai.azure.com/api/projects/{FOUNDRY_PROJECT}",
)
ARM_CONN_URL = (
    f"https://management.azure.com/subscriptions/{FOUNDRY_SUB}/resourceGroups/{FOUNDRY_RG}"
    f"/providers/Microsoft.CognitiveServices/accounts/{FOUNDRY_ACCOUNT}"
    f"/projects/{FOUNDRY_PROJECT}/connections"
)
AAP_USER = os.environ.get("AAP_USER", "admin")
AAP_PASSWORD = os.environ.get("AAP_PASSWORD", "")
AAP_BASE_URL = os.environ.get(
    "AAP_BASE_URL",
    "https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io",
)
AAP_GATEWAY_TOKEN = os.environ.get("AAP_GATEWAY_TOKEN", "").strip()
AAP_MCP_BASE = os.environ.get(
    "AAP_MCP_BASE_URL",
    "https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io",
)
CONNECTION_NAME = os.environ.get("MCP_PROJECT_CONNECTION_NAME", "aap-mcp-bearer")
AGENT_NAME = os.environ.get("FOUNDRY_AGENT_NAME", "aap-automation-agent")
MODEL = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4.1")
SCOPE_AI = "https://ai.azure.com/.default"
SCOPE_MGMT = "https://management.azure.com/.default"
CONN_ARM_API = "2025-06-01"
AGENT_API = "v1"


def http(method: str, url: str, token: str, body: dict | None = None) -> tuple[int, str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def token_via_az(scope: str) -> str | None:
    try:
        out = subprocess.run(
            [
                "az", "account", "get-access-token",
                "--scope", scope,
                "--query", "accessToken",
                "-o", "tsv",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
            env={**os.environ, "AZURE_CORE_OUTPUT": "tsv"},
        )
        token = (out.stdout or "").strip()
        return token if len(token) > 100 else None
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"az token failed for {scope}: {e}", file=sys.stderr)
        return None


def token_via_device_code(scope: str) -> str:
    from azure.identity import DeviceCodeCredential

    print("Azure login (device code)…\n")
    return DeviceCodeCredential(tenant_id=TENANT).get_token(scope).token


def create_aap_gateway_token() -> str:
    """MCP requires Authorization: Bearer <gateway token>; Basic auth breaks sessions."""
    if AAP_GATEWAY_TOKEN:
        return AAP_GATEWAY_TOKEN
    url = f"{AAP_BASE_URL.rstrip('/')}/api/gateway/v1/tokens/"
    body = json.dumps(
        {
            "description": os.environ.get("AAP_TOKEN_DESCRIPTION", "foundry-mcp"),
            "application": "",
            "scope": "write",
        }
    ).encode()
    creds = base64.b64encode(f"{AAP_USER}:{AAP_PASSWORD}".encode()).decode()
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/json",
        },
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Gateway token create failed HTTP {e.code}: {e.read().decode()[:400]}", file=sys.stderr)
        return ""
    token = data.get("token", "")
    if not token:
        print(f"Gateway token missing in response: {data}", file=sys.stderr)
    return token


def obtain_token(scope: str) -> str:
    t = token_via_az(scope)
    if t:
        return t
    if CLIENT_ID and CLIENT_SECRET:
        data = urllib.parse.urlencode(
            {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "scope": scope,
                "grant_type": "client_credentials",
            }
        ).encode()
        url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method="POST"), timeout=60) as r:
            return json.loads(r.read())["access_token"]
    return token_via_device_code(scope)


def register_connection_arm(mgmt_token: str, auth_header: str) -> bool:
    url = f"{ARM_CONN_URL}/{CONNECTION_NAME}?api-version={CONN_ARM_API}"
    body = {
        "properties": {
            "authType": "CustomKeys",
            "category": "CustomKeys",
            "target": "_",
            "credentials": {"keys": {"Authorization": auth_header}},
        }
    }
    print(f"== ARM PUT connection {CONNECTION_NAME} ==")
    code, resp = http("PUT", url, mgmt_token, body)
    print(f"HTTP {code}")
    if resp:
        print(resp[:800])
    return code in (200, 201)


def verify_mcp_bearer(auth_header: str) -> bool:
    """tools/list must return 200 with a valid Bearer session."""
    url = f"{AAP_MCP_BASE.rstrip('/')}/mcp"
    init_body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "register-foundry-mcp", "version": "1"},
            },
        }
    ).encode()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    req = urllib.request.Request(url, data=init_body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            sid = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
            resp.read()
    except urllib.error.HTTPError as e:
        print(f"MCP initialize failed HTTP {e.code}", file=sys.stderr)
        return False
    if not sid:
        print("MCP initialize missing Mcp-Session-Id", file=sys.stderr)
        return False
    list_body = json.dumps(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    ).encode()
    headers["Mcp-Session-Id"] = sid
    req2 = urllib.request.Request(url, data=list_body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req2, timeout=60, context=ctx) as resp2:
            body = resp2.read().decode()
            ok = resp2.status == 200 and "tools" in body
            print(f"== MCP tools/list probe: HTTP {resp2.status} ({'OK' if ok else 'FAIL'}) ==")
            return ok
    except urllib.error.HTTPError as e:
        print(f"MCP tools/list failed HTTP {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        return False


def register_agent(ai_token: str) -> bool:
    url = f"{FOUNDRY_PROJECT_ENDPOINT}/agents?api-version={AGENT_API}"
    body = {
        "name": AGENT_NAME,
        "description": "AAP copilot: recommend job templates from Azure alerts via MCP",
        "definition": {
            "kind": "prompt",
            "model": MODEL,
            "instructions": build_agent_instructions(),
            "tools": [
                {
                    "type": "mcp",
                    "server_label": "ansible-aap",
                    "server_url": f"{AAP_MCP_BASE.rstrip('/')}/mcp",
                    "require_approval": "always",
                    "project_connection_id": CONNECTION_NAME,
                }
            ],
        },
    }
    print(f"\n== POST agent {AGENT_NAME} ==")
    code, resp = http("POST", url, ai_token, body)
    print(f"HTTP {code}")
    if resp:
        print(resp[:1500])
    return code in (200, 201, 409)


def main() -> int:
    if not AAP_PASSWORD:
        print("Set AAP_PASSWORD", file=sys.stderr)
        return 1

    gateway = create_aap_gateway_token()
    if not gateway:
        return 1
    auth_header = f"Bearer {gateway}"
    print(f"Project: {FOUNDRY_PROJECT}")
    print(f"MCP: {AAP_MCP_BASE.rstrip('/')}/mcp")
    print("MCP auth: Gateway Bearer token (not Basic)\n")

    if not verify_mcp_bearer(auth_header):
        return 1

    mgmt = obtain_token(SCOPE_MGMT)
    ai = obtain_token(SCOPE_AI)

    if not register_connection_arm(mgmt, auth_header):
        return 1
    if not register_agent(ai):
        return 1

    print(
        "\nIMPORTANT: ARM may not persist connection secrets. In Foundry portal:\n"
        f"  Project {FOUNDRY_PROJECT} → Management → Connected resources → {CONNECTION_NAME}\n"
        "  Custom keys → Authorization → paste this value (include 'Bearer ' prefix):\n"
        f"  {auth_header}\n"
    )
    print(f"Done → https://ai.azure.com project {FOUNDRY_PROJECT} → Agents → {AGENT_NAME}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
