#!/usr/bin/env bash
# OpenShift MCP inventory — run from a shell with lab network access
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"

API="${OCP_API:-https://api.cluster-wg2cd-2.dynamic2.redhatworkshops.io:6443}"
TOKEN="${OCP_TOKEN:?Set OCP_TOKEN to your workshop bearer token}"

if ! command -v oc >/dev/null 2>&1; then
  echo "oc not found. Run: ~/aap-azure-ai-foundry/scripts/install-oc.sh" >&2
  echo "Then: export PATH=\"\$HOME/bin:\$PATH\"" >&2
  exit 1
fi

echo "== oc login =="
oc login "$API" --token="$TOKEN" --insecure-skip-tls-verify=true

echo ""
echo "== AnsibleMCPServer CRs =="
oc get ansiblemcpservers -A

echo ""
echo "== MCP routes (namespace aap) =="
oc get routes -n aap | grep -iE 'NAME|mcp' || oc get routes -n aap
