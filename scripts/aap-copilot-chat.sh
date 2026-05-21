#!/usr/bin/env bash
# GitHub Copilot SDK → RHPDS AAP MCP (no Foundry)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=scripts/workshop-env.sh
source "$ROOT/scripts/workshop-env.sh"
cd "$ROOT"
exec python3 "$ROOT/copilot-aap-agent/aap_copilot_chat.py" "$@"
