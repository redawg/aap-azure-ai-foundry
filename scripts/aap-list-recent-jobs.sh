#!/usr/bin/env bash
# List recent jobs via Controller API (no browser).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lab-env.sh
source "${SCRIPT_DIR}/lab-env.sh"

LIMIT="${1:-5}"

curl -sk -u "${AAP_USER}:${AAP_PASSWORD}" \
  "${AAP_BASE}/api/controller/v2/unified_jobs/?order_by=-finished&page_size=${LIMIT}" \
  -H 'Accept: application/json' | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"Recent jobs (newest first, count={d.get('count', '?')} total)\")
print(f\"{'ID':<6} {'STATUS':<12} {'TYPE':<22} {'FINISHED':<22} NAME\")
print('-' * 90)
for j in d.get('results', []):
    finished = (j.get('finished') or j.get('started') or '-')[:19]
    print(f\"{j.get('id',''):<6} {j.get('status',''):<12} {j.get('type',''):<22} {finished:<22} {j.get('name','')}\")
"
