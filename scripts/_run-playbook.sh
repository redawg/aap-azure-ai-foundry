#!/usr/bin/env bash
# Internal helper: run an ansible-playbook from repo root.
set -euo pipefail
PLAYBOOK="${1:?Usage: _run-playbook.sh playbooks/name.yml [ansible extra args...]}"
shift
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec ansible-playbook "${PLAYBOOK}" "$@"
