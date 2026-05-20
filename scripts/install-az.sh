#!/usr/bin/env bash
# Install Azure CLI on Fedora/RHEL (requires sudo once)
set -euo pipefail
if command -v az >/dev/null 2>&1; then
  az version
  exit 0
fi
echo "Installing azure-cli via dnf..."
sudo dnf install -y azure-cli
az version
