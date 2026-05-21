#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/_run-playbook.sh" playbooks/install-local-tools.yml -e install_az=true "$@"
