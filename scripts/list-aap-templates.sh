#!/usr/bin/env bash
# List job templates on workshop AAP Controller
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=workshop-env.sh
source "${SCRIPT_DIR}/workshop-env.sh"

AAP_USER="${AAP_USER:-admin}"
AAP_PASSWORD="${AAP_PASSWORD:?Set AAP_PASSWORD}"
AAP_BASE="${AAP_BASE:-https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io}"

curl -sk -u "${AAP_USER}:${AAP_PASSWORD}" \
  "${AAP_BASE}/api/controller/v2/job_templates/?page_size=200" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"Job templates: {d.get('count', len(d.get('results', [])))}\n\")
print(f\"{'ID':<6} {'NAME':<50} {'ORG':<20}\")
print('-' * 78)
for t in d.get('results', []):
    org = (t.get('summary_fields') or {}).get('organization', {}) or {}
    print(f\"{t.get('id',''):<6} {t.get('name','')[:49]:<50} {(org.get('name') or '-'):<20}\")
"
