# Azure AI Foundry + Ansible MCP

Register an **already-deployed** Ansible Automation Platform MCP server with:
- [Azure AI Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)
- [Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/model-context-protocol)

This repo does **not** install MCP on AAP. Set `aap_mcp_base_url` to your existing MCP route.

## Ansible

See **[docs/RUNBOOK.md](docs/RUNBOOK.md)** for prerequisites, lab `creds.md` mapping, Azure login options, and troubleshooting.

```bash
cd /Users/cferman/azure-aap-mcp
cp group_vars/all.yml.example group_vars/all.yml
# Edit: aap_mcp_base_url, aap_password, foundry_project_endpoint

az login
ansible-playbook playbooks/site.yml
```

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

## Copilot Studio (automated + manual)

Integrate AAP MCP with Microsoft Copilot Studio using Power Platform Custom Connectors.

### Quick Setup

```bash
./scripts/setup-copilot.sh
```

Interactive script with three options:
1. **Full automation** - Uses Power Platform APIs (requires Azure CLI + login)
2. **Generate artifacts** - Creates files for manual setup in Power Apps
3. **Both** - Runs automation + generates artifacts as backup

### Manual Playbook Execution

```bash
# Option 1: Automated (requires az login)
ansible-playbook playbooks/setup-copilot-mcp.yml

# Option 2: Generate artifacts for manual setup
ansible-playbook playbooks/prepare-copilot-setup.yml
cd copilot-setup-artifacts
cat SETUP-INSTRUCTIONS.txt
```

### Documentation

- **Setup Guide**: [docs/COPILOT-STUDIO-SETUP.md](docs/COPILOT-STUDIO-SETUP.md)
- **Quick Reference**: [COPILOT-SETUP-QUICK-REF.md](COPILOT-SETUP-QUICK-REF.md)
- **Playbook Docs**: [playbooks/README-COPILOT-PLAYBOOKS.md](playbooks/README-COPILOT-PLAYBOOKS.md)

## Foundry portal (manual)

1. [https://ai.azure.com](https://ai.azure.com) → **Connections** → **Custom keys** → `Authorization: Basic …`
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
