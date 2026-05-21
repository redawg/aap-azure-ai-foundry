#!/usr/bin/env python3
"""Build Foundry agent system instructions (Azure alerts → AAP templates)."""
from __future__ import annotations

import os
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_PATH = Path(
    os.environ.get(
        "AZURE_ALERT_TEMPLATE_MAP",
        REPO_ROOT / "config" / "azure_alert_template_map.yml",
    )
)


def _format_mapping_table(entries: list[dict]) -> str:
    lines = ["| Template ID | Name | Use when alert mentions |", "|---:|---|---|"]
    for t in entries:
        keywords = ", ".join(t.get("use_when", [])[:8])
        if len(t.get("use_when", [])) > 8:
            keywords += ", …"
        lines.append(f"| {t.get('id', '?')} | {t.get('name', '?')} | {keywords} |")
    return "\n".join(lines)


def load_alert_template_map(path: Path | None = None) -> dict:
    path = path or MAP_PATH
    if not path.is_file():
        return {"templates": [], "alert_field_hints": []}
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_agent_instructions(map_path: Path | None = None) -> str:
    data = load_alert_template_map(map_path)
    table = _format_mapping_table(data.get("templates", []))
    fields = ", ".join(f"`{f}`" for f in data.get("alert_field_hints", []))

    return f"""You are an Ansible Automation Platform (AAP) copilot integrated with Azure AI Foundry.

## Primary workflow: Azure alert → job template recommendation

When the user provides an Azure Monitor alert, Action Group payload, Log Analytics query result, or Foundry error:

1. **Parse the alert** — extract rule name, severity, resource type/id, error text, and any `properties` / `essentials` fields ({fields}).
2. **List templates** — call MCP tool `controller.job_templates_list` (job_management toolset) to fetch current job templates from AAP.
3. **Recommend one template** — pick the best match using the mapping below AND template names/descriptions from AAP. Explain why in plain language.
4. **Respond with**:
   - Recommended template **ID** and **name**
   - Confidence (high / medium / low)
   - Brief remediation summary tied to the alert
   - Optional next step: offer to launch via `controller.job_templates_launch_create` only after explicit user approval (writes require approval).

If no template fits, say so and suggest creating one; still list available templates.

## Workshop template mapping (hints — always verify via MCP)

{table}

## MCP usage

- Use MCP tools on `{os.environ.get('AAP_MCP_BASE_URL', 'https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io')}/mcp` or `/job_management/mcp`.
- Authentication is Gateway **Bearer** token via project connection `Authorization` header.
- Read operations (list templates, jobs, inventories) do not need launch approval.
- **Never** launch jobs or change platform state without user confirmation.

## Example user message

"Azure alert fired: DeploymentNotFound for Foundry MCP tools/list on resource foundry-wg2cd-1"

→ Recommend template **13** (Register AAP MCP with Azure Foundry) after confirming it exists in `job_templates_list`.
"""


if __name__ == "__main__":
    print(build_agent_instructions())
