# Runbook — lab environment + Azure AI Foundry

How to run `playbooks/site.yml` against the Red Hat workshop cluster (values in local `creds.md`) and register MCP in Azure AI Foundry.

---

## 1. What you are running

| Step | Requires | What it does |
|------|----------|--------------|
| MCP verify (optional) | Lab AAP password | POST `initialize` to `{aap_mcp_base_url}/mcp` with HTTP Basic |
| Foundry auth | `az login` or `foundry_agent_token` | Bearer token for Foundry REST API |
| Project connection | Foundry endpoint + token | Stores `Authorization: Basic …` in Foundry |
| Agent + MCP tool | Model deployment in Foundry | Creates agent using `claude-sonnet-4-5` |

**This repo does not deploy MCP on OpenShift.** MCP must already be reachable at your `aap_mcp_base_url`.

---

## 2. Prerequisites

### On your machine

| Tool | Purpose | Install (macOS) |
|------|---------|-----------------|
| **Ansible** | Run `playbooks/site.yml` | `pip3 install --user ansible` then add `~/Library/Python/3.9/bin` to `PATH` |
| **Azure CLI** | `az account get-access-token` for Foundry API | `brew install azure-cli` |
| **curl** | Quick MCP checks (optional) | Preinstalled |

Optional Python path (shell script alternative):

```bash
pip3 install -r requirements.txt   # azure-ai-projects, azure-identity, python-dotenv
```

### In Azure (Foundry)

- An **Azure AI Foundry** project in a subscription you can access with `az login`
- A deployed model named **`claude-sonnet-4-5`** (or change `foundry_model_deployment_name` to match your deployment name in the portal)
- **Foundry project endpoint** URL (see §4) — not included in `creds.md`

### On the lab (from `creds.md`)

| Item | Where in creds.md | Used as |
|------|-------------------|---------|
| AAP admin password | §1 Automation Controller | `aap_password` |
| MCP / AAP URL | §1 Controller URL + MCP route | `aap_mcp_base_url` |
| Azure subscription ID | §3 | Discover Foundry resources (optional) |
| Azure client ID + password | §3 | Service principal (workshop); see §5 |
| OpenShift token | §6 | Not used by this playbook |

---

## 3. Configure variables

```bash
cd /path/to/azure-aap-mcp
cp group_vars/all.yml.example group_vars/all.yml
```

Edit `group_vars/all.yml` (gitignored):

```yaml
# Lab MCP (workshop example hostnames)
aap_mcp_base_url: https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io
aap_user: admin
aap_password: "<from creds.md §1>"

# Foundry — required for full playbook (not in creds.md)
foundry_project_endpoint: "https://<resource>.services.ai.azure.com/api/projects/<project>"
foundry_model_deployment_name: claude-sonnet-4-5
```

Copy `creds.md` values only into local files; never commit `creds.md` or `group_vars/all.yml`.

---

## 4. Find your Foundry project endpoint

`creds.md` does **not** include the Foundry project URL. Get it from the portal or CLI after Azure login:

**Portal:** [https://ai.azure.com](https://ai.azure.com) → your project → **Overview** → **Project endpoint**  
Format: `https://<ai-services-resource>.services.ai.azure.com/api/projects/<project-name>`

**CLI (after `az login` to the correct subscription):**

```bash
az account set --subscription "<subscription-id-from-creds.md>"
az cognitiveservices account list -o table
# Then use portal or REST to list projects under your AI Services account
```

Optional helper (untracked in repo):

```bash
chmod +x scripts/discover-foundry-endpoint.sh
./scripts/discover-foundry-endpoint.sh
```

---

## 5. Azure authentication

The playbook role calls:

```bash
az account get-access-token --scope https://ai.azure.com/.default
```

### Option A — Your own Azure account (recommended if you have Foundry)

```bash
export PATH="/opt/homebrew/bin:$HOME/Library/Python/3.9/bin:$PATH"
az login
az account set --subscription "9dc2c3d2-35a8-4370-8997-b56a57b5778d"   # lab sub from creds.md, if you have access
az account show
```

**Note:** Logging in as `*@redhat.com` may show **no access** to the lab subscription. You need a login that can reach the subscription where your Foundry project lives.

### Option B — Workshop service principal (creds.md §3)

| Field | creds.md |
|-------|----------|
| Client ID | Azure Client ID |
| Secret | Azure Password |
| Subscription | Azure Subscription ID |

SP login requires the **tenant ID** (not listed in `creds.md`):

```bash
az login --service-principal \
  -u "<Azure Client ID>" \
  -p "<Azure Password>" \
  --tenant "<tenant-id>"
az account set --subscription "<Azure Subscription ID>"
```

Without the correct tenant, SP login fails with `unauthorized_client` or `Application … was not found in the directory`.

### Option C — Pre-set token (CI / automation)

```yaml
foundry_agent_token: "<bearer token with https://ai.azure.com/.default scope>"
```

---

## 6. MCP authentication (lab)

The AAP MCP server expects **HTTP Basic**, not a Controller OAuth2 bearer token.

| Method | Works with MCP? |
|--------|-----------------|
| `Authorization: Basic base64(admin:password)` | Yes |
| Bearer token from `/api/controller/v2/tokens/` | No (401 from MCP validator) |

The playbook builds Basic auth automatically from `aap_user` and `aap_password`.

**Quick manual check:**

```bash
AUTH=$(echo -n 'admin:YOUR_PASSWORD' | base64)
curl -sk \
  -H "Authorization: Basic ${AUTH}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  "https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp"
```

Expect HTTP **200** and an `Mcp-Session-Id` response header.

---

## 7. Run the playbook

```bash
export PATH="/opt/homebrew/bin:$HOME/Library/Python/3.9/bin:$PATH"
cd /path/to/azure-aap-mcp

# Full flow: verify MCP → az token → connection → agent
ansible-playbook playbooks/site.yml
```

### Tags

```bash
# MCP lab check only (requires aap_* vars; see §8 for tag caveats)
ansible-playbook playbooks/site.yml --tags foundry_verify_mcp

# Foundry connection only
ansible-playbook playbooks/site.yml -e foundry_register_agent=false --tags foundry_connection

# Skip MCP probe
ansible-playbook playbooks/site.yml -e foundry_verify_mcp_before_register=false
```

### Shell alternative

```bash
cp .env.example .env
# Fill FOUNDRY_PROJECT_ENDPOINT, AAP_PASSWORD, etc.
az login
./scripts/configure-foundry-rest.sh
```

---

## 8. What was validated in the lab session

| Action | Result |
|--------|--------|
| MCP endpoint reachable (`/mcp`) | **OK** — HTTP 200 with lab admin Basic auth |
| `ansible-playbook … --tags foundry_verify_mcp` | **Partial** — use full playbook or curl (see below) |
| `az login` as Red Hat user | Logged in but **no subscription** for lab sub `9dc2c3d2…` |
| Workshop SP without tenant ID | **Not completed** — tenant not in `creds.md` |
| Full `site.yml` (Foundry register) | **Blocked** — needs `foundry_project_endpoint` + working `az login` to that subscription |

---

## 9. Known issues

### `--tags foundry_verify_mcp` alone

Tagged runs may skip tasks that set `aap_mcp_server_url` / `aap_mcp_auth_header` in `tasks/main.yml`, or fail the assert because Ansible’s `uri` module does not populate `content` for `text/event-stream` responses (body is empty even on success).

**Workarounds:**

- Run the **full** playbook: `ansible-playbook playbooks/site.yml`
- Or use the **curl** check in §6

### Foundry model name

`foundry_model_deployment_name` must match the **deployment name** in your Foundry project (default in repo: `claude-sonnet-4-5`).

### Agent already exists

Creating the agent returns HTTP **409** if `foundry_agent_name` already exists; use another name or update the agent in the portal.

---

## 10. Checklist before `ansible-playbook playbooks/site.yml`

- [ ] `group_vars/all.yml` created from example
- [ ] `aap_password` set from `creds.md`
- [ ] `aap_mcp_base_url` points at live MCP route
- [ ] `foundry_project_endpoint` set from [ai.azure.com](https://ai.azure.com)
- [ ] `claude-sonnet-4-5` (or your model) deployed in that Foundry project
- [ ] `az account show` succeeds for the target subscription
- [ ] `PATH` includes `ansible-playbook` and `az`
- [ ] `creds.md` / `group_vars/all.yml` not committed

---

## 11. Related docs

- [SESSION-EXPORT.md](SESSION-EXPORT.md) — full session history and repo evolution
- [README.md](../README.md) — project overview
