#!/usr/bin/env bash
# Register AAP MCP in Azure AI Foundry (ARM connection + agent)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"

: "${AAP_PASSWORD:?Set AAP_PASSWORD}"
export FOUNDRY_ACCOUNT="${FOUNDRY_ACCOUNT:-foundry-wg2cd-1}"
export FOUNDRY_PROJECT="${FOUNDRY_PROJECT:-foundry-wg2cd-1-project}"
export FOUNDRY_PROJECT_ENDPOINT="${FOUNDRY_PROJECT_ENDPOINT:-https://${FOUNDRY_ACCOUNT}.services.ai.azure.com/api/projects/${FOUNDRY_PROJECT}}"
export FOUNDRY_MODEL_DEPLOYMENT_NAME="${FOUNDRY_MODEL_DEPLOYMENT_NAME:-claude-sonnet-4-5}"
export MCP_PROJECT_CONNECTION_NAME="${MCP_PROJECT_CONNECTION_NAME:-aap-mcp-bearer}"
export FOUNDRY_AGENT_NAME="${FOUNDRY_AGENT_NAME:-aap-automation-agent}"
export AAP_MCP_BASE_URL="${MCP_BASE:-https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"
export AAP_USER="${AAP_USER:-admin}"

if ! command -v az >/dev/null 2>&1 || ! az account show >/dev/null 2>&1; then
  echo "Run: az login" >&2
  exit 1
fi

exec python3 "${SCRIPT_DIR}/register-foundry-mcp.py"
