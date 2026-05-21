# Microsoft Copilot Studio + RHPDS AAP MCP (no Foundry)

Connect **Copilot Studio** to the workshop AAP MCP server using a **Power Apps custom connector** and OpenAPI import.

Upstream: [ansible-tmm/mcp-demo copilotstudio-mcp-setup](https://github.com/ansible-tmm/mcp-demo/tree/main/copilotstudio-mcp-setup) — this folder is the same pattern with the **RHPDS OpenShift host** and all **six toolsets**.

## Files

| File | Purpose |
|------|---------|
| [`aap-mcp-openapi-rhpds.yaml`](aap-mcp-openapi-rhpds.yaml) | OpenAPI 2.0 with workshop host and three MCP toolsets |

## Prerequisites

- [Microsoft Copilot Studio](https://copilotstudio.microsoft.com) license
- [Power Apps](https://make.powerapps.com) access
- AAP **Gateway token**: `ansible-playbook playbooks/create-gateway-token.yml -e @group_vars/all.yml`
- Workshop MCP must be reachable from Azure with a **trusted TLS certificate** (Copilot Studio rejects self-signed certs)

## Setup

1. **Import connector** — Power Apps → Custom connectors → Import OpenAPI → `aap-mcp-openapi-rhpds.yaml`
2. **Security** — API Key, parameter name **`Authorization`**, location **Header**
3. **Test connection** — API Key value: `Bearer <your-gateway-token>` (include the word `Bearer`)
4. **Copilot Studio** — Agent → Tools → Add tool → Custom connector → select connector + connection
5. **Prompt** — e.g. “List my Ansible job templates” or “Show recent failed jobs”

## Toolset URLs (same as mcp-demo)

| Path | Use |
|------|-----|
| `/job_management/mcp` | Jobs and job templates |
| `/inventory_management/mcp` | Inventories and hosts |
| `/system_monitoring/mcp` | Platform health |
| `/user_management/mcp` | Users, teams, RBAC |
| `/security_compliance/mcp` | Credentials, audit |
| `/platform_configuration/mcp` | Platform settings |

Unified `/mcp` is available but heavy for some hosts; prefer toolset paths (see [mcp-demo README](../mcp-demo/README.md)).

## Auth reference

See [`docs/AAP-MCP-AI-REFERENCE.md`](../docs/AAP-MCP-AI-REFERENCE.md) sections 2–4.

## Local Copilot SDK alternative

For a **local GitHub Copilot SDK** agent (no Copilot Studio), use [`../copilot-aap-agent/`](../copilot-aap-agent/README.md).
