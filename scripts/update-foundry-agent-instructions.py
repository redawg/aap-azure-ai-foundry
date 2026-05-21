#!/usr/bin/env python3
"""Publish a new agent version with Azure alert → template recommendation instructions."""
from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

from foundry_instructions import build_agent_instructions  # noqa: E402

PROJECT_ENDPOINT = os.environ.get(
    "FOUNDRY_PROJECT_ENDPOINT",
    "https://foundry-wg2cd-1.services.ai.azure.com/api/projects/foundry-wg2cd-1-project",
).strip()
AGENT_NAME = os.environ.get("FOUNDRY_AGENT_NAME", "aap-automation-agent").strip()
MODEL = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT_NAME", "gpt-4o").strip()
MCP_BASE = os.environ.get(
    "AAP_MCP_BASE_URL",
    "https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io",
).rstrip("/")
CONNECTION_NAME = os.environ.get("MCP_PROJECT_CONNECTION_NAME", "aap-mcp-bearer").strip()
MCP_LABEL = os.environ.get("FOUNDRY_MCP_SERVER_LABEL", "ansible-aap").strip()


def main() -> int:
    try:
        from azure.identity import AzureCliCredential
        from azure.ai.projects import AIProjectClient
        from azure.ai.projects.models import PromptAgentDefinition, MCPTool
    except ImportError:
        print("pip install azure-ai-projects azure-identity pyyaml", file=sys.stderr)
        return 1

    instructions = build_agent_instructions()
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=AzureCliCredential(),
    )

    tool = MCPTool(
        server_label=MCP_LABEL,
        server_url=f"{MCP_BASE}/mcp",
        require_approval="always",
        project_connection_id=CONNECTION_NAME,
    )

    print(f"Creating new version for agent '{AGENT_NAME}' (model={MODEL})…")
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL,
            instructions=instructions,
            tools=[tool],
        ),
        description="AAP copilot: recommend job templates from Azure alerts via MCP",
    )
    print(f"OK: version={getattr(agent, 'version', agent)}")
    print(f"Playground: https://ai.azure.com → project → Agents → {AGENT_NAME}")
    print(f"Test paste: {REPO_ROOT}/examples/azure-alert-mcp-404.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
