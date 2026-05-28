# AAP MCP Setup for Microsoft Copilot Studio

This guide walks you through connecting your Ansible Automation Platform MCP server to Microsoft Copilot Studio.

## Recommended: MCP onboarding wizard

1. Run `ansible-playbook playbooks/site.yml -e copilot_setup_mode=wizard --tags copilot_wizard`
2. Open `copilot-setup-artifacts/MCP-SETUP-WIZARD.md`
3. In [Copilot Studio](https://copilotstudio.microsoft.com) → your agent → **Tools** → **Add tool** → **MCP**
4. Enter your MCP URL and Basic `Authorization` header from the guide

Requires **generative orchestration** on the agent. See [Microsoft docs](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent).

## Alternative: Power Apps custom connector

The sections below use a **Custom Connector** (OpenAPI) when you need Power Platform DLP, published connectors, or tenant governance.

Generate artifacts:

```bash
ansible-playbook playbooks/site.yml -e copilot_setup_mode=connector --tags copilot_artifacts
```

## Prerequisites

- [x] Microsoft Copilot Studio account
- [x] Power Apps access
- [x] AAP MCP server deployed at: `https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io`
- [x] AAP credentials (from creds.md)

## Setup Overview

1. Configure OpenAPI file with your AAP MCP endpoint
2. Create Custom Connector in Power Apps
3. Configure authentication
4. Test connection
5. Add to Copilot Studio agent

## Step 1: OpenAPI File

The OpenAPI file has been created at `aap-mcp-openapi.yaml` with your AAP MCP server endpoint.

**File location:** `/Users/cferman/git/azure-aap-mcp/aap-mcp-openapi.yaml`

**Configured host:** `aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io`

## Step 2: Create Custom Connector

1. Navigate to **Power Apps**: https://make.powerapps.com
2. In the left navigation, select **Custom connectors**
3. Click **+ New custom connector** → **Import an OpenAPI file**
4. Provide a name: `AAP-MCP-Connector` (or your preferred name)
5. Upload the file: `aap-mcp-openapi.yaml`
6. Click **Continue**

## Step 3: Configure Connector Settings

### General Tab
Verify the following settings are auto-populated:
- **Host:** `aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io`
- **Base URL:** `/`
- **Scheme:** `HTTPS`
- **Connect via on-premises data gateway:** Unchecked

### Security Tab
Configure authentication:

**CRITICAL - Use these exact settings:**
- **Authentication type:** `API Key`
- **Parameter label:** `Authorization` (user-facing label)
- **Parameter name:** `Authorization` (must be exact - case sensitive!)
- **Parameter location:** `Header` (must be Header, not Query)

## Step 4: Authentication Token

### Option A: Basic Auth (Recommended based on Foundry config)

Your AAP credentials are in `group_vars/all.yml`:
```yaml
aap_user: admin
aap_password: <from group_vars/all.yml>
```

Generate Basic Auth token:
```bash
# Encode credentials to Base64
echo -n "admin:<your-password>" | base64
```

**Full Authorization header value:**
```
Basic <base64-encoded-credentials>
```

**Or run the playbook to generate it:**
```bash
ansible-playbook playbooks/prepare-copilot-setup.yml
# Check: copilot-setup-artifacts/SETUP-INSTRUCTIONS.txt
```

### Option B: Bearer Token (if MCP requires OAuth)

If your MCP deployment uses Bearer tokens instead of Basic auth, you'll need to:

1. Get an AAP API token (if the AAP controller API is available)
2. Format it as: `Bearer <token>`

**Note:** The AAP controller API was not accessible during setup. If you need Bearer auth, you may need to:
- Verify the AAP controller URL is correct
- Check if the API is accessible from your network
- Use the AAP web UI to generate a personal access token

## Step 5: Create Connection

1. In the Custom Connector wizard, click **Create connector** (bottom right)
2. After creation, go to the **Test** tab
3. Click **+ New connection**
4. In the Authorization field, enter your Basic auth token:
   ```
   Basic <base64-encoded-credentials>
   ```
   Generate with: `echo -n "username:password" | base64`
   
   Or get from artifacts: `ansible-playbook playbooks/prepare-copilot-setup.yml`
   
   ⚠️ **Include "Basic " prefix with space!**
5. Click **Create connection**

## Step 6: Test the Connection

1. On the **Test** tab, select your newly created connection
2. Try one of the operations (e.g., `InvokeMCPJobManagement`)
3. Click **Test operation**
4. Expected: **200 OK** response

**Troubleshooting:**
- **401 Unauthorized:** Check the Authorization header format
- **404 Not Found:** The MCP endpoints may use different paths (see notes below)
- **SSL/TLS errors:** Ensure the MCP server has a valid certificate

## Step 7: Add to Copilot Studio

1. Open your Copilot Studio agent: https://copilotstudio.microsoft.com
2. Navigate to **Tools** in the left sidebar
3. Click **+ Add a tool**
4. Select **Custom connector**
5. Find and select your `AAP-MCP-Connector`
6. Choose the connection you created
7. Click **Add** to add it to your agent

## Important Notes

### MCP Endpoint Paths

The OpenAPI file defines these endpoints:
- `/job_management/mcp` - Job templates and execution
- `/inventory_management/mcp` - Hosts, groups, inventories
- `/system_monitoring/mcp` - Platform health and metrics

**⚠️ Verification Needed:**
Your AAP MCP server may use different endpoint paths. The Foundry integration uses `/mcp` as a single endpoint. You may need to:

1. Test the actual endpoint structure:
   ```bash
   # Test main MCP endpoint
   curl -sk -X GET https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp
   
   # Test specific management endpoints
   curl -sk -X GET https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/job_management/mcp
   ```

2. Update the OpenAPI file paths if needed to match your deployment

### Authentication Method

The current setup uses **Basic authentication** matching your Foundry configuration. If your MCP server requires a different auth method (Bearer token, OAuth, etc.), you'll need to:

1. Update the OpenAPI file's `securityDefinitions`
2. Get the appropriate credentials/tokens
3. Update the Custom Connector authentication settings

### SSL Certificates

Microsoft Power Platform requires valid SSL certificates. Self-signed certificates will **not work**. Ensure your MCP server has a valid certificate (Let's Encrypt recommended).

## Testing Checklist

- [ ] Custom Connector created successfully
- [ ] Connection created with correct Authorization header
- [ ] Test operation returns 200 OK
- [ ] Connector added to Copilot Studio agent
- [ ] Agent can successfully call MCP tools

## Security Recommendations

- ✅ Never commit API tokens or passwords to git
- ✅ Rotate credentials regularly
- ✅ Use least-privilege access for MCP connections
- ✅ Monitor MCP server logs for unauthorized access

## Troubleshooting

### Connection Test Fails

1. **Check Authorization header format:**
   - Basic auth: `Basic <base64-encoded-username:password>`
   - Bearer token: `Bearer <your-token>`
   - Must include type prefix and space!
   - Generate token: `echo -n "username:password" | base64`

2. **Verify MCP server is accessible:**
   ```bash
   curl -sk -I https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp
   ```

3. **Check endpoint paths:**
   - The OpenAPI paths may not match your deployment
   - Test each endpoint individually

### Agent Can't Use MCP Tools

1. Verify the connection is active in Power Platform
2. Check Copilot Studio tool permissions
3. Review MCP server logs for authentication errors

## Resources

- **Power Apps Maker Portal:** https://make.powerapps.com
- **Copilot Studio:** https://copilotstudio.microsoft.com
- **AAP MCP Server:** https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io
- **GitHub Setup Guide:** https://github.com/ansible-tmm/mcp-demo/tree/main/copilotstudio-mcp-setup

## Support

For issues with:
- **AAP MCP Server:** Check AAP deployment and logs
- **Power Platform:** Microsoft support or community forums
- **Copilot Studio:** Microsoft Copilot Studio documentation

---

**Next Steps:**
1. Review this guide
2. Proceed with Custom Connector creation in Power Apps
3. Test the connection
4. Add to your Copilot Studio agent
