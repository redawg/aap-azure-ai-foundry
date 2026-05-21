#!/usr/bin/env bash
# List Cognitive Services accounts and AI Foundry project API endpoints in the current subscription.
set -euo pipefail

# Get subscription ID from environment or creds.md
if [ -z "${AZ_SUBSCRIPTION_ID:-}" ] && [ -f "creds.md" ]; then
  AZ_SUBSCRIPTION_ID=$(grep -i "subscription id" creds.md | head -1 | awk '{print $NF}' || true)
fi

if [ -z "${AZ_SUBSCRIPTION_ID:-}" ]; then
  echo "Error: AZ_SUBSCRIPTION_ID not set"
  echo "Set it via environment variable or ensure creds.md contains Azure Subscription ID"
  exit 1
fi

az account set --subscription "${AZ_SUBSCRIPTION_ID}"

echo "Cognitive Services accounts:"
az cognitiveservices account list -o table

echo
echo "Attempting project endpoints (requires ai extension or REST)..."
for id in $(az cognitiveservices account list --query "[].id" -o tsv); do
  name=$(az cognitiveservices account show --ids "$id" --query name -o tsv)
  rg=$(az cognitiveservices account show --ids "$id" --query resourceGroup -o tsv)
  endpoint=$(az cognitiveservices account show --ids "$id" --query properties.endpoint -o tsv 2>/dev/null || true)
  echo "--- ${name} (${rg}) endpoint=${endpoint}"
  az rest --method get \
    --url "https://management.azure.com${id}/projects?api-version=2025-05-01-preview" 2>/dev/null \
    | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for p in data.get('value', []):
        props = p.get('properties', {})
        print('  project:', p.get('name'), props.get('displayName', ''))
except Exception as e:
    print('  (projects API:', e, ')')
" || true
done
