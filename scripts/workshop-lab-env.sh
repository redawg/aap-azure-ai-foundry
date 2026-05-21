#!/usr/bin/env bash
# Source workshop vars from gitignored group_vars/all.yml (no secrets in repo).
#   source scripts/workshop-lab-env.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GV="$ROOT/group_vars/all.yml"
if [[ ! -f "$GV" ]]; then
  echo "Missing $GV — cp group_vars/all.yml.example and fill secrets." >&2
  return 1 2>/dev/null || exit 1
fi

_py() {
  python3 - "$GV" "$1" <<'PY'
import sys
import yaml
path, key = sys.argv[1], sys.argv[2]
with open(path) as f:
    data = yaml.safe_load(f) or {}
v = data.get(key)
if v is None:
    sys.exit(1)
print(v, end="")
PY
}

export AAP_BASE_URL="${AAP_BASE_URL:-$(_py aap_base_url)}"
export AAP_USER="${AAP_USER:-$(_py aap_user)}"
export AAP_PASSWORD="${AAP_PASSWORD:-$(_py aap_password)}"
export AAP_MCP_BASE_URL="${AAP_MCP_BASE_URL:-$(_py aap_mcp_base_url)}"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-$(_py aws_access_key_id 2>/dev/null || true)}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-$(_py aws_secret_access_key 2>/dev/null || true)}"
export AZURE_SUBSCRIPTION_ID="${AZURE_SUBSCRIPTION_ID:-$(_py foundry_sub 2>/dev/null || true)}"
export OCP_API_URL="${OCP_API_URL:-$(_py ocp_api_url 2>/dev/null || true)}"
export OCP_TOKEN="${OCP_TOKEN:-$(_py ocp_token 2>/dev/null || true)}"

# shellcheck source=scripts/workshop-env.sh
source "$ROOT/scripts/workshop-env.sh"

# MCP / Cursor (mcp-demo)
export AAP_MCP_BASE="${AAP_MCP_BASE:-${AAP_MCP_BASE_URL#https://}}"
export AAP_MCP_BASE="${AAP_MCP_BASE%%/*}"
if [[ -z "${MY_SERVICE_TOKEN:-}" && -n "${AAP_GATEWAY_TOKEN:-}" ]]; then
  export MY_SERVICE_TOKEN="$AAP_GATEWAY_TOKEN"
fi

echo "Loaded workshop env (AAP, MCP, AWS, Azure sub, OCP)."
