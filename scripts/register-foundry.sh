#!/usr/bin/env bash
# Register AAP MCP in Azure AI Foundry
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"

: "${AAP_PASSWORD:?Set AAP_PASSWORD}"
export FOUNDRY_PROJECT_ENDPOINT="${FOUNDRY_PROJECT_ENDPOINT:-https://foundry-wg2cd-1.services.ai.azure.com/api/projects/foundry-wg2cd-1-project}"
export FOUNDRY_MODEL_DEPLOYMENT_NAME="${FOUNDRY_MODEL_DEPLOYMENT_NAME:-claude-sonnet-4-5}"
export MCP_PROJECT_CONNECTION_NAME="${MCP_PROJECT_CONNECTION_NAME:-aap-mcp-bearer}"
export FOUNDRY_AGENT_NAME="${FOUNDRY_AGENT_NAME:-aap-automation-agent}"
export AAP_MCP_BASE_URL="${MCP_BASE:-https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"
export AAP_USER="${AAP_USER:-admin}"
export AZURE_TENANT="${AZURE_TENANT:-RedHat.com}"

if command -v az >/dev/null 2>&1 && az account show >/dev/null 2>&1; then
  echo "Using az login session..."
  if [[ "${REGISTER_USE_ANSIBLE:-}" == "1" ]] && command -v ansible-playbook >/dev/null 2>&1; then
    cd "${REPO_ROOT}"
    exec ansible-playbook playbooks/site.yml
  fi
  exec env AAP_PASSWORD="${AAP_PASSWORD}" AAP_USER="${AAP_USER}" \
    FOUNDRY_PROJECT_ENDPOINT="${FOUNDRY_PROJECT_ENDPOINT}" \
    FOUNDRY_MODEL_DEPLOYMENT_NAME="${FOUNDRY_MODEL_DEPLOYMENT_NAME}" \
    MCP_PROJECT_CONNECTION_NAME="${MCP_PROJECT_CONNECTION_NAME}" \
    FOUNDRY_AGENT_NAME="${FOUNDRY_AGENT_NAME}" \
    AAP_MCP_BASE_URL="${AAP_MCP_BASE_URL}" \
    "${SCRIPT_DIR}/configure-foundry-rest.sh"
fi

echo "No az session — using browser device-code login (azure-identity)."
echo "Install az optional: ./scripts/install-az.sh"
export PATH="${HOME}/.local/bin:${PATH}"
export AZURE_USE_DEVICE_CODE=1
exec python3 "${SCRIPT_DIR}/register-foundry-mcp.py"
