#!/usr/bin/env bash
# Create Foundry project connection + MCP agent via REST (requires az login).
set -euo pipefail

: "${FOUNDRY_PROJECT_ENDPOINT:?}"
: "${FOUNDRY_MODEL_DEPLOYMENT_NAME:?}"
: "${AAP_USER:?}"
: "${AAP_PASSWORD:?}"
AUTH_HEADER="Basic $(printf '%s:%s' "${AAP_USER}" "${AAP_PASSWORD}" | base64 | tr -d '\n')"
: "${MCP_PROJECT_CONNECTION_NAME:=aap-mcp-bearer}"
: "${FOUNDRY_AGENT_NAME:=aap-automation-agent}"
: "${AAP_MCP_BASE_URL:=https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"

AGENT_TOKEN=$(az account get-access-token --scope "https://ai.azure.com/.default" --query accessToken -o tsv)

echo "Creating project connection ${MCP_PROJECT_CONNECTION_NAME}..."
/usr/bin/curl -sS -X PUT \
  "${FOUNDRY_PROJECT_ENDPOINT}/connections/${MCP_PROJECT_CONNECTION_NAME}?api-version=v1" \
  -H "Authorization: Bearer ${AGENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "name": "${MCP_PROJECT_CONNECTION_NAME}",
  "type": "CustomKeys",
  "credentials": {
    "keys": {
      "Authorization": "${AUTH_HEADER}"
    }
  }
}
EOF
)"

echo
echo "Creating agent ${FOUNDRY_AGENT_NAME}..."
/usr/bin/curl -sS -X POST \
  "${FOUNDRY_PROJECT_ENDPOINT}/agents?api-version=v1" \
  -H "Authorization: Bearer ${AGENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$(cat <<EOF
{
  "name": "${FOUNDRY_AGENT_NAME}",
  "description": "Ansible Automation Platform agent via MCP",
  "definition": {
    "kind": "prompt",
    "model": "${FOUNDRY_MODEL_DEPLOYMENT_NAME}",
    "instructions": "Use Ansible Automation Platform MCP tools for inventories, jobs, and platform configuration. Request approval before writes.",
    "tools": [
      {
        "type": "mcp",
        "server_label": "ansible-aap",
        "server_url": "${AAP_MCP_BASE_URL}/mcp",
        "require_approval": "always",
        "project_connection_id": "${MCP_PROJECT_CONNECTION_NAME}"
      }
    ]
  }
}
EOF
)"

echo
echo "Done. Test in Foundry portal chat or POST to .../openai/v1/responses with agent_reference."
