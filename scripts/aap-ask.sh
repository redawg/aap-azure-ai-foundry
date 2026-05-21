#!/usr/bin/env bash
# Ask AAP: try MCP tools first, then ansible-navigator (or ansible-playbook) fallback.
#
#   ./scripts/aap-ask.sh list-projects
#   ./scripts/aap-ask.sh sync-github-projects
#   ./scripts/aap-ask.sh list-job-templates
#   ./scripts/aap-ask.sh create-project -e aap_project_name=foo -e aap_project_scm_url=...
#
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
OPERATION="${1:?Usage: aap-ask.sh <operation> [ansible extra args...]}"
shift || true
export AAP_MCP_BASE_URL="${AAP_MCP_BASE_URL:-https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"
export AAP_MCP_SERVER_PATH="${AAP_MCP_SERVER_PATH:-/mcp}"
export AAP_BASE_URL="${AAP_BASE_URL:-https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"
EXTRA=()
if [[ $# -gt 0 ]]; then
  EXTRA=(-- "$@")
fi
exec python3 "${ROOT}/scripts/aap_mcp_or_navigator.py" "${OPERATION}" "${EXTRA[@]}"
