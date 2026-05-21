#!/usr/bin/env python3
"""
Configure Azure AI Foundry Agent Service with the Ansible MCP server.

Prerequisites:
  pip install azure-ai-projects azure-identity python-dotenv
  az login
  Copy .env.example to .env and set FOUNDRY_* and AAP_MCP_TOKEN

Creates:
  1. A key-based project connection (Authorization: Bearer <AAP token>)
  2. A prompt agent with MCPTool pointing at the AAP MCP endpoint
"""
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "").strip()
MODEL = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME", "claude-sonnet-4-5").strip()
CONNECTION_NAME = os.environ.get("MCP_PROJECT_CONNECTION_NAME", "aap-mcp-bearer").strip()
MCP_BASE = os.environ.get(
    "AAP_MCP_BASE_URL",
    "https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io",
).rstrip("/")
AAP_USER = os.environ.get("AAP_USER", "admin").strip()
AAP_PASSWORD = os.environ.get("AAP_PASSWORD", "").strip()
AGENT_NAME = os.environ.get("FOUNDRY_AGENT_NAME", "aap-automation-agent").strip()

# Unified MCP endpoint (all tool categories); Foundry also supports per-toolset URLs below.
MCP_SERVER_URL = f"{MCP_BASE}/mcp"
MCP_SERVER_LABEL = "ansible-aap"


def _require_env() -> None:
    missing = [k for k, v in [
        ("FOUNDRY_PROJECT_ENDPOINT", PROJECT_ENDPOINT),
        ("AAP_PASSWORD", AAP_PASSWORD),
    ] if not v]
    if missing:
        print(f"Missing required env: {', '.join(missing)}", file=sys.stderr)
        print("Copy .env.example to .env and fill values.", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    _require_env()

    from azure.identity import DefaultAzureCredential
    import base64

    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import PromptAgentDefinition, MCPTool

    from foundry_instructions import build_agent_instructions

    credential = DefaultAzureCredential()
    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)

    # MCP requires Gateway Bearer token (see scripts/create-aap-gateway-token.sh)
    import subprocess

    tok = os.environ.get("AAP_GATEWAY_TOKEN", "").strip()
    if not tok:
        tok = subprocess.check_output(
            [os.path.join(os.path.dirname(__file__), "create-aap-gateway-token.sh")],
            env={**os.environ, "AAP_PASSWORD": AAP_PASSWORD},
            text=True,
        ).strip()
    auth_header = f"Bearer {tok}"

    print(f"Creating/updating project connection '{CONNECTION_NAME}'...")
    connection = project.connections.create_or_update(
        name=CONNECTION_NAME,
        api_key={"key": auth_header},
        metadata={"purpose": "ansible-mcp-gateway-bearer"},
    )
    print(f"  Connection id: {connection.id}")

    tool = MCPTool(
        server_label=MCP_SERVER_LABEL,
        server_url=MCP_SERVER_URL,
        require_approval="always",
        project_connection_id=CONNECTION_NAME,
    )

    print(f"Creating agent '{AGENT_NAME}' with MCP tool {MCP_SERVER_URL}...")
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL,
            instructions=build_agent_instructions(),
            tools=[tool],
        ),
    )
    print(f"Agent created: name={agent.name} id={agent.id} version={agent.version}")
    print()
    print("Optional per-toolset MCP URLs (add extra MCPTool entries if needed):")
    for path in (
        "job_management",
        "inventory_management",
        "system_monitoring",
        "user_management",
        "security_compliance",
        "platform_configuration",
    ):
        print(f"  {MCP_BASE}/{path}/mcp")


if __name__ == "__main__":
    main()
