#!/usr/bin/env python3
"""GitHub Copilot SDK chat agent → RHPDS AAP MCP (no Azure AI Foundry)."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from aap_mcp_client import gateway_token  # noqa: E402

DEFAULT_MCP_URL = (
    "https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io"
    "/job_management/mcp"
)


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _resolve_token() -> str:
    token = os.environ.get("AAP_GATEWAY_TOKEN", "").strip()
    if token:
        return token
    return gateway_token()


def _azure_provider() -> dict | None:
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
    model = os.environ.get("AZURE_MODEL_NAME", "o4-mini").strip()
    if not endpoint:
        return None
    from azure.identity import DefaultAzureCredential

    cred = DefaultAzureCredential()
    access = cred.get_token("https://cognitiveservices.azure.com/.default")
    return {
        "model": model,
        "provider": {
            "type": "azure",
            "baseUrl": endpoint.rstrip("/"),
            "bearerToken": access.token,
            "wireApi": "completions",
            "azure": {"apiVersion": "2025-04-01-preview"},
        },
    }


async def _run_chat() -> None:
    _load_dotenv()
    mcp_url = os.environ.get("AAP_MCP_URL", DEFAULT_MCP_URL).strip()
    token = _resolve_token()

    from copilot import CopilotClient
    from copilot.session import PermissionHandler

    client = CopilotClient()
    await client.start()

    session_kwargs: dict = {
        "on_permission_request": PermissionHandler.approve_all,
        "mcp_servers": {
            "aap-rhpds": {
                "type": "http",
                "url": mcp_url,
                "headers": {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json, text/event-stream",
                },
                "tools": ["*"],
                "timeout": 120000,
            }
        },
    }
    azure = _azure_provider()
    if azure:
        session_kwargs.update(azure)
    else:
        session_kwargs["model"] = os.environ.get("COPILOT_MODEL", "gpt-4.1")

    session = await client.create_session(**session_kwargs)
    print(f"AAP Copilot ready (MCP: {mcp_url}). Type 'exit' to quit.\n")

    try:
        while True:
            try:
                prompt = input("You> ").strip()
            except EOFError:
                break
            if not prompt or prompt.lower() in {"exit", "quit"}:
                break
            result = await session.send_and_wait(prompt)
            text = ""
            if result and result.data and result.data.content:
                text = result.data.content
            print(f"\nCopilot> {text or '(no content)'}\n")
    finally:
        await session.disconnect()
        await client.stop()


def main() -> None:
    try:
        asyncio.run(_run_chat())
    except KeyboardInterrupt:
        print("\nBye.")


if __name__ == "__main__":
    main()
