#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/_run-playbook.sh" playbooks/site.yml --tags foundry_verify_mcp "$@"
