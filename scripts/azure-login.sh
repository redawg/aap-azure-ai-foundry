#!/usr/bin/env bash
# Azure login helper script using credentials from creds.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Azure Login (Service Principal)${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo

# Load credentials from creds.md if available
if [ -f "$PROJECT_DIR/creds.md" ]; then
    echo "Loading credentials from creds.md..."

    AZURE_CLIENT_ID=$(grep -A 2 "Azure Client ID:" "$PROJECT_DIR/creds.md" | tail -1 | tr -d '[:space:]')
    AZURE_CLIENT_SECRET=$(grep -A 2 "Azure Password:" "$PROJECT_DIR/creds.md" | tail -1 | tr -d '[:space:]')
    AZURE_SUBSCRIPTION_ID=$(grep -A 2 "Azure Subscription ID:" "$PROJECT_DIR/creds.md" | tail -1 | tr -d '[:space:]')
    AZURE_TENANT="redhat.com"  # Red Hat workshop tenant

    echo -e "${GREEN}✓${NC} Client ID: ${AZURE_CLIENT_ID}"
    echo -e "${GREEN}✓${NC} Subscription ID: ${AZURE_SUBSCRIPTION_ID}"
    echo -e "${GREEN}✓${NC} Tenant: ${AZURE_TENANT}"
    echo
else
    echo -e "${YELLOW}⚠${NC} creds.md not found. Please provide Azure credentials:"
    echo
    read -p "Client ID: " AZURE_CLIENT_ID
    read -p "Client Secret: " AZURE_CLIENT_SECRET
    read -p "Subscription ID: " AZURE_SUBSCRIPTION_ID
    read -p "Tenant (default: redhat.com): " AZURE_TENANT
    AZURE_TENANT=${AZURE_TENANT:-redhat.com}
    echo
fi

# Login to Azure
echo "Logging in to Azure..."
az login --service-principal \
    --username "$AZURE_CLIENT_ID" \
    --password "$AZURE_CLIENT_SECRET" \
    --tenant "$AZURE_TENANT" \
    --output table

echo
echo "Setting subscription..."
az account set --subscription "$AZURE_SUBSCRIPTION_ID"

echo
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Azure login successful!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo

# Show current account
echo "Current account:"
az account show -o table

echo
echo "Resource groups:"
az group list --query "[].{Name:name, Location:location}" -o table | head -10

echo
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo
echo "Next steps:"
echo "  • Run Copilot setup: ansible-playbook playbooks/setup-copilot-mcp.yml"
echo "  • List Foundry endpoints: ./scripts/discover-foundry-endpoint.sh"
echo "  • View subscription: az account show"
echo
