#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/aap-ask.sh" sync-github-projects "$@"
