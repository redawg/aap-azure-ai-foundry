# AAP Copilot agent (no Azure AI Foundry)

[GitHub Copilot SDK](https://github.com/github/copilot-sdk) agent that calls the **RHPDS workshop AAP MCP** server over HTTP. This does **not** use Azure AI Foundry Agent Service, project connections, or `playbooks/site.yml` Foundry registration.

## Architecture

```text
You → Copilot SDK (local) → HTTP MCP → AAP on OpenShift (RHPDS)
              ↓
     GitHub Copilot model  OR  Azure OpenAI BYOM (optional)
```

| Component | Value |
|-----------|--------|
| MCP URL (default) | `https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/job_management/mcp` |
| Auth | `Authorization: Bearer <gateway-token>` |
| Protocol | See [`docs/AAP-MCP-AI-REFERENCE.md`](../docs/AAP-MCP-AI-REFERENCE.md) |

## Prerequisites

1. **[GitHub Copilot CLI](https://github.com/github/copilot-cli)** installed and on `PATH` (the SDK drives it via JSON-RPC).
2. **Gateway token** (workshop AAP):

   ```bash
   ansible-playbook playbooks/create-gateway-token.yml -e @group_vars/all.yml
   ```

3. **GitHub auth** (default model path):

   ```bash
   gh auth login
   gh auth refresh --scopes copilot
   ```

4. **Python 3.11+** and deps:

   ```bash
   pip install -r copilot-aap-agent/requirements.txt
   cp copilot-aap-agent/.env.example copilot-aap-agent/.env
   # Set AAP_GATEWAY_TOKEN=... in .env
   ```

## Run

```bash
source scripts/workshop-env.sh   # optional: NO_PROXY for workshop hosts
python3 copilot-aap-agent/aap_copilot_chat.py
```

Example prompts:

- List job templates on AAP
- What is the status of the most recent failed job?
- Which templates match a high CPU alert on a RHEL VM?

## Optional: Azure model (BYOM, not Foundry agents)

Set in `.env`:

```bash
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
AZURE_MODEL_NAME=o4-mini
az login
```

Uses `DefaultAzureCredential` and Copilot SDK BYOM ([supported models](https://github.com/github/copilot-sdk/blob/main/docs/features/mcp.md)). This is **Azure OpenAI / AI Services inference only** — not Foundry MCP connections.

## Other clients ([mcp-demo](https://github.com/ansible-tmm/mcp-demo/tree/main))

| Client | Guide |
|--------|--------|
| **Cursor IDE** (6 × `streamable-http`) | [`../mcp-demo/cursor-mcp-setup/`](../mcp-demo/cursor-mcp-setup/README.md) |
| **Copilot Studio** | [`../copilotstudio/`](../copilotstudio/README.md) |

## Verify MCP without Copilot

```bash
python3 scripts/aap_mcp_or_navigator.py list-job-templates
```
