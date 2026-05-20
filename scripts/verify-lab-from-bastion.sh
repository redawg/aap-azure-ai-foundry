#!/usr/bin/env bash
# Run on the RHEL bastion (lab network). Usage:
#   AAP_PASSWORD='your-admin-password' ./scripts/verify-lab-from-bastion.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"

AAP_USER="${AAP_USER:-admin}"
AAP_PASSWORD="${AAP_PASSWORD:?Set AAP_PASSWORD}"
AAP_BASE="${AAP_BASE:-https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"
MCP_BASE="${MCP_BASE:-https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"

echo "== AAP Controller API =="
# pipefail + head closes early → curl SIGPIPE (exit 141); avoid aborting the script
curl -sk -u "${AAP_USER}:${AAP_PASSWORD}" \
  "${AAP_BASE}/api/controller/v2/config/" | head -c 200 || true
echo

echo "== MCP initialize =="
curl -sk -u "${AAP_USER}:${AAP_PASSWORD}" -X POST "${MCP_BASE}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"verify","version":"1.0"}},"id":1}'
echo

echo "== OpenShift MCP routes (if oc configured) =="
if command -v oc >/dev/null 2>&1 && [ -n "${OCP_TOKEN:-}" ]; then
  API="${OCP_API:-https://api.cluster-wg2cd-2.dynamic2.redhatworkshops.io:6443}"
  oc login "$API" --token="$OCP_TOKEN" --insecure-skip-tls-verify=true >/dev/null
  oc get ansiblemcpservers -A 2>/dev/null || true
  oc get routes -n aap 2>/dev/null | grep -iE 'NAME|mcp' || true
elif command -v oc >/dev/null 2>&1; then
  oc get ansiblemcpservers -A 2>/dev/null || true
  oc get routes -n aap 2>/dev/null | grep -i mcp || true
else
  echo "Skip: run scripts/install-oc.sh, export PATH=\$HOME/bin:\$PATH, set OCP_TOKEN"
fi
