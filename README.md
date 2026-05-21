# Azure AI Foundry + Ansible MCP

Register an **already-deployed** Ansible Automation Platform MCP server with [Azure AI Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol).

The repo is **Ansible-first**: shell scripts are thin wrappers around `ansible-playbook`.

## Quick start

```bash
cp group_vars/all.yml.example group_vars/all.yml
# Edit: aap_password, foundry_project_endpoint (or foundry_account + foundry_project)

az login
ansible-playbook playbooks/site.yml
```

Workshop Foundry project endpoint (example):

`https://foundry-wg2cd-1.services.ai.azure.com/api/projects/foundry-wg2cd-1-project`

## Playbooks

| Playbook | Purpose |
|----------|---------|
| [`playbooks/site.yml`](playbooks/site.yml) | Full registration: Gateway token, MCP verify, ARM connection, agent |
| [`playbooks/verify.yml`](playbooks/verify.yml) | AAP API + MCP Bearer + optional OpenShift MCP routes |
| [`playbooks/cleanup-foundry.yml`](playbooks/cleanup-foundry.yml) | Delete agents, connection, optional extra projects |
| [`playbooks/redeploy.yml`](playbooks/redeploy.yml) | Cleanup then `site.yml` |
| [`playbooks/update-agent-instructions.yml`](playbooks/update-agent-instructions.yml) | Azure alert → template recommendation prompt (agent v2+) |
| [`playbooks/create-gateway-token.yml`](playbooks/create-gateway-token.yml) | Mint AAP Gateway token; print `Bearer …` for portal |
| [`playbooks/list-job-templates.yml`](playbooks/list-job-templates.yml) | Controller API job templates |
| [`playbooks/list-recent-jobs.yml`](playbooks/list-recent-jobs.yml) | Recent unified jobs |
| [`playbooks/launch-job-template.yml`](playbooks/launch-job-template.yml) | Launch template by ID |
| [`playbooks/mcp-list-job-templates.yml`](playbooks/mcp-list-job-templates.yml) | Templates via MCP |
| [`playbooks/openshift-mcp-routes.yml`](playbooks/openshift-mcp-routes.yml) | `oc` MCP CRs and routes |
| [`playbooks/install-local-tools.yml`](playbooks/install-local-tools.yml) | Install `oc` to `~/bin` |

### Tags (`site.yml`)

| Tag | Action |
|-----|--------|
| `foundry_verify_mcp` | MCP initialize + `tools/list` only |
| `foundry_connection` | ARM CustomKeys connection |
| `foundry_agent` | Create agent with MCP tool |
| `foundry_gateway_token` | Create Gateway Bearer token only |

## Copilot: Azure alert → job template

| File | Purpose |
|------|---------|
| [`config/azure_alert_template_map.yml`](config/azure_alert_template_map.yml) | Keyword → template hints |
| [`examples/azure-alert-mcp-404.json`](examples/azure-alert-mcp-404.json) | Sample alert for Playground |

```bash
ansible-playbook playbooks/update-agent-instructions.yml
```

## Shell wrappers (optional)

Scripts in `scripts/` call the playbooks above, for example:

```bash
./scripts/verify-lab-from-bastion.sh
./scripts/register-foundry.sh
./scripts/create-aap-gateway-token.sh
```

`scripts/workshop-env.sh` still sets `NO_PROXY` for workshop hosts (not Ansible).

## Roles

| Role | Purpose |
|------|---------|
| `foundry_mcp_agent` | Gateway token, MCP verify, ARM connection, agent, cleanup |
| `aap_workshop_verify` | Lab health checks |
| `aap_controller` | List/launch job templates |
| `local_tools` | Install `oc` locally |

## Foundry portal (required for MCP auth)

ARM cannot persist connection secrets. After `site.yml`:

1. [https://ai.azure.com](https://ai.azure.com) → project → **Connected resources** → `aap-mcp-bearer`
2. **Custom keys** → name **`Authorization`** → value **`Bearer <token>`** from `create-gateway-token.yml`
3. **Agents** → MCP URL: `{{ aap_mcp_base_url }}/mcp`

See [`scripts/FIX-FOUNDRY-MCP-404.md`](scripts/FIX-FOUNDRY-MCP-404.md).

## Variables

See [`group_vars/all.yml.example`](group_vars/all.yml.example).

## Security

Do not commit `creds.md`, `.env`, or `group_vars/all.yml`.

## References

- [Connect agents to MCP servers (Foundry)](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)
- [MCP server authentication (Foundry)](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication)
