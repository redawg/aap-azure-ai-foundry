# AAP MCP → Microsoft Copilot Studio Integration

## Overview

**Copilot Studio is the primary integration path** (`playbooks/site.yml`). This includes:

- MCP health checks and templated OpenAPI (six toolsets + unified `/mcp`)
- **MCP onboarding wizard** guide (`MCP-SETUP-WIZARD.md`)
- Optional Power Platform **custom connector** automation

Azure AI Foundry is legacy — see `playbooks/foundry-site.yml` and `docs/LEGACY-FOUNDRY.md`.

## What Was Created

### 📄 Configuration Files
- **`aap-mcp-openapi.yaml`** - OpenAPI 2.0 specification for AAP MCP Custom Connector
  - Pre-configured with your AAP MCP host
  - Defines three operations: Job Management, Inventory Management, System Monitoring
  - Uses API Key authentication (Basic auth)

### 🤖 Automation Playbooks
- **`playbooks/setup-copilot-mcp.yml`** - Full automation via Power Platform APIs
  - Authenticates to Azure/Power Platform
  - Creates Custom Connector
  - Creates connection with credentials
  - Generates summary report
  
- **`playbooks/prepare-copilot-setup.yml`** - Generates artifacts for manual setup
  - Creates `copilot-setup-artifacts/` directory
  - Step-by-step instructions
  - Quick reference cards
  - PowerShell scripts

### 📚 Documentation
- **`docs/COPILOT-STUDIO-SETUP.md`** - Comprehensive setup guide
- **`COPILOT-SETUP-QUICK-REF.md`** - Quick reference card
- **`playbooks/README-COPILOT-PLAYBOOKS.md`** - Playbook documentation

### 🛠️ Scripts
- **`scripts/setup-copilot.sh`** - Interactive setup wizard
- **`scripts/get-aap-token.sh`** - AAP token retrieval (for future use)

## Quick Start

### Option 1: Interactive Script (Recommended)

```bash
./scripts/setup-copilot.sh
```

This presents three choices:
1. **Full automation** (if Azure CLI available)
2. **Generate artifacts** for manual setup
3. **Both** approaches

### Option 2: Direct Playbook

```bash
# Automated
az login
az account set --subscription 9dc2c3d2-35a8-4370-8997-b56a57b5778d
ansible-playbook playbooks/setup-copilot-mcp.yml

# Manual artifacts
ansible-playbook playbooks/prepare-copilot-setup.yml
```

## Authentication Details

### Your Configuration

**AAP MCP Server:**
```
Host: aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io
Scheme: HTTPS
Base URL: /
```

**AAP Credentials:**
```yaml
# Configured in: group_vars/all.yml
aap_user: <from config>
aap_password: <from config>
```

**Generate Auth Token:**
```bash
# Method 1: Manual encoding
echo -n "username:password" | base64

# Method 2: Generate artifacts with token
ansible-playbook playbooks/prepare-copilot-setup.yml
# Token in: copilot-setup-artifacts/SETUP-INSTRUCTIONS.txt
```

**Authorization Header Format:**
```
Basic <base64-encoded-credentials>
```

⚠️ **CRITICAL**: When entering in Copilot Studio, include "Basic " prefix with space!

## MCP Endpoints

The Custom Connector exposes three MCP operations:

| Operation | Endpoint | Purpose |
|-----------|----------|---------|
| `InvokeMCPJobManagement` | `/job_management/mcp` | Job templates, execution, monitoring |
| `InvokeMCPInventoryManagement` | `/inventory_management/mcp` | Hosts, groups, inventories |
| `InvokeMCPSystemMonitoring` | `/system_monitoring/mcp` | Platform health and metrics |

## Setup Workflow

### Automated Path

```
1. Run setup script or playbook
   └─> Authenticates to Azure
   └─> Discovers Power Platform environment
   └─> Creates Custom Connector
   └─> Creates connection
   └─> Generates summary

2. Review COPILOT-SETUP-SUMMARY.md

3. Manually add to Copilot agent
   └─> https://copilotstudio.microsoft.com
   └─> Tools → Add tool → Custom connector
```

### Manual Path

```
1. Generate artifacts
   └─> ansible-playbook playbooks/prepare-copilot-setup.yml

2. Navigate to copilot-setup-artifacts/

3. Follow SETUP-INSTRUCTIONS.txt
   └─> Upload OpenAPI file to Power Apps
   └─> Configure authentication
   └─> Create connection
   └─> Add to Copilot agent
```

## Testing

### Test AAP MCP Server

```bash
# Health check
curl -sk -I https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp

# Test with authentication (get credentials from group_vars/all.yml)
USER=$(grep '^aap_user:' group_vars/all.yml | awk '{print $2}')
PASS=$(grep '^aap_password:' group_vars/all.yml | awk '{print $2}' | tr -d '"')
AUTH_TOKEN=$(echo -n "${USER}:${PASS}" | base64)

curl -sk -X POST https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp \
  -H "Authorization: Basic ${AUTH_TOKEN}" \
  -H "Content-Type: application/json"
```

### Test Custom Connector (Post-Setup)

In Power Apps (https://make.powerapps.com):
1. Go to Custom connectors
2. Select your AAP MCP connector
3. Go to Test tab
4. Select your connection
5. Test an operation
6. Expect: 200 OK response

## Prerequisites

### For Automated Setup
- ✅ Azure CLI installed (`brew install azure-cli`)
- ✅ Logged into Azure (`az login`)
- ✅ Subscription set (9dc2c3d2-35a8-4370-8997-b56a57b5778d)
- ✅ Power Platform access
- ✅ Permissions to create Custom Connectors

### For Manual Setup
- ✅ Power Apps access (https://make.powerapps.com)
- ✅ Copilot Studio access (https://copilotstudio.microsoft.com)
- ✅ Permissions to create Custom Connectors

## File Locations

```
aap-azure-ai-foundry/
├── aap-mcp-openapi.yaml              # Generated OpenAPI (from template)
├── roles/copilot_mcp/                # Verify MCP, render OpenAPI, wizard template
├── playbooks/site.yml                # Primary entry (Copilot Studio)
├── playbooks/foundry-site.yml        # Legacy Foundry
├── COPILOT-SETUP-QUICK-REF.md        # Quick reference
├── COPILOT-INTEGRATION-SUMMARY.md    # This file
├── docs/
│   └── COPILOT-STUDIO-SETUP.md       # Full setup guide
├── playbooks/
│   ├── setup-copilot-mcp.yml         # Automated setup
│   ├── prepare-copilot-setup.yml     # Generate artifacts
│   └── README-COPILOT-PLAYBOOKS.md   # Playbook docs
└── scripts/
    ├── setup-copilot.sh              # Interactive wizard
    └── get-aap-token.sh              # Token retrieval
```

## Resources

### Microsoft Portals
- **Power Apps**: https://make.powerapps.com
- **Copilot Studio**: https://copilotstudio.microsoft.com
- **Azure Portal**: https://portal.azure.com

### Documentation
- [Microsoft Copilot Studio MCP Docs](https://learn.microsoft.com/en-us/microsoft-copilot-studio/model-context-protocol)
- [Power Platform Custom Connectors](https://learn.microsoft.com/en-us/connectors/custom-connectors/)
- [Azure AI Foundry MCP Integration](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)

### Reference Implementation
- [ansible-tmm/mcp-demo](https://github.com/ansible-tmm/mcp-demo/tree/main/copilotstudio-mcp-setup)

## Troubleshooting

### Issue: Azure login fails
**Solution**: Run `az login` and ensure you're using the correct subscription

### Issue: Power Platform environment not found
**Solution**: Specify manually with `-e power_platform_environment=YOUR_ENV_ID`

### Issue: Custom Connector creation fails
**Solution**: Check permissions or use manual approach (`prepare-copilot-setup.yml`)

### Issue: Connection test returns 401
**Solution**: Verify Authorization header includes "Basic " prefix with space

### Issue: Connection test returns 404
**Solution**: MCP endpoints may use different paths - verify with curl test

### Issue: SSL/TLS errors
**Solution**: Ensure AAP MCP server has valid SSL certificate (not self-signed)

## Security Notes

- ✅ Credentials stored in `group_vars/all.yml` (gitignored)
- ✅ Basic auth token auto-generated from credentials
- ⚠️ Never commit `creds.md`, `.env`, or `group_vars/all.yml`
- ⚠️ Rotate credentials regularly
- ⚠️ Use least-privilege access for MCP connections

## Next Steps

After setup is complete:

1. **Verify connector** in Power Apps
2. **Add to Copilot agent** in Copilot Studio
3. **Test MCP operations** in the agent
4. **Monitor usage** in AAP MCP server logs
5. **Document workflows** that use the integration

## Support

For issues:
1. Check the troubleshooting section above
2. Review generated summary: `COPILOT-SETUP-SUMMARY.md`
3. Review artifacts: `copilot-setup-artifacts/SETUP-INSTRUCTIONS.txt`
4. Test MCP server directly with curl commands
5. Check Power Platform admin center for connector status

---

**Configuration**: See `group_vars/all.yml.example` and `creds.md` (gitignored)
