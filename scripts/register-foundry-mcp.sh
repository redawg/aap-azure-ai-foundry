#!/usr/bin/env bash
# Legacy name — same as register-foundry.sh / playbooks/site.yml
set -euo pipefail
exec "$(dirname "$0")/register-foundry.sh" "$@"
