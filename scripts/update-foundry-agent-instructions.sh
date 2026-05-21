#!/usr/bin/env bash
# Push new agent instructions (Azure alert → AAP template recommendations) to Foundry.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"

export FOUNDRY_PROJECT_ENDPOINT="${FOUNDRY_PROJECT_ENDPOINT:-https://foundry-wg2cd-1.services.ai.azure.com/api/projects/foundry-wg2cd-1-project}"
export FOUNDRY_AGENT_NAME="${FOUNDRY_AGENT_NAME:-aap-automation-agent}"
export FOUNDRY_MODEL_DEPLOYMENT_NAME="${FOUNDRY_MODEL_DEPLOYMENT_NAME:-gpt-4o}"
export MCP_PROJECT_CONNECTION_NAME="${MCP_PROJECT_CONNECTION_NAME:-aap-mcp-bearer}"

python3 -m pip install -q pyyaml azure-ai-projects azure-identity 2>/dev/null || true
exec python3 "${SCRIPT_DIR}/update-foundry-agent-instructions.py"
