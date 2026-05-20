#!/usr/bin/env bash
# Ask AAP via MCP (job_management) what job templates exist
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"
export MCP_BASE="${MCP_BASE:-https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"
exec python3 "${SCRIPT_DIR}/mcp-list-job-templates.py"
