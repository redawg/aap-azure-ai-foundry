# AAP MCP reference (workshop)

## Endpoints

| Service | URL |
|---------|-----|
| MCP | `https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp` |
| Controller | `https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io` |
| Foundry project API | `https://foundry-wg2cd-1.services.ai.azure.com/api/projects/foundry-wg2cd-1-project` |

## MCP protocol (direct test)

Headers on every POST:

- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`
- `Authorization: Bearer <gateway-token>`
- `Mcp-Session-Id: <from initialize response>` (for `tools/list` and `tools/call`)

Flow: `initialize` → capture session → `tools/list` or `tools/call`.

## Toolset paths

| Path | Scope |
|------|--------|
| `/mcp` | All toolsets (~100+ tools) |
| `/job_management/mcp` | Jobs, job templates, activations |
| `/inventory_management/mcp` | Inventories, hosts |

## Workshop job template hints (verify via MCP)

| ID | Name |
|----|------|
| 7 | Demo Job Template |
| 9 | APD \| Single demo setup |
| 10 | APD \| Multi-demo setup |
| 13 | Register AAP MCP with Azure Foundry |
| 37 | Azure VM + Foundry Alerts |
| 38 | Azure RG + RHEL BYOS Server |

Full keyword map: `config/azure_alert_template_map.yml`.

## Foundry agent versions

Publishing a new version (gpt-4.1 + `/mcp` + auto-approve):

```bash
FOUNDRY_MODEL_DEPLOYMENT_NAME=gpt-4.1 \
  python3 scripts/update-foundry-agent-instructions.py
```

Or use Azure SDK in `scripts/update-foundry-agent-instructions.py` / `playbooks/site.yml`.
