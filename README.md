# Azure AI Foundry + Ansible MCP

Register an **already-deployed** Ansible Automation Platform MCP server with [Azure AI Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol).

This repo does **not** install MCP on AAP. Set `aap_mcp_base_url` to your existing MCP route.

## Ansible

```bash
cp group_vars/all.yml.example group_vars/all.yml
# Edit: aap_password, foundry_project_endpoint (workshop example below)

# Option A — device-code login (no az CLI required)
python3 -m pip install --user azure-identity
AAP_PASSWORD='…' ./scripts/register-foundry.sh

# Option B — Azure CLI
sudo dnf install -y azure-cli   # or: ./scripts/install-az.sh
az login
ansible-playbook playbooks/site.yml
```

Workshop Foundry project endpoint (example):

`https://foundry-wg2cd-1.services.ai.azure.com/api/projects/foundry-wg2cd-1-project`

### Tags

| Tag | Action |
|-----|--------|
| `foundry_verify_mcp` | Probe MCP `/mcp` only |
| `foundry_connection` | Foundry project connection only |
| `foundry_agent` | Create agent with MCP tool |
| `foundry_mcp_agent` | Full registration (default) |

Examples:

```bash
# MCP health check only
ansible-playbook playbooks/site.yml --tags foundry_verify_mcp

# Connection only (no agent)
ansible-playbook playbooks/site.yml -e foundry_register_agent=false --tags foundry_connection
```

## Copilot: Azure alert → job template recommendation

The agent instructions map Azure Monitor / Foundry errors to AAP job templates using MCP `controller.job_templates_list`.

| File | Purpose |
|------|---------|
| [`config/azure_alert_template_map.yml`](config/azure_alert_template_map.yml) | Keyword → template hints (workshop IDs 7, 9, 10, 13) |
| [`examples/azure-alert-mcp-404.json`](examples/azure-alert-mcp-404.json) | Sample alert to paste in Playground |
| [`scripts/update-foundry-agent-instructions.sh`](scripts/update-foundry-agent-instructions.sh) | Publish a new agent version with updated instructions |

```bash
az login
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4o ./scripts/update-foundry-agent-instructions.sh
```

**Playground test:** paste the JSON from `examples/azure-alert-mcp-404.json` and ask: *Which job template should remediate this alert?*

## Foundry portal (manual)

1. [https://ai.azure.com](https://ai.azure.com) → **Connected resources** → **Custom keys** → name `Authorization`, value `Bearer <gateway-token>`
2. **Agents** → **MCP** → server URL `{{ aap_mcp_base_url }}/mcp`

## Scripts (optional)

```bash
cp .env.example .env
./scripts/configure-foundry-rest.sh
```

## Variables

See [`group_vars/all.yml.example`](group_vars/all.yml.example).

## Security

Do not commit `creds.md`, `.env`, or `group_vars/all.yml`.

## References

- [Connect agents to MCP servers (Foundry)](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)
- [MCP server authentication (Foundry)](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication)
