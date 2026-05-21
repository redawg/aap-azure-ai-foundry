#!/usr/bin/env python3
"""
Ask AAP: try MCP tools first, then fall back to ansible-navigator (or ansible-playbook).

Exit codes:
  0 — completed via MCP or ansible-navigator/ansible-playbook fallback
  1 — error
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from aap_mcp_client import McpClient, ToolNotAvailableError, tool_result_json

REPO_ROOT = Path(__file__).resolve().parent.parent


class NeedsNavigatorFallback(Exception):
    """MCP cannot complete the change; run the Ansible playbook."""

OPERATIONS: dict[str, dict] = {
    "list-projects": {
        "required_tools": ["projects_list"],
        "mcp_tool": "projects_list",
        "playbook": "playbooks/aap-list-projects.yml",
    },
    "list-job-templates": {
        "required_tools": ["job_templates_list"],
        "mcp_tool": "job_templates_list",
        "playbook": "playbooks/mcp-list-job-templates.yml",
    },
    "sync-github-projects": {
        "required_tools": ["projects_create"],
        "playbook": "playbooks/sync-github-projects.yml",
    },
    "create-project": {
        "required_tools": ["projects_create"],
        "playbook": "playbooks/aap-create-project.yml",
    },
    "launch-job-template": {
        "required_tools": ["job_templates_launch_create"],
        "playbook": "playbooks/launch-job-template.yml",
    },
}


def navigator_extra_vars() -> list[str]:
    """Pass workshop credentials into the fallback playbook."""
    out: list[str] = []
    for key, var in (
        ("AAP_PASSWORD", "aap_password"),
        ("AAP_USER", "aap_user"),
        ("AAP_GATEWAY_TOKEN", "aap_gateway_token"),
        ("AAP_BASE_URL", "aap_base_url"),
        ("AAP_GITHUB_OWNER", "aap_github_owner"),
        ("AAP_ORGANIZATION_ID", "aap_organization_id"),
    ):
        val = os.environ.get(key, "").strip()
        if val:
            out.extend(["-e", f"{var}={val}"])
    return out


def run_navigator(playbook: str, extra_args: list[str]) -> int:
    pb = REPO_ROOT / playbook
    if not pb.exists():
        print(f"Fallback playbook not found: {pb}", file=sys.stderr)
        return 1
    cmd = ["ansible-navigator", "run", str(pb), "-m", "stdout", "--playbook-dir", str(REPO_ROOT)]
    if shutil_which("ansible-navigator"):
        runner = cmd
        label = "ansible-navigator"
    else:
        runner = ["ansible-playbook", str(pb)]
        label = "ansible-playbook (ansible-navigator not installed)"
    runner.extend(navigator_extra_vars())
    runner.extend(extra_args)
    print(f"\n→ MCP tools not available for this change; running {label}:")
    print(" ", " ".join(runner))
    env = os.environ.copy()
    env.setdefault("ANSIBLE_CONFIG", str(REPO_ROOT / "ansible.cfg"))
    proc = subprocess.run(runner, cwd=REPO_ROOT, env=env)
    return proc.returncode


def shutil_which(name: str) -> str | None:
    from shutil import which

    return which(name)


def github_repos(owner: str, limit: int) -> list[dict]:
    out = subprocess.check_output(
        [
            "gh",
            "repo",
            "list",
            owner,
            "--limit",
            str(limit),
            "--json",
            "name,url,isPrivate,defaultBranchRef",
        ],
        text=True,
        cwd=REPO_ROOT,
    )
    repos = []
    for r in json.loads(out):
        if r.get("isPrivate"):
            continue
        ref = r.get("defaultBranchRef") or {}
        r["default_branch"] = ref.get("name") or "main"
        repos.append(r)
    return repos


def scm_url(url: str) -> str:
    u = url.rstrip("/")
    return u if u.endswith(".git") else f"{u}.git"


def mcp_list_projects(client: McpClient) -> int:
    data = tool_result_json(client.call_tool("projects_list", {"page_size": 200}))
    print(f"Projects (via MCP projects_list): {data.get('count', len(data.get('results', [])))}")
    for p in data.get("results", []):
        print(f"  [{p.get('id')}] {p.get('name')}  {p.get('scm_url', '-')}")
    return 0


def mcp_list_job_templates(client: McpClient) -> int:
    data = tool_result_json(client.call_tool("job_templates_list", {"page_size": 200}))
    print(f"Job templates (via MCP): {data.get('count', len(data.get('results', [])))}")
    for t in data.get("results", []):
        org = (t.get("summary_fields") or {}).get("organization") or {}
        print(f"  [{t.get('id')}] {t.get('name')}  (org: {org.get('name', '-')})")
    return 0


def mcp_sync_github_projects(client: McpClient, owner: str, org_id: int) -> int:
    """Use MCP projects_create when the server exposes it."""
    existing = tool_result_json(client.call_tool("projects_list", {"page_size": 200}))
    by_url = {
        scm_url(p.get("scm_url", "")).lower(): p
        for p in existing.get("results", [])
        if p.get("scm_url")
    }
    by_name = {p["name"]: p for p in existing.get("results", [])}
    repos = github_repos(owner, int(os.environ.get("AAP_GITHUB_REPO_LIMIT", "100")))
    created = updated = 0
    for repo in repos:
        name = repo["name"]
        url = scm_url(repo["url"])
        if url.lower() in by_url:
            print(f"OK  [{name}] already linked")
            continue
        if name in by_name:
            raise NeedsNavigatorFallback(
                f"project [{name}] exists but SCM URL differs — playbook will patch via API"
            )
        body = {
            "name": name,
            "organization": org_id,
            "scm_type": "git",
            "scm_url": url,
            "scm_branch": repo.get("default_branch", "main"),
        }
        client.call_tool("projects_create", body)
        print(f"CREATE [{name}] {url} (MCP)")
        created += 1
    print(f"\nDone via MCP: created={created} updated={updated}")
    return 0


def try_mcp(operation: str, extra_args: list[str]) -> tuple[int, str]:
    op = OPERATIONS[operation]
    client = McpClient()
    try:
        info = client.connect()
        print(f"MCP server: {info.get('name')} {info.get('version')}")
        tools = {t["name"] for t in client.list_tools()}
        missing = [t for t in op.get("required_tools", []) if t not in tools]
        if missing:
            print(f"MCP missing required tools: {', '.join(missing)}")
            client.close()
            return run_navigator(op["playbook"], extra_args), "ansible-navigator"

        if operation == "list-projects":
            rc = mcp_list_projects(client)
        elif operation == "list-job-templates":
            rc = mcp_list_job_templates(client)
        elif operation == "sync-github-projects":
            owner = os.environ.get("AAP_GITHUB_OWNER", "redawg")
            org_id = int(os.environ.get("AAP_ORGANIZATION_ID", "1"))
            rc = mcp_sync_github_projects(client, owner, org_id)
        else:
            tool = op.get("mcp_tool")
            if tool:
                result = client.call_tool(tool, {})
                print(json.dumps(tool_result_json(result), indent=2)[:8000])
                rc = 0
            else:
                client.close()
                return run_navigator(op["playbook"], extra_args), "ansible-navigator"
        client.close()
        return rc, "mcp"
    except (ToolNotAvailableError, NeedsNavigatorFallback) as e:
        print(f"MCP: {e}")
        client.close()
        return run_navigator(op["playbook"], extra_args), "ansible-navigator"
    except RuntimeError as e:
        err = str(e)
        if "Unknown tool" in err or "Session not found" in err:
            print(f"MCP failed ({e}); using Ansible fallback.")
            client.close()
            return run_navigator(op["playbook"], extra_args), "ansible-navigator"
        client.close()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="AAP MCP first, ansible-navigator fallback")
    parser.add_argument("operation", choices=sorted(OPERATIONS.keys()))
    parser.add_argument("extra", nargs=argparse.REMAINDER, help="Extra args passed to navigator/playbook")
    args = parser.parse_args()
    extra = list(args.extra)
    if extra and extra[0] == "--":
        extra = extra[1:]
    try:
        rc, via = try_mcp(args.operation, extra)
        if rc == 0:
            label = "AAP MCP" if via == "mcp" else "ansible-navigator/ansible-playbook fallback"
            print(f"\nCompleted via {label}.")
        return rc
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
