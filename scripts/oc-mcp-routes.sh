#!/usr/bin/env bash
set -euo pipefail
: "${OCP_TOKEN:?Set OCP_TOKEN (workshop OpenShift bearer token)}"
exec "$(dirname "$0")/_run-playbook.sh" playbooks/openshift-mcp-routes.yml -e "ocp_token=${OCP_TOKEN}" "$@"
