#!/usr/bin/env bash
# Source before opening Cursor:  source mcp-demo/cursor-mcp-setup/env-rhpds.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck source=scripts/workshop-env.sh
source "$ROOT/scripts/workshop-env.sh"

export AAP_MCP_BASE="${AAP_MCP_BASE:-aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"

if [[ -z "${MY_SERVICE_TOKEN:-}" ]]; then
  if [[ -n "${AAP_GATEWAY_TOKEN:-}" ]]; then
    export MY_SERVICE_TOKEN="$AAP_GATEWAY_TOKEN"
  else
    echo "Set MY_SERVICE_TOKEN or AAP_GATEWAY_TOKEN (playbooks/create-gateway-token.yml)" >&2
  fi
fi

# Demo/lab TLS only — matches mcp-demo cursor guide
export NODE_TLS_REJECT_UNAUTHORIZED="${NODE_TLS_REJECT_UNAUTHORIZED:-0}"

echo "AAP_MCP_BASE=https://${AAP_MCP_BASE}"
echo "MY_SERVICE_TOKEN=${MY_SERVICE_TOKEN:+set (${#MY_SERVICE_TOKEN} chars)}"
echo "Paste MCP config: ${ROOT}/mcp-demo/cursor-mcp-setup/mcp-config-rhpds.json"
