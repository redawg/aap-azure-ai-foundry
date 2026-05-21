# Fix Foundry MCP "HTTP 404 while enumerating tools"

## What the error really means

The MCP URL is correct. The server returns **HTTP 404** with JSON `"Session not found"` when **`tools/list` runs without a valid Gateway Bearer token** in the `Authorization` header.

`initialize` can succeed with Basic auth; **tool enumeration requires Bearer**.

## Wrong portal setup (causes 404)

If the connection was created as **API key** with **Target URL** = the full MCP URL, Foundry may not send `Authorization: Bearer …` and tool discovery fails.

## Correct setup

### 1. Create a Gateway token

```bash
AAP_PASSWORD='…' ~/aap-azure-ai-foundry/scripts/create-aap-gateway-token.sh
```

Copy the token (single line, no spaces).

### 2. Fix the Foundry connection

1. [https://ai.azure.com](https://ai.azure.com) → project **`foundry-wg2cd-1-project`**
2. **Management** → **Connected resources** → **`aap-mcp-bearer`**
3. Connection must be **Custom keys** (not “API key” with MCP URL as target).
4. **Target** should be `_` or blank — **not** the full `…/mcp` URL (the agent supplies the MCP URL).
5. Under **Custom keys** add:
   - **Name:** `Authorization`
   - **Value:** `Bearer <paste-token-here>` (include the word `Bearer` and a space)
6. **Save**

### 3. Agent MCP URL (unchanged)

```
https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp
```

### 4. Test

**Agents** → **aap-automation-agent** → Playground.

## Verify from terminal

```bash
TOK=$(AAP_PASSWORD='…' scripts/create-aap-gateway-token.sh)
# tools/list must be HTTP 200
AAP_PASSWORD='…' AAP_GATEWAY_TOKEN="$TOK" python3 scripts/register-foundry-mcp.py
# (only runs MCP probe; re-paste Bearer in portal after)
```
