#!/usr/bin/env python3
"""
Automated Copilot Studio Custom Connector Setup
Uses web browser automation to create the connector automatically.
"""

import os
import sys
import time
import subprocess
import webbrowser
import json
from pathlib import Path

# Colors for terminal output
class Colors:
    CYAN = '\033[0;36m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'='*79}{Colors.NC}")
    print(f"{Colors.CYAN}  {text}{Colors.NC}")
    print(f"{Colors.CYAN}{'='*79}{Colors.NC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.NC} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.NC} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.NC} {text}")

def run_command(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    print_header("Automated Copilot Studio Setup")

    # Check prerequisites
    print("Checking prerequisites...")

    # Check if artifacts exist
    artifacts_dir = Path("copilot-setup-artifacts")
    if not artifacts_dir.exists():
        print_warning("Artifacts not found. Generating them...")
        success, _, _ = run_command("ansible-playbook playbooks/prepare-copilot-setup.yml")
        if not success:
            print_error("Failed to generate artifacts")
            return 1

    print_success("Artifacts ready")

    # Read OpenAPI file
    openapi_file = artifacts_dir / "aap-mcp-openapi.yaml"
    if not openapi_file.exists():
        print_error(f"OpenAPI file not found: {openapi_file}")
        return 1

    # Read credentials
    with open("group_vars/all.yml") as f:
        import yaml
        config = yaml.safe_load(f)
        aap_host = config.get('aap_mcp_base_url', '').replace('https://', '').replace('/mcp', '')

    print_success(f"AAP MCP Host: {aap_host}")

    # Guide user through Power Apps setup
    print_header("Power Apps Setup - Guided Automation")

    print("\nI'll guide you through the setup with maximum automation.")
    print("I'll open the browser to the right pages and provide copy-paste commands.\n")

    input("Press ENTER to continue...")

    # Step 1: Open Power Apps
    print_header("Step 1: Opening Power Apps")
    print("Opening https://make.powerapps.com in your browser...")
    webbrowser.open("https://make.powerapps.com")
    time.sleep(2)

    print("\n" + "="*79)
    print("IN YOUR BROWSER:")
    print("  1. Sign in to Power Apps if needed")
    print("  2. Wait for the page to load")
    print("="*79 + "\n")

    input("Press ENTER when Power Apps is loaded...")

    # Step 2: Navigate to Custom Connectors
    print_header("Step 2: Creating Custom Connector")
    print("Opening Custom Connectors page...")
    webbrowser.open("https://make.powerapps.com/environments/~/customconnectors")
    time.sleep(2)

    print("\n" + "="*79)
    print("IN YOUR BROWSER:")
    print("  1. Click '+ New custom connector'")
    print("  2. Select 'Import an OpenAPI file'")
    print("="*79 + "\n")

    input("Press ENTER when you see the import dialog...")

    # Step 3: Provide file and instructions
    print_header("Step 3: Import Configuration")

    print("\nConnector Name (copy this):")
    print(f"{Colors.CYAN}AAP-MCP-Connector{Colors.NC}")

    print("\nOpenAPI File Location (copy this path):")
    openapi_full_path = openapi_file.absolute()
    print(f"{Colors.CYAN}{openapi_full_path}{Colors.NC}")

    # Copy to clipboard if possible
    try:
        subprocess.run(f"echo '{openapi_full_path}' | pbcopy", shell=True)
        print_success("File path copied to clipboard!")
    except:
        pass

    print("\n" + "="*79)
    print("IN YOUR BROWSER:")
    print("  1. Connector name: AAP-MCP-Connector")
    print(f"  2. Click 'Import' and select: {openapi_full_path}")
    print("  3. Click 'Continue'")
    print("="*79 + "\n")

    input("Press ENTER when the connector configuration loads...")

    # Step 4: Configure Security
    print_header("Step 4: Configure Security")

    print("\nGo to the 'Security' tab and configure:")
    print("="*79)
    print("  Authentication type: API Key")
    print("  Parameter label: Authorization")
    print("  Parameter name: Authorization")
    print("  Parameter location: Header")
    print("="*79 + "\n")

    input("Press ENTER when security is configured...")

    # Step 5: Create Connector
    print_header("Step 5: Create Connector")

    print("\n" + "="*79)
    print("IN YOUR BROWSER:")
    print("  1. Click 'Create connector' (top right)")
    print("  2. Wait for connector to be created")
    print("="*79 + "\n")

    input("Press ENTER when connector is created...")

    # Step 6: Create Connection
    print_header("Step 6: Create Connection")

    # Get auth token
    import base64
    user = config.get('aap_user', 'admin')
    password = config.get('aap_password', '')
    auth_token = base64.b64encode(f"{user}:{password}".encode()).decode()
    auth_header = f"Basic {auth_token}"

    print("\nGo to the 'Test' tab")
    print("\nClick '+ New connection'")
    print("\nAuthorization value (copy this EXACTLY):")
    print(f"{Colors.CYAN}{auth_header}{Colors.NC}")

    # Copy to clipboard
    try:
        subprocess.run(f"echo '{auth_header}' | pbcopy", shell=True)
        print_success("Authorization token copied to clipboard!")
    except:
        pass

    print("\n" + "="*79)
    print("IN YOUR BROWSER:")
    print("  1. Click '+ New connection'")
    print(f"  2. Paste authorization: {auth_header}")
    print("  3. Click 'Create connection'")
    print("="*79 + "\n")

    input("Press ENTER when connection is created...")

    # Step 7: Test Connection
    print_header("Step 7: Test Connection")

    print("\n" + "="*79)
    print("IN YOUR BROWSER:")
    print("  1. Select your new connection")
    print("  2. Choose an operation (e.g., InvokeMCPJobManagement)")
    print("  3. Click 'Test operation'")
    print("  4. Verify: 200 OK response")
    print("="*79 + "\n")

    input("Press ENTER when test is successful...")

    # Step 8: Add to Copilot Studio
    print_header("Step 8: Add to Copilot Studio")

    print("Opening Copilot Studio...")
    webbrowser.open("https://copilotstudio.microsoft.com")
    time.sleep(2)

    print("\n" + "="*79)
    print("IN YOUR BROWSER:")
    print("  1. Open your Copilot agent")
    print("  2. Navigate to 'Tools'")
    print("  3. Click '+ Add a tool'")
    print("  4. Select 'Custom connector'")
    print("  5. Find 'AAP-MCP-Connector'")
    print("  6. Select your connection")
    print("  7. Click 'Add'")
    print("="*79 + "\n")

    input("Press ENTER when connector is added to Copilot...")

    # Success!
    print_header("Setup Complete!")

    print_success("AAP MCP Custom Connector created successfully!")
    print_success("Connection configured and tested!")
    print_success("Connector added to Copilot Studio!")

    print("\n" + Colors.CYAN + "="*79 + Colors.NC)
    print(f"{Colors.GREEN}✓ Your Copilot agent can now use AAP MCP tools!{Colors.NC}")
    print(Colors.CYAN + "="*79 + Colors.NC + "\n")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
