#!/usr/bin/env bash
# Verify API + optional native MCP on lab AAP (172.16.1.23).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lab-env.sh
source "${SCRIPT_DIR}/lab-env.sh"

echo "AAP_BASE=$AAP_BASE"
echo "NO_PROXY includes 172.16.1.23: $(echo "$NO_PROXY" | grep -q '172.16.1.23' && echo yes || echo no)"

echo ""
echo "== Controller ping =="
curl -sk -u "${AAP_USER}:${AAP_PASSWORD}" \
  "${AAP_BASE}/api/controller/v2/ping/" -H 'Accept: application/json' | head -c 300
echo

echo ""
echo "== Recent jobs (API) =="
"${SCRIPT_DIR}/aap-list-recent-jobs.sh" 5

echo ""
echo "== Native MCP initialize (/mcp) =="
code=$(curl -sk -o /tmp/mcp-init.out -w '%{http_code}' -u "${AAP_USER}:${AAP_PASSWORD}" \
  -X POST "${MCP_BASE}/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"verify","version":"1"}},"id":1}')
echo "HTTP $code"
head -c 400 /tmp/mcp-init.out 2>/dev/null || true
echo
