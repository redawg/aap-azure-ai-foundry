#!/usr/bin/env bash
# Launch job template by ID (default 39 = Plex demo on lab AAP).
set -euo pipefail
EXTRA=()
if [[ "${1:-}" == "--find" ]]; then
  exec "$(dirname "$0")/_run-playbook.sh" playbooks/search-job-templates.yml \
    -e aap_job_template_search=plex
fi
ID="${PLEX_JOB_TEMPLATE_ID:-39}"
exec "$(dirname "$0")/_run-playbook.sh" playbooks/launch-job-template.yml \
  -e "aap_launch_job_template_id=${ID}" "$@"
