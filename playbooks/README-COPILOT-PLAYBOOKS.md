# Copilot Studio Setup Playbooks

This directory contains Ansible playbooks to automate the setup of AAP MCP integration with Microsoft Copilot Studio.

## Playbooks

### 1. `setup-copilot-mcp.yml` - Full Automation (Recommended)

Attempts to fully automate the Custom Connector creation using Power Platform APIs.

**Features:**
- Authenticates to Azure and Power Platform
- Creates Custom Connector from OpenAPI spec
- Creates connection with Basic auth
- Optionally adds connector to Copilot agent
- Generates setup summary

**Prerequisites:**
```bash
# Install Azure CLI
brew install azure-cli  # macOS
# or: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# Set subscription (from creds.md)
az account set --subscription <your-subscription-id>
```

**Usage:**
```bash
# Basic run (auto-discovers environment)
ansible-playbook playbooks/setup-copilot-mcp.yml

# Specify Power Platform environment
ansible-playbook playbooks/setup-copilot-mcp.yml \
  -e power_platform_environment="YOUR_ENV_ID"

# Add to Copilot agent automatically
ansible-playbook playbooks/setup-copilot-mcp.yml \
  -e copilot_agent_name="YourAgentName" \
  -e auto_add_to_copilot=true
```

**Environment Variables:**
```bash
export POWER_PLATFORM_ENV="your-environment-id"
export POWER_PLATFORM_REGION="unitedstates"  # or your region
```

---

### 2. `prepare-copilot-setup.yml` - Artifact Generation (Fallback)

Generates all files needed for manual setup. Use this if API automation doesn't work.

**Features:**
- Creates setup artifacts directory
- Generates step-by-step instructions
- Creates quick reference cards
- Includes PowerShell alternative
- Pre-fills all authentication tokens

**Usage:**
```bash
# Generate artifacts
ansible-playbook playbooks/prepare-copilot-setup.yml

# Output directory: copilot-setup-artifacts/
```

**Generated Files:**
```
copilot-setup-artifacts/
├── aap-mcp-openapi.yaml          # OpenAPI spec
├── SETUP-INSTRUCTIONS.txt        # Step-by-step guide
├── QUICK-REFERENCE.txt           # Quick reference card
├── setup-connector.ps1           # PowerShell script
└── README.md                     # Overview
```

---

## Variables

Both playbooks use variables from `group_vars/all.yml`:

| Variable | Description | Example |
|----------|-------------|---------|
| `aap_mcp_base_url` | AAP MCP server URL | `https://aap-mcp-aap.apps...` |
| `aap_user` | AAP admin username | `admin` |
| `aap_password` | AAP admin password | `<from group_vars/all.yml>` |

### Additional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `power_platform_environment` | auto-discover | Power Platform environment ID |
| `connector_name` | `AAP-MCP-Connector` | Connector technical name |
| `connector_display_name` | `Ansible Automation Platform MCP` | Display name |
| `copilot_agent_name` | `""` | Copilot agent name (optional) |
| `auto_add_to_copilot` | `false` | Auto-add to Copilot agent |

---

## Setup Workflows

### Workflow A: Full Automation

```bash
# 1. Ensure Azure login
az login
az account set --subscription 9dc2c3d2-35a8-4370-8997-b56a57b5778d

# 2. Run automated setup
ansible-playbook playbooks/setup-copilot-mcp.yml

# 3. Review summary
cat COPILOT-SETUP-SUMMARY.md

# 4. Manually add to Copilot Studio agent (if not automated)
# Visit: https://copilotstudio.microsoft.com
```

### Workflow B: Semi-Automated (API fails)

```bash
# 1. Generate artifacts
ansible-playbook playbooks/prepare-copilot-setup.yml

# 2. Review instructions
cd copilot-setup-artifacts
cat SETUP-INSTRUCTIONS.txt

# 3. Follow manual steps in Power Apps
# https://make.powerapps.com

# 4. Copy/paste auth token from instructions
```

### Workflow C: PowerShell Alternative

```bash
# 1. Generate artifacts
ansible-playbook playbooks/prepare-copilot-setup.yml

# 2. Install Power Platform modules (Windows PowerShell)
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell
Install-Module -Name Microsoft.PowerApps.PowerShell

# 3. Run PowerShell script
cd copilot-setup-artifacts
.\setup-connector.ps1

# Note: PowerShell script guides through manual steps
```

---

## Troubleshooting

### Azure Authentication Fails

```bash
# Check login status
az account show

# Re-login if needed
az login

# List subscriptions
az account list -o table

# Set correct subscription (from creds.md)
az account set --subscription <your-subscription-id>
```

### Power Platform Environment Not Found

```bash
# List environments
az rest --method GET \
  --url "https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments?api-version=2020-10-01" \
  --resource "https://api.powerplatform.com"

# Or specify manually
ansible-playbook playbooks/setup-copilot-mcp.yml \
  -e power_platform_environment="YOUR_ENV_ID"
```

### API Permission Errors

You need the following permissions:
- Power Platform Administrator (or Environment Admin)
- Power Apps User
- Ability to create Custom Connectors

If you lack permissions, use the `prepare-copilot-setup.yml` playbook for manual setup.

### Connector Creation Fails

**Symptoms:** 401, 403, or 500 errors when creating connector

**Solutions:**
1. Verify Azure token: `az account get-access-token --resource https://api.powerplatform.com`
2. Check permissions in Power Platform admin center
3. Use manual approach: `ansible-playbook playbooks/prepare-copilot-setup.yml`

### Connection Test Fails

**Common causes:**
- Missing "Basic " prefix in auth token
- Wrong credentials (check `group_vars/all.yml`)
- MCP server not accessible
- SSL certificate issues

**Verify MCP server:**
```bash
curl -sk -I https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp

# Test with auth
curl -sk -X POST https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp \
  -H "Authorization: Basic $(echo -n \"${AAP_USER}:${AAP_PASSWORD}\" | base64)" \
  -H "Content-Type: application/json"
```

---

## API Endpoints Reference

### Power Platform APIs Used

| API | Purpose | Authentication |
|-----|---------|----------------|
| `https://api.bap.microsoft.com` | Business Application Platform - environments | Azure AD token |
| `https://api.powerapps.com` | Power Apps - connectors & connections | Azure AD token |
| `https://api.powerplatform.com` | Power Platform management | Azure AD token |

### Token Scopes

```bash
# Power Platform token
az account get-access-token --resource https://api.powerplatform.com

# Power Apps token
az account get-access-token --resource https://service.powerapps.com
```

---

## Testing

### Test OpenAPI File

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('aap-mcp-openapi.yaml'))"

# Check host configuration
grep "^host:" aap-mcp-openapi.yaml
```

### Test AAP MCP Server

```bash
# Health check
curl -sk -I https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp

# Initialize session
curl -sk -X POST https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp \
  -H "Authorization: Basic $(echo -n \"${AAP_USER}:${AAP_PASSWORD}\" | base64)" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'
```

### Test Custom Connector (Post-Setup)

After creating the connector:

```bash
# List custom connectors (requires PowerShell)
Get-AdminPowerAppConnector | Where-Object {$_.DisplayName -like "*AAP*"}

# Test connection
Test-PowerAppConnection -EnvironmentName YOUR_ENV -ConnectionName YOUR_CONNECTION
```

---

## Resources

### Microsoft Documentation
- [Power Platform Connectors API](https://learn.microsoft.com/en-us/connectors/custom-connectors/)
- [Power Platform PowerShell](https://learn.microsoft.com/en-us/power-platform/admin/powershell-getting-started)
- [Copilot Studio MCP Integration](https://learn.microsoft.com/en-us/microsoft-copilot-studio/model-context-protocol)

### Internal Documentation
- [Full Setup Guide](../docs/COPILOT-STUDIO-SETUP.md)
- [Quick Reference](../COPILOT-SETUP-QUICK-REF.md)
- [AAP MCP Runbook](../docs/RUNBOOK.md)

### GitHub
- [Reference Implementation](https://github.com/ansible-tmm/mcp-demo/tree/main/copilotstudio-mcp-setup)

---

## Support

For issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review generated `COPILOT-SETUP-SUMMARY.md` (after running playbook)
3. Review artifacts in `copilot-setup-artifacts/` directory
4. Test MCP server directly with curl commands above

---

*Generated for azure-aap-mcp project - {{ ansible_date_time.iso8601 }}*
