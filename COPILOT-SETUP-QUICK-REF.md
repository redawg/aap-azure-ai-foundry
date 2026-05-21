# AAP MCP → Copilot Studio Quick Reference

## 🚀 Quick Setup

### 1. Upload OpenAPI File
**File:** `/Users/cferman/git/azure-aap-mcp/aap-mcp-openapi.yaml`

**Power Apps:** https://make.powerapps.com → Custom connectors → + New custom connector → Import an OpenAPI file

### 2. Security Configuration
```
Authentication type: API Key
Parameter name: Authorization
Parameter location: Header
```

### 3. Authorization Value

Generate your auth token:
```bash
# Get credentials from group_vars/all.yml and encode
echo -n "$(grep aap_user group_vars/all.yml | awk '{print $2}'):$(grep aap_password group_vars/all.yml | awk '{print $2}' | tr -d '\"')" | base64
```

Or run the playbook to generate setup artifacts:
```bash
ansible-playbook playbooks/prepare-copilot-setup.yml
# Token will be in: copilot-setup-artifacts/SETUP-INSTRUCTIONS.txt
```

Format:
```
Basic <base64-encoded-username:password>
```
⚠️ **Include "Basic " prefix with space!**

### 4. Add to Copilot
**Copilot Studio:** https://copilotstudio.microsoft.com → Tools → + Add a tool → Custom connector

---

## 📋 Key Details

| Setting | Value |
|---------|-------|
| **AAP MCP Host** | `aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io` |
| **Scheme** | `HTTPS` |
| **Base URL** | `/` |
| **Auth Type** | `Basic` (API Key in Header) |
| **Credentials** | From `group_vars/all.yml` |

## 🔍 MCP Endpoints

The OpenAPI file defines three operations:
- **InvokeMCPJobManagement** → `/job_management/mcp`
- **InvokeMCPInventoryManagement** → `/inventory_management/mcp`
- **InvokeMCPSystemMonitoring** → `/system_monitoring/mcp`

## ⚡ Testing

Test MCP server accessibility:
```bash
curl -sk -I https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp
```

Test with auth:
```bash
# Get auth token from group_vars
USER=$(grep '^aap_user:' group_vars/all.yml | awk '{print $2}')
PASS=$(grep '^aap_password:' group_vars/all.yml | awk '{print $2}' | tr -d '"')
AUTH_TOKEN=$(echo -n "${USER}:${PASS}" | base64)

curl -sk -X POST https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp \
  -H "Authorization: Basic ${AUTH_TOKEN}" \
  -H "Content-Type: application/json"
```

## ⚠️ Important Notes

1. **SSL Certificate Required:** Self-signed certificates won't work with Power Platform
2. **Endpoint Paths:** May need adjustment based on your MCP deployment
3. **Authorization Header:** Must include "Basic " or "Bearer " prefix with space
4. **Case Sensitive:** Parameter name "Authorization" must be exact

## 📚 Full Documentation

See: `/Users/cferman/git/azure-aap-mcp/docs/COPILOT-STUDIO-SETUP.md`
