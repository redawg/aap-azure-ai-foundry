# AAP MCP — reference for AI models

This document is the **canonical reference** for AI assistants (Azure AI Foundry agents, Cursor, Claude, GPT, etc.) that need to call the **Ansible Automation Platform (AAP) Model Context Protocol (MCP)** server on the Red Hat workshop cluster.

**Read this before** invoking MCP tools or advising users on Foundry connection setup.

---

## 1. What this server is

| Item | Value |
|------|--------|
| Product | Ansible Automation Platform 2.x (Controller + Gateway MCP) |
| Protocol | [Model Context Protocol](https://modelcontextprotocol.io/) (JSON-RPC 2.0 over HTTP) |
| Transport | HTTP POST; responses often **Server-Sent Events** (`text/event-stream`) |
| Server name | `aap` (version `0.1.0` in `initialize` result) |
| Primary URL | `https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp` |
| Controller API | `https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/api/controller/v2/` |

The MCP server exposes **Controller operations as tools** (list job templates, launch jobs, list projects, inventories, etc.). It does **not** execute Ansible playbooks directly; it proxies to the Controller REST API.

---

## 2. Authentication (required)

### 2.1 Gateway Bearer token (correct method)

MCP **requires** an AAP **Gateway API token** in the HTTP header:

```http
Authorization: Bearer <gateway-token>
```

- Mint tokens with Controller admin credentials: `POST /api/gateway/v1/tokens/` (Basic auth).
- **Do not** use only `Authorization: Basic …` for `tools/list` — you may get HTTP 404 `"Session not found"`.
- Token is a single opaque string (no spaces). Prefix with exactly one `Bearer ` and one space in the header value.

**Example mint (human or script):**

```bash
curl -sk -u 'admin:<password>' \
  -X POST 'https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/api/gateway/v1/tokens/' \
  -H 'Content-Type: application/json' \
  -d '{"description":"mcp-client","application":"","scope":"write"}'
```

Response JSON field: `token`.

### 2.2 Azure AI Foundry connection

| Field | Value |
|--------|--------|
| Connection name | `aap-mcp-bearer` |
| Auth type | **Custom keys** (not “API key” with MCP URL as target) |
| Target | `_` or blank — **not** the full `/mcp` URL |
| Custom key **name** | `Authorization` |
| Custom key **value** | `Bearer <gateway-token>` |

**Wrong:** key name `Value` → Foundry error `Failed to add header 'Value:'`.

### 2.3 Secrets

- Never commit tokens or `group_vars/all.yml` to git.
- Rotate tokens if leaked; revoke under AAP **Administration → Tokens**.

---

## 3. HTTP requirements

Every MCP POST must include:

```http
Content-Type: application/json
Accept: application/json, text/event-stream
Authorization: Bearer <gateway-token>
```

For all requests **after** `initialize`, also send:

```http
Mcp-Session-Id: <session-uuid>
```

The session ID is returned in the **`Mcp-Session-Id`** response header (or `mcp-session-id`) from a successful `initialize` with Bearer auth.

Missing `Accept: application/json, text/event-stream` → HTTP **406** Not Acceptable.

---

## 4. Session workflow

```text
1. POST initialize     (Bearer; no session header yet)
   ← 200 + Mcp-Session-Id header + SSE body with serverInfo

2. POST tools/list     (Bearer + Mcp-Session-Id)
   ← 200 + SSE body with tools[] array

3. POST tools/call     (Bearer + Mcp-Session-Id)
   ← 200 + SSE body with tool result (often JSON in content[].text)
```

Optional: `notifications/initialized` after `initialize` (some clients send it; server may ignore errors).

---

## 5. JSON-RPC message formats

### 5.1 initialize

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": { "name": "your-client", "version": "1.0" }
  }
}
```

### 5.2 tools/list

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### 5.3 tools/call

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "job_templates_list",
    "arguments": {}
  }
}
```

Use the **exact** tool `name` from `tools/list` (snake_case, e.g. `job_templates_list` — not `controller.job_templates_list`).

---

## 6. Parsing SSE responses

Bodies are often **not** plain JSON documents. Typical format:

```text
event: message
data: {"result":{"protocolVersion":"2024-11-05","capabilities":{},"serverInfo":{"name":"aap","version":"0.1.0"}},"jsonrpc":"2.0","id":1}
```

**Algorithm for AI clients:**

1. Read response body as text.
2. For each line starting with `data:`, parse the remainder as JSON.
3. Use the last (or matching `id`) message’s `result` or `error`.

`tools/list` result shape:

```json
{
  "result": {
    "tools": [
      {
        "name": "job_templates_list",
        "description": "...",
        "inputSchema": { "type": "object", "properties": { ... } }
      }
    ]
  }
}
```

`tools/call` result often includes:

```json
{
  "result": {
    "content": [
      { "type": "text", "text": "{ \"count\": 5, \"results\": [ ... ] }" }
    ]
  }
}
```

Parse the inner `text` string as JSON for Controller API-shaped payloads.

---

## 7. MCP base URLs (toolsets)

| URL path | Approx. tools | Use when |
|----------|---------------|----------|
| `/mcp` | ~100+ | Full platform access; may be large for some AI hosts |
| `/job_management/mcp` | ~25 | Job templates, jobs, activations |
| `/inventory_management/mcp` | ~8 | Inventories, hosts |

Workshop Foundry agent **aap-automation-agent** is typically configured with **`/mcp`**.

If an AI host returns **HTTP 500** on tool enumeration with `/mcp`, retry registration with `/job_management/mcp` (see [scripts/FIX-FOUNDRY-MCP-404.md](../scripts/FIX-FOUNDRY-MCP-404.md)).

---

## 8. High-value tools (by intent)

Always call **`tools/list`** first on your configured URL to see the live catalog. Common tools:

| Intent | Tool name(s) | Notes |
|--------|----------------|-------|
| List job templates | `job_templates_list` | Primary tool for alert → template workflows |
| Get one template | `job_templates_retrieve` | Pass template `id` in arguments |
| Launch a job | `job_templates_launch_create` | **Writes** — require human approval |
| List recent jobs | `jobs_list` | Filter/pagination per `inputSchema` |
| Get job details | `jobs_retrieve` | |
| List projects | `projects_list` | SCM projects on Controller |
| List inventories | `inventories_list` | |
| Controller status | `status_retrieve`, `config_retrieve` | |
| Instances / hosts | `instances_retrieve` | |

Tool names and schemas are defined by the AAP MCP server; **do not invent** tool names.

---

## 9. Errors and fixes

| HTTP / JSON-RPC | Meaning | Action |
|-----------------|--------|--------|
| 404 `"Session not found"` | Missing/invalid Bearer or missing `Mcp-Session-Id` | Mint token; re-run `initialize`; pass session on follow-up calls |
| 406 Not Acceptable | Missing SSE Accept header | Add `Accept: application/json, text/event-stream` |
| 400 parse/auth | `Bearer Bearer …` or bad token | Single `Bearer ` prefix; mint new token |
| 500 (Foundry only) | Host timeout or huge `tools/list` | Use `/job_management/mcp`; refresh portal secret |
| `-32603` Unknown tool | Wrong tool name | Re-read `tools/list` |

---

## 10. Azure AI Foundry agent (workshop)

| Setting | Value |
|---------|--------|
| Project | `foundry-wg2cd-1-project` |
| Agent | `aap-automation-agent` |
| Model deployment | `gpt-4.1` |
| MCP tool URL | `https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp` |
| Connection | `aap-mcp-bearer` |

**Agent behavior instructions** (embedded in Foundry): [config/foundry_agent_aap_mcp_skill.md](../config/foundry_agent_aap_mcp_skill.md)  
**Alert → template hints:** [config/azure_alert_template_map.yml](../config/azure_alert_template_map.yml)

**Sample alert payloads:** [examples/](../examples/)

Foundry may use `require_approval: never` (auto-run tools) or `always` / selective — check the active agent version in Playground.

---

## 11. Verify connectivity (terminal)

From repo root with `group_vars/all.yml`:

```bash
source scripts/workshop-env.sh
export AAP_GATEWAY_TOKEN='<token>'   # optional if password in group_vars
python3 scripts/aap_mcp_or_navigator.py list-job-templates
```

Expected: `Completed via AAP MCP.` and a list of job templates.

```bash
ansible-playbook playbooks/site.yml -e @group_vars/all.yml --tags foundry_verify_mcp
```

---

## 12. Rules for AI models

1. **Use MCP for live AAP data** — do not guess template IDs or job status.
2. **Call `job_templates_list`** before recommending a template for an Azure alert.
3. **Reads** (list, retrieve) are safe to run when the user asks about AAP state.
4. **Writes** (`job_templates_launch_create`, creates, deletes) require **explicit user confirmation** in chat before `tools/call`.
5. **One MCP server only** in Foundry — do not mix with unrelated tools for AAP questions.
6. **Report tool errors verbatim** (HTTP status, MCP error message) when calls fail.

---

## 13. Related repository files

| Path | Purpose |
|------|---------|
| [scripts/aap_mcp_client.py](../scripts/aap_mcp_client.py) | Python MCP client (Bearer, SSE, tools/call) |
| [scripts/aap_mcp_or_navigator.py](../scripts/aap_mcp_or_navigator.py) | CLI wrapper + playbook fallback |
| [scripts/FIX-FOUNDRY-MCP-404.md](../scripts/FIX-FOUNDRY-MCP-404.md) | Foundry 404/500 troubleshooting |
| [config/foundry_agent_aap_mcp_skill.md](../config/foundry_agent_aap_mcp_skill.md) | Short Foundry system prompt |
| [examples/AGENT-ALERT-PROMPTS.md](../examples/AGENT-ALERT-PROMPTS.md) | Copy-paste Playground tests |
| [playbooks/site.yml](../playbooks/site.yml) | Register MCP + Foundry connection |
| [playbooks/create-gateway-token.yml](../playbooks/create-gateway-token.yml) | Mint Bearer token |

---

## 14. Quick curl sequence (copy-paste template)

Replace `<TOKEN>` and use `-k` only if TLS verification is disabled in lab.

```bash
MCP='https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp'
TOK='<TOKEN>'
HDR=(-H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -H "Authorization: Bearer $TOK")

# initialize — capture Mcp-Session-Id from response headers
curl -sk -D /tmp/mcp.hdr -X POST "$MCP" "${HDR[@]}" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"1"}}}'

SID=$(grep -i mcp-session-id /tmp/mcp.hdr | awk '{print $2}' | tr -d '\r')

# tools/list
curl -sk -X POST "$MCP" "${HDR[@]}" -H "Mcp-Session-Id: $SID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

---

*Document version: workshop cluster `cluster-wg2cd-2.dynamic2.redhatworkshops.io`. Update URLs if the environment changes.*
