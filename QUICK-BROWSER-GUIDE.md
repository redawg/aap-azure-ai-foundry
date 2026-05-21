# Quick Browser Setup Guide - Open Now!

**Two browser tabs just opened for you:**
- ✅ Power Apps (Custom Connectors page)
- ✅ Copilot Studio

**Authorization token:** Already copied to your clipboard! ✓

---

## 🎯 Follow These Steps (2 minutes)

### Tab 1: Power Apps

**1. Create Custom Connector** (30 seconds)
```
Click: "+ New custom connector" → "Import an OpenAPI file"

Name: AAP-MCP-Connector
File: /Users/cferman/git/azure-aap-mcp/copilot-setup-artifacts/aap-mcp-openapi.yaml

Click: "Continue"
```

**2. Configure Security** (20 seconds)
```
Go to: "Security" tab

Set these values:
  • Authentication type: API Key
  • Parameter name: Authorization  
  • Parameter location: Header

(Leave other fields default)
```

**3. Create Connector** (10 seconds)
```
Click: "Create connector" (blue button, top right)

Wait: ~5 seconds for it to save
```

**4. Create Connection** (30 seconds)
```
Go to: "Test" tab

Click: "+ New connection"

Paste authorization: Cmd+V (already in your clipboard!)
  Should paste: Basic YWRtaW46TXpjME1EZ3dfMQ==

Click: "Create connection"
```

**5. Test It** (20 seconds)
```
Select: Your new connection (dropdown)

Pick operation: InvokeMCPJobManagement

Click: "Test operation"

✓ Should show: 200 OK
```

---

### Tab 2: Copilot Studio

**6. Add to Your Agent** (30 seconds)
```
1. Open your Copilot agent

2. Go to: "Tools" (left sidebar)

3. Click: "+ Add a tool"

4. Select: "Custom connector"

5. Find: "AAP-MCP-Connector"

6. Select your connection

7. Click: "Add"
```

---

## ✅ Done!

Your Copilot agent can now use AAP MCP tools for:
- Job management
- Inventory management  
- System monitoring

**Test it:** Ask your Copilot agent to "list AAP job templates"

---

**Having issues?**
- Auth token not working? It's: `Basic YWRtaW46TXpjME1EZ3dfMQ==`
- File path: `/Users/cferman/git/azure-aap-mcp/copilot-setup-artifacts/aap-mcp-openapi.yaml`
- Can't find the file? Click "Browse" and navigate to it

**Total time:** ~2-3 minutes ⏱️
