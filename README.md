# Azure AI Foundry + Ansible MCP

Register an **already-deployed** Ansible Automation Platform MCP server with [Azure AI Foundry Agent Service](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol).

The repo is **Ansible-first**: shell scripts are thin wrappers around `ansible-playbook` or **ansible-navigator** when MCP cannot make the change.

## Asking AAP (MCP first, Ansible fallback)

Use **`./scripts/aap-ask.sh <operation>`** to talk to the workshop AAP MCP server first. If the needed MCP tool is missing (for example `projects_create`), it automatically runs the matching playbook with **ansible-navigator** (or `ansible-playbook` if navigator is not installed).

| Command | MCP tool tried | Fallback playbook |
|---------|----------------|-------------------|
| `./scripts/aap-ask.sh list-projects` | `projects_list` | `playbooks/aap-list-projects.yml` |
| `./scripts/aap-ask.sh list-job-templates` | `job_templates_list` | `playbooks/mcp-list-job-templates.yml` |
| `./scripts/aap-ask.sh sync-github-projects` | `projects_create` | `playbooks/sync-github-projects.yml` |
| `./scripts/aap-ask.sh create-project` | `projects_create` | `playbooks/aap-create-project.yml` |
| `./scripts/aap-ask.sh launch-job-template` | `job_templates_launch_create` | `playbooks/launch-job-template.yml` |

```bash
# Requires AAP_PASSWORD or aap_gateway_token in group_vars/all.yml
./scripts/aap-ask.sh list-projects
./scripts/aap-ask.sh sync-github-projects

# Or via Ansible wrapper:
ansible-playbook playbooks/aap-ask.yml -e aap_mcp_operation=sync-github-projects
```

On the workshop cluster, MCP exposes **`projects_list`** but not **`projects_create`**, so repo sync uses the fallback playbook (Controller API via `uri`).

## Red Hat console: Galaxy + Analytics credentials

[access.redhat.com/articles/7112649](https://access.redhat.com/articles/7112649) covers **service accounts** for **Automation Analytics** and **subscriptions**. It does **not** replace the Automation Hub token used for Galaxy collection sync.

| Need | Console | Doc / playbook |
|------|---------|----------------|
| Hub / Galaxy API token | [automation-hub/token](https://console.redhat.com/ansible/automation-hub/token) | [`docs/REDHAT-CONSOLE-CREDENTIALS.md`](docs/REDHAT-CONSOLE-CREDENTIALS.md), [`playbooks/aap-redhat-galaxy-credential.yml`](playbooks/aap-redhat-galaxy-credential.yml) |
| Analytics service account | [iam/service-accounts](https://console.redhat.com/iam/service-accounts) | Same doc, [`playbooks/aap-redhat-analytics-service-account.yml`](playbooks/aap-redhat-analytics-service-account.yml) |

## Cursor skill

| Artifact | Purpose |
|----------|---------|
| [`config/foundry_agent_aap_mcp_skill.md`](config/foundry_agent_aap_mcp_skill.md) | **Foundry gpt-4.1 agent** system instructions (AAP MCP tool usage) |
| [`.cursor/skills/gpt41-aap-mcp/`](.cursor/skills/gpt41-aap-mcp/SKILL.md) | **Cursor IDE** skill (same workflow + repo commands) |

Publish skill to Foundry: `ansible-playbook playbooks/update-agent-instructions.yml -e @group_vars/all.yml`

## Quick start

```bash
cp group_vars/all.yml.example group_vars/all.yml
# Edit: aap_password, foundry_project_endpoint (or foundry_account + foundry_project)

pip install -r requirements.txt
ansible-galaxy collection install -r collections/requirements.yml -p collections

az login
ansible-playbook playbooks/site.yml
```

**Dependencies:** Python tools use [`requirements.txt`](requirements.txt). Ansible playbooks need [`collections/requirements.yml`](collections/requirements.yml) (`ansible.netcommon`, `azure.azcollection`, `community.general`). The Function App under `roles/azure_fedora_foundry_alerts/files/function_bridge/` has its own [`requirements.txt`](roles/azure_fedora_foundry_alerts/files/function_bridge/requirements.txt) for Azure deployment.

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
| [`playbooks/provision-aap-analytics.yml`](playbooks/provision-aap-analytics.yml) | AAP 2.6 MetricsService + controller metrics-utility on OpenShift |
| [`playbooks/aap-ask.yml`](playbooks/aap-ask.yml) | MCP-first operations with ansible-navigator fallback |
| [`playbooks/sync-github-projects.yml`](playbooks/sync-github-projects.yml) | Fallback: sync `redawg/*` GitHub repos to Controller projects (API) |
| [`playbooks/aap-list-projects.yml`](playbooks/aap-list-projects.yml) | Fallback: list Controller projects (API) |
| [`playbooks/aap-create-project.yml`](playbooks/aap-create-project.yml) | Fallback: create one project (API) |
| [`playbooks/install-local-tools.yml`](playbooks/install-local-tools.yml) | Install `oc` to `~/bin` |
| [`playbooks/azure-fedora-alerts.yml`](playbooks/azure-fedora-alerts.yml) | Fedora VM on Azure + Monitor alerts → Foundry copilot agent |
| [`playbooks/aap-create-azure-fedora-template.yml`](playbooks/aap-create-azure-fedora-template.yml) | Create AAP job template for `azure-fedora-alerts.yml` |

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
| [`examples/AGENT-ALERT-PROMPTS.md`](examples/AGENT-ALERT-PROMPTS.md) | Copy-paste Playground prompts + optional live alert |
| [`examples/azure-alert-mcp-404.json`](examples/azure-alert-mcp-404.json) | MCP tools/list / Bearer auth failure |
| [`examples/azure-alert-vm-cpu-high.json`](examples/azure-alert-vm-cpu-high.json) | Metric alert: VM CPU high |
| [`examples/azure-alert-rhel-deploy-failed.json`](examples/azure-alert-rhel-deploy-failed.json) | Activity-style: RHEL BYOS deploy failed |
| [`examples/azure-alert-cisco-snmp-updated.json`](examples/azure-alert-cisco-snmp-updated.json) | Log alert: Cisco SNMP configuration changed |

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

## Azure Fedora VM → Foundry alerts

Deploy a **Fedora Linux VM**, an **Azure Monitor** metric alert (CPU), and a **Function App** that forwards the alert payload to your **Foundry agent** (`aap-automation-agent`) via the Responses API.

```bash
ansible-galaxy collection install -r collections/requirements.yml
az login
ansible-playbook playbooks/site.yml          # register agent first
ansible-playbook playbooks/azure-fedora-alerts.yml
# optional end-to-end webhook test:
ansible-playbook playbooks/azure-fedora-alerts.yml -e azure_fedora_test_foundry_invoke=true
```

**AAP job template** (Controller UI launch):

```bash
ansible-playbook playbooks/aap-create-azure-fedora-template.yml -e @group_vars/all.yml
# or: ./scripts/aap-create-azure-fedora-template.sh
```

Creates template **Azure VM + Foundry Alerts** on project `aap-azure-ai-foundry`, playbook `playbooks/azure-fedora-alerts.yml`, inventory `foundry-local` (localhost). Default extra vars: [`config/azure_fedora_job_template_extra_vars.yml`](config/azure_fedora_job_template_extra_vars.yml).

Flow: **Metric alert** → **Action group webhook** → **Function `AlertToFoundry`** → **Foundry agent** (recommends AAP job template from alert JSON).

If the Fedora image URN fails in your region, list images with `az vm image list -p FedoraLinux -l <location> -o table` and set `azure_fedora_vm_image`.

## Roles

| Role | Purpose |
|------|---------|
| `foundry_mcp_agent` | Gateway token, MCP verify, ARM connection, agent, cleanup |
| `aap_workshop_verify` | Lab health checks |
| `aap_controller` | List/launch job templates |
| `local_tools` | Install `oc` locally |
| `azure_fedora_foundry_alerts` | Fedora VM, Function alert bridge, Monitor → Foundry |

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
