#!/usr/bin/env bash
# Get AAP API token for Copilot Studio authentication
set -euo pipefail

# Load from group_vars if not set
if [ -z "${AAP_URL:-}" ] && [ -f "group_vars/all.yml" ]; then
  AAP_URL=$(grep '^aap_mcp_base_url:' group_vars/all.yml | awk '{print $2}' | sed 's|/mcp$||')
  AAP_URL=${AAP_URL:-$(grep '^aap_controller_url:' group_vars/all.yml | awk '{print $2}')}
fi

if [ -z "${AAP_USER:-}" ] && [ -f "group_vars/all.yml" ]; then
  AAP_USER=$(grep '^aap_user:' group_vars/all.yml | awk '{print $2}')
fi

if [ -z "${AAP_PASSWORD:-}" ] && [ -f "group_vars/all.yml" ]; then
  AAP_PASSWORD=$(grep '^aap_password:' group_vars/all.yml | awk '{print $2}' | tr -d '"')
fi

AAP_URL="${AAP_URL:-https://your-aap-controller.example.com}"
AAP_USER="${AAP_USER:-admin}"
AAP_PASSWORD="${AAP_PASSWORD:-your-password}"

if [ "$AAP_PASSWORD" = "your-password" ]; then
  echo "❌ Credentials not found in group_vars/all.yml"
  echo "Please set AAP_USER and AAP_PASSWORD environment variables"
  echo "Or ensure group_vars/all.yml exists with aap_user and aap_password"
  exit 1
fi

echo "Fetching AAP API token..."
echo "Controller URL: ${AAP_URL}"
echo

# Get OAuth2 token
TOKEN_RESPONSE=$(curl -sk -X POST \
  "${AAP_URL}/api/v2/tokens/" \
  -H "Content-Type: application/json" \
  -u "${AAP_USER}:${AAP_PASSWORD}" \
  -d '{
    "description": "Copilot Studio MCP Integration",
    "application": null,
    "scope": "write"
  }')

# Extract token
TOKEN=$(echo "${TOKEN_RESPONSE}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))")

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token. Response:"
  echo "${TOKEN_RESPONSE}" | python3 -m json.tool 2>/dev/null || echo "${TOKEN_RESPONSE}"
  exit 1
fi

echo "✅ Token retrieved successfully!"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Copy this value for Copilot Studio Custom Connector authentication:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Bearer ${TOKEN}"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "⚠️  IMPORTANT: Include the 'Bearer ' prefix (with space) when pasting into Copilot Studio"
echo
