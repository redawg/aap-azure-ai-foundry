# Session export — Azure AI Foundry + AAP MCP

**Date:** May 18–19, 2026  
**Workspace:** `/Users/cferman/azure-aap-mcp`  
**GitHub:** https://github.com/chadmf/aap-azure-ai-foundry

This document summarizes work done in the Cursor session that built this repository.

---

## 1. Original goal

Configure **Azure AI Foundry** so agents can use the **Ansible Automation Platform (AAP) MCP server**, using credentials and URLs from a local `creds.md` file (workshop/lab environment).

---

## 2. What was discovered (workshop cluster)

| Item | Value |
|------|--------|
| AAP gateway | `https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io` |
| OpenShift API | `https://api.cluster-wg2cd-2.dynamic2.redhatworkshops.io:6443` |
| AAP operator | `aap` namespace, AAP 2.6 |
| MCP operator CRD | `ansiblemcpservers.mcpserver.ansible.com` (present) |
| MCP initially | **Not deployed** (no `AnsibleMCPServer` CR, no MCP routes) |

**MCP auth behavior (important):**

- **HTTP Basic** (`admin` + password) works against `/mcp`.
- **OAuth2 bearer tokens** from Controller API (`/api/controller/v2/tokens/`) return **401** from the MCP server validator.
- Foundry project connections must use `Authorization: Basic <base64(user:pass)>`.

---

## 3. Evolution of the repository

### Phase A — Full stack (later removed)

Initially the repo included **OpenShift MCP deployment**:

- `manifests/ansible-mcp-server.yaml`
- `scripts/deploy-mcp-openshift.sh`
- `roles/aap_mcp_openshift/`
- `playbooks/deploy-mcp-openshift.yml`
- `collections/requirements.yml` (`kubernetes.core`)

An `AnsibleMCPServer` CR was applied to the workshop cluster:

- Route: `https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io`
- Unified endpoint: `.../mcp`
- Per-toolset paths: `.../job_management/mcp`, etc.

### Phase B — Foundry-only (current scope)

Per your request, **all AAP/OpenShift MCP install automation was removed**. The repo now assumes **MCP is already running on AAP**. It only:

1. Verifies MCP (optional)
2. Registers a Foundry **project connection** (CustomKeys)
3. Creates a Foundry **agent** with an **MCP tool**

### Phase C — Playbook consolidation

Multiple playbooks were merged into a single entry point:

- **`playbooks/site.yml`** (only playbook)

Removed: `configure-mcp-azure-foundry.yml`, `configure-foundry.yml`, `verify-mcp.yml`, `deploy-mcp-openshift.yml`.

### Phase D — Security & GitHub

- Added `creds.md` to `.gitignore`
- Scanned tracked files — no secrets in committed content
- Created public repo **`aap-azure-ai-foundry`** and pushed `main`
- Default Foundry model changed from `gpt-4.1-mini` → **`claude-sonnet-4-5`**

---

## 4. Git history

| Commit | Message |
|--------|---------|
| `193db10` | Initial commit: Ansible playbooks for Azure AI Foundry MCP integration |
| `d4cd7e5` | Use Claude Sonnet 4.5 as the default Foundry model deployment |

**Never committed (gitignored):** `creds.md`, `group_vars/all.yml`, `.env`

---

## 5. Final repository layout

```
aap-azure-ai-foundry/
├── ansible.cfg
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt          # Python SDK optional script
├── docs/
│   └── SESSION-EXPORT.md     # this file
├── group_vars/
│   └── all.yml.example
├── inventory/
│   └── hosts.yml             # localhost / foundry group
├── playbooks/
│   └── site.yml              # single playbook
├── roles/
│   └── foundry_mcp_agent/
│       ├── defaults/main.yml
│       └── tasks/
│           ├── main.yml
│           ├── validate.yml
│           ├── verify-mcp.yml
│           ├── authenticate.yml
│           ├── register-connection.yml
│           └── register-agent.yml
└── scripts/
    ├── configure-foundry-rest.sh
    └── configure-foundry-agent.py
```

---

## 6. Ansible playbook flow (`playbooks/site.yml`)

**Role:** `foundry_mcp_agent`

| Step | Task file | Purpose |
|------|-----------|---------|
| 1 | `validate.yml` | Check required vars |
| 2 | `main.yml` | Build `Basic` auth header |
| 3 | `verify-mcp.yml` | POST MCP `initialize` (tag: `foundry_verify_mcp`) |
| 4 | `authenticate.yml` | `az account get-access-token` for Foundry API |
| 5 | `register-connection.yml` | PUT CustomKeys connection (tag: `foundry_connection`) |
| 6 | `register-agent.yml` | POST agent with MCP tool (tag: `foundry_agent`) |

**Tags:** `foundry_mcp_agent` (all), `foundry_verify_mcp`, `foundry_connection`, `foundry_agent`

---

## 7. Key variables (`group_vars/all.yml.example`)

| Variable | Purpose |
|----------|---------|
| `aap_mcp_base_url` | Existing MCP host (no path) |
| `aap_user` / `aap_password` | MCP Basic auth |
| `foundry_project_endpoint` | Foundry project API URL |
| `foundry_model_deployment_name` | **`claude-sonnet-4-5`** (must match portal deployment name) |
| `foundry_mcp_connection_name` | e.g. `aap-mcp-bearer` |
| `foundry_agent_name` | e.g. `aap-automation-agent` |
| `foundry_mcp_server_label` | e.g. `ansible-aap` |
| `foundry_verify_mcp_before_register` | Probe MCP before Foundry API calls |
| `foundry_register_agent` | Create agent (false = connection only) |

---

## 8. Foundry API actions (what automation does)

### Project connection (PUT)

```
{foundry_project_endpoint}/connections/{foundry_mcp_connection_name}?api-version=2025-05-01-preview
```

Body type `CustomKeys`, key `Authorization` = `Basic <base64(admin:password)>`.

### Agent (POST)

```
{foundry_project_endpoint}/agents?api-version=v1
```

Agent definition includes MCP tool:

- `server_url`: `{aap_mcp_base_url}/mcp`
- `project_connection_id`: connection name
- `require_approval`: `always`
- `model`: `claude-sonnet-4-5`

---

## 9. How to run (current)

```bash
cd /Users/cferman/azure-aap-mcp
cp group_vars/all.yml.example group_vars/all.yml
# Edit: aap_mcp_base_url, aap_password, foundry_project_endpoint

az login
ansible-playbook playbooks/site.yml
```

Optional shell/Python alternatives:

```bash
cp .env.example .env   # fill values
./scripts/configure-foundry-rest.sh
# or: python scripts/configure-foundry-agent.py
```

---

## 10. Manual Foundry portal steps (equivalent)

1. https://ai.azure.com → project → **Connections** → **Custom keys**
   - Key: `Authorization`
   - Value: `Basic ` + base64(`admin:PASSWORD`)
2. **Agents** → add **MCP** tool
   - URL: `https://<mcp-host>/mcp`
   - Connection: your connection name
   - Model: Claude Sonnet 4.5 deployment
3. Test in **Playground**; approve MCP tool calls when prompted.

---

## 11. MCP endpoints (workshop, when deployed)

| Endpoint | Path |
|----------|------|
| Unified | `/mcp` |
| Job management | `/job_management/mcp` |
| Inventory | `/inventory_management/mcp` |
| Monitoring | `/system_monitoring/mcp` |
| Users | `/user_management/mcp` |
| Security | `/security_compliance/mcp` |
| Platform config | `/platform_configuration/mcp` |

---

## 12. Files removed during session (not in final repo)

- `manifests/ansible-mcp-server.yaml`
- `scripts/deploy-mcp-openshift.sh`
- `roles/aap_mcp_openshift/` (entire role)
- `playbooks/deploy-mcp-openshift.yml`
- `playbooks/configure-mcp-azure-foundry.yml`
- `playbooks/configure-foundry.yml`
- `playbooks/verify-mcp.yml` (logic → role + tags)
- `collections/requirements.yml`
- `playbooks/site.yml` (old version that imported deploy playbook)

---

## 13. References

- [Connect agents to MCP servers (Foundry)](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)
- [MCP server authentication (Foundry)](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication)
- [Deploy Claude models in Foundry](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-claude)
- [AAP MCP on OpenShift 2.6](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/html/installing_on_openshift_container_platform/deploy-ansible-mcp-server-operator-install)

---

## 14. Local-only artifacts

- **`creds.md`** — workshop passwords, AWS/Azure keys, OpenShift token (gitignored; keep local only)
- **`group_vars/all.yml`** — your filled-in vars (gitignored)
- **`.env`** — shell/Python script env (gitignored)

If `creds.md` was ever committed elsewhere, rotate all credentials in that file.
