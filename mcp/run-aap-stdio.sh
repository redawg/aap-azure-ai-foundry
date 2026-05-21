#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../scripts/lab-env.sh
source "${SCRIPT_DIR}/../scripts/lab-env.sh"
exec python3 "${SCRIPT_DIR}/aap_stdio_server.py"
