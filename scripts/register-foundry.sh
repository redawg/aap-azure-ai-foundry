#!/usr/bin/env bash
# Register AAP MCP in Azure AI Foundry (Ansible).
set -euo pipefail
exec "$(dirname "$0")/_run-playbook.sh" playbooks/site.yml "$@"
