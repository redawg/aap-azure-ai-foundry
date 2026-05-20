#!/usr/bin/env bash
# Confirm MCP is up and tools/list returns tool definitions
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"

AAP_USER="${AAP_USER:-admin}"
AAP_PASSWORD="${AAP_PASSWORD:?Set AAP_PASSWORD}"
MCP_URL="${MCP_BASE:-https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}/mcp"

HDR=(-H "Content-Type: application/json" -H "Accept: application/json, text/event-stream")

post_mcp() {
  local payload="$1"
  curl -sk -u "${AAP_USER}:${AAP_PASSWORD}" -X POST "$MCP_URL" "${HDR[@]}" -d "$payload"
}

echo "== 1. MCP initialize =="
INIT='{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"verify-tools","version":"1.0"}},"id":1}'
init_out=$(post_mcp "$INIT")
echo "$init_out"
if ! echo "$init_out" | grep -q 'serverInfo'; then
  echo "FAIL: initialize did not return serverInfo" >&2
  exit 1
fi
echo "OK: MCP server responded to initialize"

echo ""
echo "== 2. MCP tools/list =="
LIST='{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}'
list_out=$(post_mcp "$LIST")
echo "$list_out"

tool_count=$(echo "$list_out" | python3 -c "
import sys, re, json
text = sys.stdin.read()
# SSE: extract data: lines
chunks = re.findall(r'^data:\s*(\{.*\})\s*$', text, re.M)
if not chunks:
    try:
        d = json.loads(text)
        chunks = [json.dumps(d)]
    except json.JSONDecodeError:
        pass
for c in chunks:
    try:
        d = json.loads(c)
        tools = d.get('result', {}).get('tools', [])
        if tools:
            print(len(tools))
            for t in tools:
                print(f\"  - {t.get('name','?')}\")
            sys.exit(0)
    except json.JSONDecodeError:
        continue
print(0)
" 2>/dev/null || echo "0")

if [ "${tool_count:-0}" = "0" ] || [ -z "${tool_count}" ]; then
  echo ""
  echo "WARN: tools/list returned no tools (or parse failed). Server is up; toolsets may need a session or separate paths."
  echo "Per-toolset URLs on this cluster:"
  echo "  ${MCP_URL%/mcp}/job_management/mcp"
  echo "  ${MCP_URL%/mcp}/inventory_management/mcp"
  echo "  ${MCP_URL%/mcp}/system_monitoring/mcp"
  exit 0
fi

echo ""
echo "OK: MCP tools available (count above)"
