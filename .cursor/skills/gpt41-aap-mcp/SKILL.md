---
name: gpt41-aap-mcp
description: >-
  Operate the workshop Azure AI Foundry agent (gpt-4.1) with Ansible Automation
  Platform MCP tools. Use when the user mentions Foundry Playground, gpt-4.1,
  aap-automation-agent, AAP MCP, job templates, Azure Monitor alerts, Gateway
  Bearer tokens, or aap-mcp-bearer connection issues.
---

# gpt-4.1 + AAP MCP

**Foundry agent instructions** live in [`config/foundry_agent_aap_mcp_skill.md`](../../config/foundry_agent_aap_mcp_skill.md) and are published via `scripts/foundry_instructions.py` → `playbooks/update-agent-instructions.yml`. Edit that file to change what **gpt-4.1** sees in Playground.

## Foundry agent (Playground)

| Setting | Value |
|---------|--------|
| Project | `foundry-wg2cd-1-project` |
| Agent | `aap-automation-agent` |
| Model | `gpt-4.1` (use latest version, e.g. v22+) |
| MCP URL | `https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp` |
| Connection | `aap-mcp-bearer` — Custom key **`Authorization`** = `Bearer <gateway-token>` |
| Target | `_` (not the MCP URL) |

Foundry calls `tools/list` on connect, then invokes tools (e.g. `job_templates_list`) during the chat.

### Portal troubleshooting

- **404 Session not found** / **500 on enumerate** → refresh Bearer token; see [scripts/FIX-FOUNDRY-MCP-404.md](../../scripts/FIX-FOUNDRY-MCP-404.md)
- **`mcpr_…` approval** → approve in UI, or use agent version with `require_approval: never`
- **Wrong header** → key name must be `Authorization`, not `Value`

Mint token:

```bash
source scripts/workshop-env.sh
ansible-playbook playbooks/create-gateway-token.yml -e @group_vars/all.yml -e aap_gateway_token=
```

Register / refresh agent:

```bash
ansible-playbook playbooks/site.yml -e @group_vars/all.yml
ansible-playbook playbooks/update-agent-instructions.yml -e @group_vars/all.yml
```

## Primary workflow: Azure alert → AAP job template

When the user provides an alert JSON or describes a fired alert:

1. Parse `essentials` / `alertContext.properties` (rule, severity, resource, error text).
2. Use MCP **`job_templates_list`** (live data from Controller).
3. Match using hints in [config/azure_alert_template_map.yml](../../config/azure_alert_template_map.yml) **and** template names from AAP.
4. Respond with template **ID**, **name**, confidence, remediation summary.
5. Offer **`job_templates_launch_create`** only after explicit user approval.

Sample payloads: [examples/](../../examples/) — see [examples/AGENT-ALERT-PROMPTS.md](../../examples/AGENT-ALERT-PROMPTS.md).

## Cursor / terminal MCP (this repo)

Requires `group_vars/all.yml` (from `all.yml.example`) and:

```bash
source scripts/workshop-env.sh
```

| Task | Command |
|------|---------|
| Verify MCP | `python3 scripts/aap_mcp_or_navigator.py list-job-templates` |
| List recent jobs | `ansible-playbook playbooks/list-recent-jobs.yml -e @group_vars/all.yml` |
| MCP + playbook fallback | `scripts/aap-ask.sh list-job-templates` |

MCP client: [scripts/aap_mcp_client.py](../../scripts/aap_mcp_client.py) — Bearer session, SSE, `tools/call`.

### High-value MCP tools

| Tool | Use |
|------|-----|
| `job_templates_list` | List job templates (alert copilot) |
| `job_templates_retrieve` | Details for one template |
| `jobs_list` | Recent unified jobs |
| `projects_list` | Controller projects |
| `job_templates_launch_create` | Launch job — **confirm with user first** |

Unified `/mcp` exposes ~100+ tools across toolsets; `/job_management/mcp` is smaller if Foundry returns 500 on full list.

## Do not

- Commit `group_vars/all.yml` or paste Gateway tokens into git.
- Launch jobs or change AAP state without user confirmation.
- Use MCP key name `Value` in Foundry connection.

## More detail

- MCP tool patterns and endpoints: [reference.md](reference.md)
