#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/aap-ask.sh" list-job-templates "$@"
