#!/usr/bin/env bash
# Install oc/kubectl to ~/bin (no dnf package required)
set -euo pipefail

INSTALL_DIR="${HOME}/bin"
OC_URL="${OC_URL:-https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-linux.tar.gz}"

mkdir -p "$INSTALL_DIR"
cd "$(mktemp -d)"
trap 'rm -rf "$PWD"' EXIT

echo "Downloading OpenShift client from $OC_URL ..."
curl -fsSL -o oc.tar.gz "$OC_URL"
tar xzf oc.tar.gz oc kubectl
install -m 755 oc kubectl "$INSTALL_DIR/"

echo ""
echo "Installed:"
"$INSTALL_DIR/oc" version --client
echo ""
echo "Add to PATH if needed:  export PATH=\"\$HOME/bin:\$PATH\""
