#!/usr/bin/env python3
"""Register AAP MCP in Azure AI Foundry (connection + agent) via REST."""
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

TENANT = os.environ.get("AZURE_TENANT", "RedHat.com")
CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")
FOUNDRY_PROJECT = os.environ.get("FOUNDRY_PROJECT", "foundry-wg2cd-1-project")
FOUNDRY_ACCOUNT = os.environ.get("FOUNDRY_ACCOUNT", "foundry-wg2cd-1")
FOUNDRY_PROJECT_ENDPOINT = os.environ.get(
    "FOUNDRY_PROJECT_ENDPOINT",
    f"https://{FOUNDRY_ACCOUNT}.services.ai.azure.com/api/projects/{FOUNDRY_PROJECT}",
)
AAP_USER = os.environ.get("AAP_USER", "admin")
AAP_PASSWORD = os.environ.get("AAP_PASSWORD", "")
AAP_MCP_BASE = os.environ.get(
    "AAP_MCP_BASE_URL",
    "https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io",
)
CONNECTION_NAME = os.environ.get("MCP_PROJECT_CONNECTION_NAME", "aap-mcp-bearer")
AGENT_NAME = os.environ.get("FOUNDRY_AGENT_NAME", "aap-automation-agent")
MODEL = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME", "claude-sonnet-4-5")
SCOPE = "https://ai.azure.com/.default"
CONN_API = "2025-05-01-preview"
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


def token_via_az() -> str | None:
    try:
        out = subprocess.run(
            ["az", "account", "get-access-token", "--scope", SCOPE, "-o", "tsv"],
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )
        return out.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def token_via_device_code() -> str:
    from azure.identity import DeviceCodeCredential

    print("Azure login (device code) — use your Red Hat / lab account in the browser.\n")
    cred = DeviceCodeCredential(tenant_id=TENANT)
    return cred.get_token(SCOPE).token


def token_via_client_secret() -> str:
    data = urllib.parse.urlencode(
        {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": SCOPE,
            "grant_type": "client_credentials",
        }
    ).encode()
    url = f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token"
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())["access_token"]


def obtain_token() -> str:
    if os.environ.get("FOUNDRY_ACCESS_TOKEN"):
        return os.environ["FOUNDRY_ACCESS_TOKEN"]
    t = token_via_az()
    if t:
        print("Using token from: az account get-access-token")
        return t
    if os.environ.get("AZURE_USE_DEVICE_CODE", "1") == "1":
        return token_via_device_code()
    if CLIENT_ID and CLIENT_SECRET:
        print("Using workshop service principal (may lack Foundry write RBAC).")
        return token_via_client_secret()
    return token_via_device_code()


def main() -> int:
    if not AAP_PASSWORD:
        print("Set AAP_PASSWORD", file=sys.stderr)
        return 1

    print(f"Foundry endpoint: {FOUNDRY_PROJECT_ENDPOINT}")
    print(f"MCP server: {AAP_MCP_BASE.rstrip('/')}/mcp\n")

    token = obtain_token()
    basic = base64.b64encode(f"{AAP_USER}:{AAP_PASSWORD}".encode()).decode()

    conn_url = (
        f"{FOUNDRY_PROJECT_ENDPOINT}/connections/{CONNECTION_NAME}"
        f"?api-version={CONN_API}"
    )
    conn_body = {
        "name": CONNECTION_NAME,
        "type": "CustomKeys",
        "credentials": {"keys": {"Authorization": f"Basic {basic}"}},
    }
    print(f"== PUT connection {CONNECTION_NAME} ==")
    code, body = http("PUT", conn_url, token, conn_body)
    print(f"HTTP {code}")
    if body:
        print(body[:1000])
    if code not in (200, 201):
        if "PermissionDenied" in body or code == 401:
            print(
                "\nHint: log in with a user that has access to the Foundry project "
                "(device code above, or install az and run az login).",
                file=sys.stderr,
            )
        return 1

    agent_url = f"{FOUNDRY_PROJECT_ENDPOINT}/agents?api-version={AGENT_API}"
    agent_body = {
        "name": AGENT_NAME,
        "description": "Ansible Automation Platform agent via MCP",
        "definition": {
            "kind": "prompt",
            "model": MODEL,
            "instructions": (
                "Use Ansible Automation Platform MCP tools for inventories, jobs, "
                "and platform configuration. Request approval before write operations."
            ),
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
    code, body = http("POST", agent_url, token, agent_body)
    print(f"HTTP {code}")
    if body:
        print(body[:1500])
    if code in (200, 201, 409):
        print(f"\nDone. Open https://ai.azure.com → project → Playground → {AGENT_NAME}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
