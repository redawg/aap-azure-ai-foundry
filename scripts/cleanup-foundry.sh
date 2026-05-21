#!/usr/bin/env bash
# Remove Foundry agents, connections, and optional extra ARM projects (workshop reset).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"

FOUNDRY_ACCOUNT="${FOUNDRY_ACCOUNT:-foundry-wg2cd-1}"
FOUNDRY_PROJECT="${FOUNDRY_PROJECT:-foundry-wg2cd-1-project}"
FOUNDRY_RG="${FOUNDRY_RG:-openenv-wg2cd-1}"
FOUNDRY_SUB="${FOUNDRY_SUB:-9dc2c3d2-35a8-4370-8997-b56a57b5778d}"
CONN_NAME="${MCP_PROJECT_CONNECTION_NAME:-aap-mcp-bearer}"
AGENT_NAME="${FOUNDRY_AGENT_NAME:-aap-automation-agent}"
DELETE_EXTRA_PROJECTS="${DELETE_EXTRA_PROJECTS:-true}"

EP="https://${FOUNDRY_ACCOUNT}.services.ai.azure.com/api/projects/${FOUNDRY_PROJECT}"
ARM_BASE="https://management.azure.com/subscriptions/${FOUNDRY_SUB}/resourceGroups/${FOUNDRY_RG}/providers/Microsoft.CognitiveServices/accounts/${FOUNDRY_ACCOUNT}"

if ! command -v az >/dev/null 2>&1 || ! az account show >/dev/null 2>&1; then
  echo "Run: az login" >&2
  exit 1
fi

AI_TOKEN=$(az account get-access-token --scope https://ai.azure.com/.default --query accessToken -o tsv)
MGMT_TOKEN=$(az account get-access-token --scope https://management.azure.com/.default --query accessToken -o tsv)

echo "== Delete agents in ${FOUNDRY_PROJECT} =="
agents=$(curl -sk -H "Authorization: Bearer ${AI_TOKEN}" "${EP}/agents?api-version=v1" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(' '.join(x['name'] for x in d.get('data',[])))" 2>/dev/null || true)
for a in ${agents:-}; do
  code=$(curl -sk -o /dev/null -w "%{http_code}" -X DELETE \
    -H "Authorization: Bearer ${AI_TOKEN}" "${EP}/agents/${a}?api-version=v1")
  echo "  deleted agent ${a}: HTTP ${code}"
done
[ -z "${agents:-}" ] && echo "  (none)"

echo "== Delete connection ${CONN_NAME} (ARM) =="
code=$(curl -sk -o /dev/null -w "%{http_code}" -X DELETE \
  -H "Authorization: Bearer ${MGMT_TOKEN}" \
  "${ARM_BASE}/projects/${FOUNDRY_PROJECT}/connections/${CONN_NAME}?api-version=2025-06-01")
echo "  HTTP ${code}"

if [[ "${DELETE_EXTRA_PROJECTS}" == "true" ]]; then
  echo "== Delete extra ARM projects (wg2cd-mcp, wg2cd-project) =="
  for extra in wg2cd-mcp wg2cd-project; do
    code=$(curl -sk -o /dev/null -w "%{http_code}" -X DELETE \
      -H "Authorization: Bearer ${MGMT_TOKEN}" \
      "${ARM_BASE}/projects/${extra}?api-version=2025-06-01")
    echo "  ${extra}: HTTP ${code}"
  done
fi

echo "Done. Redeploy with: AAP_PASSWORD='…' ./scripts/register-foundry.sh"
