#!/usr/bin/env bash
# Full reset: cleanup Foundry agents/connections, then register AAP MCP agent.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${AAP_PASSWORD:?Set AAP_PASSWORD}"

"${SCRIPT_DIR}/cleanup-foundry.sh"
AAP_PASSWORD="${AAP_PASSWORD}" "${SCRIPT_DIR}/register-foundry.sh"
