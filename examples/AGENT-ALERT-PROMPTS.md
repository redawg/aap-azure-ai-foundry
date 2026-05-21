# Sample Azure alerts for Foundry agent evaluation

Use these with agent **aap-automation-agent** in [https://ai.azure.com](https://ai.azure.com) → project **foundry-wg2cd-1-project** → **Playground**.

Prerequisites:

- Connection **aap-mcp-bearer**: Custom key `Authorization` = `Bearer <AAP gateway token>`
- MCP tool URL on the agent: `https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp`

## Quick prompts (copy into Playground)

### 1. MCP / Foundry connection issue (template hint: Register AAP MCP)

Paste as the user message:

```text
Evaluate this Azure-related alert and recommend an AAP job template. Use job_templates_list to verify IDs.

Alert JSON:
```

Then paste the contents of [`azure-alert-mcp-404.json`](azure-alert-mcp-404.json).

**Expected:** Template **Register AAP MCP with Azure Foundry** (id 13) if it exists on the workshop controller.

---

### 2. VM high CPU (template hint: Demo or APD)

```text
You are my AAP copilot. Parse this Azure Monitor metric alert, list job templates via MCP, and recommend the best template with confidence and remediation steps.

```

Paste [`azure-alert-vm-cpu-high.json`](azure-alert-vm-cpu-high.json).

**Expected:** **Demo Job Template** (7), **APD | Single demo setup** (9), or similar; agent should call MCP to confirm.

---

### 3. RHEL BYOS deploy failure (template hint: Azure RG + RHEL BYOS Server)

```text
An Azure activity log style alert fired for a failed RHEL BYOS VM deployment. Recommend an AAP job template and whether to launch it (ask before launch).

```

Paste [`azure-alert-rhel-deploy-failed.json`](azure-alert-rhel-deploy-failed.json).

**Expected:** **Azure RG + RHEL BYOS Server** (id 38) after MCP list, if that template is synced on Controller.

---

## One-line prompts (no JSON)

```text
Azure alert: Sev2 metric alert on VM aap-fedora-demo-vm in RG openenv-wg2cd-1 — Percentage CPU above 75% for 5 minutes. Recommend an AAP job template.
```

```text
Azure alert: Foundry MCP tools/list HTTP 404 Session not found on https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp. Which AAP job template should we run?
```

## Send JSON via CLI (webhook / test playbook)

If the Function alert bridge is deployed:

```bash
WEBHOOK_URL='https://<your-function>.azurewebsites.net/api/AlertToFoundry'
curl -sS -X POST "$WEBHOOK_URL" \
  -H 'Content-Type: application/json' \
  -d @examples/azure-alert-vm-cpu-high.json
```

Or test via Ansible:

```bash
ansible-playbook playbooks/azure-fedora-alerts.yml \
  -e @group_vars/all.yml \
  -e azure_fedora_test_foundry_invoke=true \
  -e azure_fedora_webhook_url="$WEBHOOK_URL"
```

## Create a live metric alert in Azure (optional)

```bash
az login
az account set --subscription 9dc2c3d2-35a8-4370-8997-b56a57b5778d

VM_ID="/subscriptions/9dc2c3d2-35a8-4370-8997-b56a57b5778d/resourceGroups/openenv-wg2cd-1/providers/Microsoft.Compute/virtualMachines/aap-fedora-demo-vm"

az monitor metrics alert create \
  --name aap-fedora-demo-cpu-high \
  --resource-group openenv-wg2cd-1 \
  --scopes "$VM_ID" \
  --condition "avg Percentage CPU > 75" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --description "Workshop CPU alert for Foundry AAP copilot evaluation"
```

Wire the alert to your Action Group / Function webhook when ready; until then, use the JSON files above in Playground.
