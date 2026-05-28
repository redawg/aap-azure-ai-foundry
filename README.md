# AAP MCP + Microsoft Copilot Studio

Register an **already-deployed** [Ansible Automation Platform MCP](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/containerized_installation/deploying-ansible-mcp-server) server with **Microsoft Copilot Studio** (primary).

**Legacy:** [Azure AI Foundry](docs/LEGACY-FOUNDRY.md) registration remains available via `playbooks/foundry-site.yml`.

## Quick start (Copilot Studio)

```bash
cp group_vars/all.yml.example group_vars/all.yml
# Edit: aap_mcp_base_url, aap_user, aap_password

./scripts/setup-copilot.sh
# or:
ansible-playbook playbooks/site.yml
```

### Setup modes (`copilot_setup_mode`)

| Mode | What runs |
|------|-----------|
| `wizard` | MCP health check + `copilot-setup-artifacts/MCP-SETUP-WIZARD.md` |
| `connector` | OpenAPI + Power Platform custom connector artifacts/API |
| `both` | Wizard + connector (default) |

### Tags

| Tag | Action |
|-----|--------|
| `verify_mcp` | Probe unified `/mcp` and toolset endpoints |
| `copilot_openapi` | Regenerate `aap-mcp-openapi.yaml` (6 toolsets + `/mcp`) |
| `copilot_wizard` | MCP onboarding wizard guide |
| `copilot_artifacts` | Manual custom connector artifacts |
| `copilot_connector` | Power Platform API automation |

## Prerequisites

- AAP MCP server URL and admin credentials (Basic auth)
- [Copilot Studio](https://copilotstudio.microsoft.com) — **generative orchestration** enabled on your agent
- Valid HTTPS certificate on MCP (required by Power Platform)
- For connector automation: `az login` and Power Platform permissions

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | Copilot Studio runbook |
| [docs/COPILOT-STUDIO-SETUP.md](docs/COPILOT-STUDIO-SETUP.md) | UI setup (wizard + custom connector) |
| [COPILOT-SETUP-QUICK-REF.md](COPILOT-SETUP-QUICK-REF.md) | Quick reference |
| [playbooks/README-COPILOT-PLAYBOOKS.md](playbooks/README-COPILOT-PLAYBOOKS.md) | Playbook details |
| [docs/LEGACY-FOUNDRY.md](docs/LEGACY-FOUNDRY.md) | Azure AI Foundry (optional) |

## Architecture

```
AAP MCP (HTTPS, Basic auth)
    ├── Copilot Studio MCP wizard (recommended)
    └── Power Platform custom connector (OpenAPI, streamable MCP)
            └── Copilot Studio agent tools
```

OpenAPI is generated from [`roles/copilot_mcp/templates/aap-mcp-openapi.yaml.j2`](roles/copilot_mcp/templates/aap-mcp-openapi.yaml.j2) aligned with [ansible-tmm/mcp-demo](https://github.com/ansible-tmm/mcp-demo/tree/main/copilotstudio-mcp-setup).

## Variables

See [`group_vars/all.yml.example`](group_vars/all.yml.example).

## Security

Do not commit `creds.md`, `.env`, or `group_vars/all.yml`.

## References

- [Copilot Studio — connect MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)
- [Copilot Studio — extend agent with MCP](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp)
- [Red Hat AAP MCP server](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/containerized_installation/deploying-ansible-mcp-server)
