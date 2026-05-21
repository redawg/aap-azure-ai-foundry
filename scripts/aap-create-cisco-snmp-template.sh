#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/_run-playbook.sh" playbooks/aap-create-cisco-snmp-template.yml -e @group_vars/all.yml "$@"
