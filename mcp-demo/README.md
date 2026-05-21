# AAP MCP client setup (mcp-demo pattern)

Workshop-specific configs following **[ansible-tmm/mcp-demo](https://github.com/ansible-tmm/mcp-demo/tree/main)** — six MCP toolset endpoints, no Azure AI Foundry.

| Platform | This repo | Upstream guide |
|----------|-----------|----------------|
| **Cursor IDE** | [`cursor-mcp-setup/`](cursor-mcp-setup/README.md) | [cursor-mcp-setup](https://github.com/ansible-tmm/mcp-demo/tree/main/cursor-mcp-setup) |
| **Claude Desktop** | Use upstream + RHPDS URLs below | [claude-mcp-setup](https://github.com/ansible-tmm/mcp-demo/tree/main/claude-mcp-setup) |
| **Microsoft Copilot Studio** | [`../copilotstudio/`](../copilotstudio/README.md) | [copilotstudio-mcp-setup](https://github.com/ansible-tmm/mcp-demo/tree/main/copilotstudio-mcp-setup) |
| **GitHub Copilot SDK** | [`../copilot-aap-agent/`](../copilot-aap-agent/README.md) | (not in mcp-demo; HTTP MCP via SDK) |

## RHPDS workshop endpoints (OpenShift)

Base host (no port):

`https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io`

| Toolset | Path |
|---------|------|
| Job management | `/job_management/mcp` |
| Inventory | `/inventory_management/mcp` |
| System monitoring | `/system_monitoring/mcp` |
| User management | `/user_management/mcp` |
| Security & compliance | `/security_compliance/mcp` |
| Platform configuration | `/platform_configuration/mcp` |

Unified catalog (large): `/mcp` — see [`docs/AAP-MCP-AI-REFERENCE.md`](../docs/AAP-MCP-AI-REFERENCE.md).

## Token

Gateway Bearer token (not Controller password alone for MCP):

```bash
ansible-playbook playbooks/create-gateway-token.yml -e @group_vars/all.yml
export MY_SERVICE_TOKEN='<token-from-output>'
```

Or `export MY_SERVICE_TOKEN` from `group_vars/all.yml` → `aap_gateway_token`.

## Cursor quick start

```bash
source mcp-demo/cursor-mcp-setup/env-rhpds.sh
# Cursor → Settings → Tools & MCP → paste mcp-demo/cursor-mcp-setup/mcp-config-rhpds.json
```

## Video / upstream docs

- [mcp-demo README](https://github.com/ansible-tmm/mcp-demo/blob/main/README.md)
- [YouTube: 5 use-cases with AAP MCP](https://youtu.be/h6VboweM8Ww)
