# Cursor + AAP MCP (RHPDS / OpenShift)

Based on [ansible-tmm/mcp-demo cursor-mcp-setup](https://github.com/ansible-tmm/mcp-demo/tree/main/cursor-mcp-setup), adapted for the **Red Hat workshop** route (no `:8448` port).

## Why `streamable-http` and short server names

- **`streamable-http`** — AAP MCP uses sessions and SSE; required per [mcp-demo KNOWN_ISSUES](https://github.com/ansible-tmm/mcp-demo/blob/main/cursor-mcp-setup/KNOWN_ISSUES.md).
- **Short names** (`aap-job`, `aap-inv`, …) — avoids Cursor’s 60-character server+tool name limit ([TOOL_NAME_LIMITS](https://github.com/ansible-tmm/mcp-demo/blob/main/cursor-mcp-setup/TOOL_NAME_LIMITS.md)).

## Setup

1. Mint token:

   ```bash
   ansible-playbook playbooks/create-gateway-token.yml -e @group_vars/all.yml
   export MY_SERVICE_TOKEN='<gateway-token>'
   ```

2. Load env and open Cursor from the same shell:

   ```bash
   source mcp-demo/cursor-mcp-setup/env-rhpds.sh
   cursor .   # or your Cursor launcher
   ```

3. **Cursor → Settings → Tools & MCP** — paste contents of [`mcp-config-rhpds.json`](mcp-config-rhpds.json).

4. Verify in chat:

   ```text
   What MCP tools are available for my Ansible Automation Platform?
   ```

## Config file

| File | Purpose |
|------|---------|
| [`mcp-config-rhpds.json`](mcp-config-rhpds.json) | Six toolset servers using `AAP_MCP_BASE` + `MY_SERVICE_TOKEN` |

Host only (no `https://` in env var — URLs in JSON add scheme):

```bash
export AAP_MCP_BASE=aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io
```

## Test MCP from CLI

```bash
source mcp-demo/cursor-mcp-setup/env-rhpds.sh
curl -sk -H "Authorization: Bearer $MY_SERVICE_TOKEN" \
  -H "Accept: application/json, text/event-stream" \
  "https://${AAP_MCP_BASE}/job_management/mcp" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"1"}}}'
```

Or: `python3 scripts/aap_mcp_or_navigator.py list-job-templates`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| SSL errors in Cursor | `export NODE_TLS_REJECT_UNAUTHORIZED=0` (lab only); relaunch Cursor from terminal |
| 404 Session not found | Use **Gateway** Bearer token, not Basic-only |
| Tool name too long | Use this repo’s short server names, not `aap-mcp-job-management` |

See also [`docs/AAP-MCP-AI-REFERENCE.md`](../../docs/AAP-MCP-AI-REFERENCE.md).
