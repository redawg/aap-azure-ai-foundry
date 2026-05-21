#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/_run-playbook.sh" playbooks/mcp-list-job-templates.yml "$@"
