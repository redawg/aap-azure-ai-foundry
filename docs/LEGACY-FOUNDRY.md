# Legacy: Azure AI Foundry integration

Microsoft **Copilot Studio** is the primary integration path. Use [`playbooks/site.yml`](../playbooks/site.yml) and [`docs/RUNBOOK.md`](RUNBOOK.md).

## When to use Foundry

- You already have an Azure AI Foundry project and agent workflow
- Workshop labs that register MCP via [ai.azure.com](https://ai.azure.com)

## Run

```bash
cp group_vars/all.yml.example group_vars/all.yml
# Set foundry_project_endpoint, aap_password, aap_mcp_base_url

az login
ansible-playbook playbooks/foundry-site.yml
```

## Tags

| Tag | Action |
|-----|--------|
| `foundry_verify_mcp` | Probe MCP `/mcp` only |
| `foundry_connection` | Foundry project connection only |
| `foundry_agent` | Create agent with MCP tool |
| `foundry_mcp_agent` | Full registration |

## Scripts (legacy)

Optional helpers moved to [`scripts/legacy/`](../scripts/legacy/):

- `configure-foundry-rest.sh`
- `configure-foundry-agent.py`
- `discover-foundry-endpoint.sh`

## References

- [Connect agents to MCP servers (Foundry)](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)
- [MCP server authentication (Foundry)](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/mcp-authentication)
