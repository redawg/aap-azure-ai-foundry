#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/_run-playbook.sh" playbooks/list-job-templates.yml "$@"
