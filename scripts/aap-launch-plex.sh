#!/usr/bin/env bash
# Launch "Personal - Plex Server Updated" on lab AAP (172.16.1.23).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lab-env.sh
source "${SCRIPT_DIR}/lab-env.sh"

TEMPLATE_ID="${PLEX_JOB_TEMPLATE_ID:-39}"
TEMPLATE_NAME="${PLEX_JOB_TEMPLATE_NAME:-Personal - Plex Server Updated}"

if [ "${1:-}" = "--find" ]; then
  curl -sk -u "${AAP_USER}:${AAP_PASSWORD}" \
    "${AAP_BASE}/api/controller/v2/job_templates/?search=plex&page_size=20" \
    -H 'Accept: application/json' | python3 -c "
import json, sys
d = json.load(sys.stdin)
for t in d.get('results', []):
    print(f\"{t['id']}\t{t['name']}\")
"
  exit 0
fi

echo "Launching job template ${TEMPLATE_ID} (${TEMPLATE_NAME}) on ${AAP_BASE} ..."
resp=$(curl -sk -w '\n%{http_code}' -u "${AAP_USER}:${AAP_PASSWORD}" \
  -X POST "${AAP_BASE}/api/controller/v2/job_templates/${TEMPLATE_ID}/launch/" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{}')

body=$(echo "$resp" | sed '$d')
code=$(echo "$resp" | tail -1)

if [ "$code" != "201" ]; then
  echo "Launch failed (HTTP ${code}):" >&2
  echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body" >&2
  exit 1
fi

echo "$body" | python3 -c "
import json, sys
j = json.load(sys.stdin)
print(f\"Job launched: id={j.get('id')} name={j.get('name')} status={j.get('status')}\")
print(f\"Monitor: ${AAP_BASE}/execution/jobs/playbook/{j.get('id')}/output\")
"
