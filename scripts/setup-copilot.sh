#!/usr/bin/env bash
# Quick setup script for AAP MCP → Copilot Studio integration
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo
}

print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_header "AAP MCP → Copilot Studio Setup"

# Check prerequisites
print_step "Checking prerequisites..."

if ! command -v ansible-playbook &> /dev/null; then
    print_error "ansible-playbook not found. Please install Ansible."
    exit 1
fi
print_success "Ansible found"

if ! command -v az &> /dev/null; then
    print_warning "Azure CLI not found. It's required for automated setup."
    echo "  Install: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    SKIP_AZURE=1
else
    print_success "Azure CLI found"
    SKIP_AZURE=0
fi

# Check Azure login
if [ "$SKIP_AZURE" -eq 0 ]; then
    print_step "Checking Azure login status..."
    if az account show &> /dev/null; then
        SUBSCRIPTION=$(az account show --query name -o tsv)
        print_success "Logged into Azure: $SUBSCRIPTION"
    else
        print_warning "Not logged into Azure. Automated setup will not work."
        echo "  Run: az login"
        SKIP_AZURE=1
    fi
fi

echo

# Present options
print_header "Setup Options"
echo "1. Full automation (Azure CLI + Power Platform APIs)"
echo "2. Generate setup artifacts for manual configuration"
echo "3. Both (run automation + generate artifacts)"
echo
read -p "Select option (1-3): " OPTION

cd "$PROJECT_DIR"

case $OPTION in
    1)
        if [ "$SKIP_AZURE" -eq 1 ]; then
            print_error "Azure CLI not available or not logged in. Cannot run automated setup."
            echo "Please run: az login"
            exit 1
        fi

        print_header "Running Automated Setup"

        # Check for custom environment
        read -p "Power Platform environment ID (leave empty to auto-discover): " PP_ENV

        if [ -z "$PP_ENV" ]; then
            ansible-playbook playbooks/setup-copilot-mcp.yml
        else
            ansible-playbook playbooks/setup-copilot-mcp.yml -e "power_platform_environment=$PP_ENV"
        fi

        print_success "Automated setup complete!"
        echo
        print_step "Next steps:"
        echo "  1. Review: COPILOT-SETUP-SUMMARY.md"
        echo "  2. Add connector to Copilot Studio agent:"
        echo "     https://copilotstudio.microsoft.com"
        ;;

    2)
        print_header "Generating Setup Artifacts"

        ansible-playbook playbooks/prepare-copilot-setup.yml

        print_success "Artifacts generated!"
        echo
        print_step "Next steps:"
        echo "  1. cd copilot-setup-artifacts"
        echo "  2. Review: SETUP-INSTRUCTIONS.txt"
        echo "  3. Follow manual setup steps"
        ;;

    3)
        print_header "Running Full Setup + Generating Artifacts"

        # Generate artifacts first
        print_step "Generating artifacts..."
        ansible-playbook playbooks/prepare-copilot-setup.yml
        print_success "Artifacts generated"
        echo

        # Run automation if Azure is available
        if [ "$SKIP_AZURE" -eq 0 ]; then
            print_step "Running automated setup..."
            read -p "Power Platform environment ID (leave empty to auto-discover): " PP_ENV

            if [ -z "$PP_ENV" ]; then
                ansible-playbook playbooks/setup-copilot-mcp.yml
            else
                ansible-playbook playbooks/setup-copilot-mcp.yml -e "power_platform_environment=$PP_ENV"
            fi

            print_success "Automated setup complete!"
        else
            print_warning "Skipping automated setup (Azure not available)"
        fi

        echo
        print_step "Next steps:"
        echo "  1. Review: COPILOT-SETUP-SUMMARY.md (if automation ran)"
        echo "  2. Or follow: copilot-setup-artifacts/SETUP-INSTRUCTIONS.txt"
        ;;

    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

echo
print_header "Setup Complete"

# Display auth token instructions
print_step "Authentication Token:"
if [ -d "copilot-setup-artifacts" ]; then
    echo "  Your authorization token is in:"
    echo -e "  ${CYAN}copilot-setup-artifacts/SETUP-INSTRUCTIONS.txt${NC}"
    echo -e "  ${CYAN}copilot-setup-artifacts/QUICK-REFERENCE.txt${NC}"
elif [ -f "group_vars/all.yml" ]; then
    print_step "Generate token with:"
    echo "  ansible-playbook playbooks/prepare-copilot-setup.yml"
    echo "  # Token will be in: copilot-setup-artifacts/SETUP-INSTRUCTIONS.txt"
else
    print_warning "Configure group_vars/all.yml first"
fi

echo
print_step "Resources:"
echo "  • Power Apps: https://make.powerapps.com"
echo "  • Copilot Studio: https://copilotstudio.microsoft.com"
echo "  • Documentation: docs/COPILOT-STUDIO-SETUP.md"
echo
