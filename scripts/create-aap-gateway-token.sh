#!/usr/bin/env bash
# Create an AAP Gateway API token for MCP (Bearer auth required by aap-mcp-server).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"

AAP_USER="${AAP_USER:-admin}"
AAP_PASSWORD="${AAP_PASSWORD:?Set AAP_PASSWORD}"
AAP_BASE="${AAP_BASE_URL:-https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"
DESC="${AAP_TOKEN_DESCRIPTION:-foundry-mcp}"

resp=$(curl -sk -u "${AAP_USER}:${AAP_PASSWORD}" -X POST "${AAP_BASE%/}/api/gateway/v1/tokens/" \
  -H "Content-Type: application/json" \
  -d "{\"description\":\"${DESC}\",\"application\":\"\",\"scope\":\"write\"}")

python3 -c "
import json, sys
d = json.loads(sys.argv[1])
tok = d.get('token')
if not tok:
    print('Failed to create gateway token:', d, file=sys.stderr)
    sys.exit(1)
print(tok)
" "$resp"
