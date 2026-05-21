#!/usr/bin/env python3
"""
Opens Power Apps and provides all the information needed for setup.
No interaction required - just follow the browser tabs and copy-paste.
"""

import os
import sys
import time
import webbrowser
import base64
from pathlib import Path

# Colors
C = '\033[0;36m'
G = '\033[0;32m'
Y = '\033[1;33m'
NC = '\033[0m'

def main():
    # Load config
    import yaml
    with open("group_vars/all.yml") as f:
        config = yaml.safe_load(f)

    user = config.get('aap_user', 'admin')
    password = config.get('aap_password', '')
    auth_token = base64.b64encode(f"{user}:{password}".encode()).decode()
    auth_header = f"Basic {auth_token}"

    # Get OpenAPI file path
    openapi_file = Path("copilot-setup-artifacts/aap-mcp-openapi.yaml").absolute()

    print(f"\n{C}{'='*79}{NC}")
    print(f"{C}  AAP MCP → Copilot Studio - Automated Setup{NC}")
    print(f"{C}{'='*79}{NC}\n")

    print(f"{G}✓{NC} Opening Power Apps in your browser...")
    print(f"{G}✓{NC} Opening Copilot Studio in another tab...")
    print()

    # Open browsers
    webbrowser.open("https://make.powerapps.com/environments/~/customconnectors")
    time.sleep(1)
    webbrowser.open("https://copilotstudio.microsoft.com")

    # Display all information
    print(f"{C}{'='*79}{NC}")
    print(f"{C}  COPY-PASTE VALUES - Keep this window open for reference{NC}")
    print(f"{C}{'='*79}{NC}\n")

    print(f"{Y}STEP 1: Create Custom Connector{NC}")
    print("  → In Power Apps tab: Click '+ New custom connector' → 'Import an OpenAPI file'")
    print()
    print(f"  Connector Name:")
    print(f"  {C}AAP-MCP-Connector{NC}")
    print()
    print(f"  OpenAPI File:")
    print(f"  {C}{openapi_file}{NC}")
    print()

    print(f"{Y}STEP 2: Configure Security{NC}")
    print("  → Go to 'Security' tab")
    print()
    print(f"  Authentication type: {C}API Key{NC}")
    print(f"  Parameter name: {C}Authorization{NC}")
    print(f"  Parameter location: {C}Header{NC}")
    print()

    print(f"{Y}STEP 3: Create Connector{NC}")
    print("  → Click 'Create connector' (top right)")
    print()

    print(f"{Y}STEP 4: Create Connection{NC}")
    print("  → Go to 'Test' tab")
    print("  → Click '+ New connection'")
    print()
    print(f"  Authorization (copy this EXACTLY):")
    print(f"  {C}{auth_header}{NC}")
    print()

    # Copy to clipboard
    try:
        import subprocess
        subprocess.run(f"echo '{auth_header}' | pbcopy", shell=True, check=False)
        print(f"  {G}✓ Copied to clipboard!{NC}")
    except:
        pass

    print()
    print(f"{Y}STEP 5: Test Connection{NC}")
    print("  → Select your new connection")
    print("  → Pick an operation: InvokeMCPJobManagement")
    print("  → Click 'Test operation'")
    print("  → Verify: 200 OK")
    print()

    print(f"{Y}STEP 6: Add to Copilot Studio{NC}")
    print("  → Switch to Copilot Studio tab")
    print("  → Open your agent → Tools → + Add a tool")
    print("  → Select 'Custom connector'")
    print(f"  → Choose: {C}AAP-MCP-Connector{NC}")
    print("  → Select your connection")
    print("  → Click 'Add'")
    print()

    print(f"{C}{'='*79}{NC}")
    print(f"{G}✓ Setup complete when you finish these steps!{NC}")
    print(f"{C}{'='*79}{NC}\n")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
