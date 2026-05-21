#!/usr/bin/env python3
"""Sync GitHub repos into AAP Controller projects using MCP projects_list + Controller API."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from urllib.parse import urlparse

import requests

# Reuse MCP session client from mcp-list-job-templates.py
sys.path.insert(0, os.path.dirname(__file__))
exec(open(os.path.join(os.path.dirname(__file__), "mcp-list-job-templates.py")).read().split("def main")[0])

AAP_BASE = os.environ.get(
    "AAP_BASE_URL",
    "https://aap-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io",
).rstrip("/")
MCP_URL = os.environ.get(
    "AAP_MCP_URL",
    "https://aap-mcp-aap.apps.cluster-wg2cd-2.dynamic2.redhatworkshops.io/mcp",
)
AAP_USER = os.environ.get("AAP_USER", "admin")
AAP_PASSWORD = os.environ.get("AAP_PASSWORD", "")
AAP_GATEWAY_TOKEN = os.environ.get("AAP_GATEWAY_TOKEN", "").strip()
GITHUB_OWNER = os.environ.get("AAP_GITHUB_OWNER", "redawg")
AAP_ORG_ID = int(os.environ.get("AAP_ORGANIZATION_ID", "1"))
VERIFY = os.environ.get("AAP_VERIFY_SSL", "false").lower() in ("1", "true", "yes")


def _session() -> requests.Session:
    s = requests.Session()
    s.verify = VERIFY
    s.auth = (AAP_USER, AAP_PASSWORD)
    return s


def gateway_token(session: requests.Session) -> str:
    if AAP_GATEWAY_TOKEN:
        return AAP_GATEWAY_TOKEN
    if not AAP_PASSWORD:
        raise SystemExit("Set AAP_PASSWORD or AAP_GATEWAY_TOKEN")
    r = session.post(
        f"{AAP_BASE}/api/gateway/v1/tokens/",
        json={"description": "mcp-sync-projects", "application": "", "scope": "write"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["token"]


def mcp_projects_list(token: str) -> list[dict]:
    client = McpClient(MCP_URL)
    client.auth_header = f"Bearer {token}"
    try:
        client.rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-sync-projects", "version": "1.0"},
            },
            1,
        )
        client.notify_initialized()
        msgs = client.rpc(
            "tools/call",
            {"name": "projects_list", "arguments": {"page_size": 200}},
            2,
        )
        for msg in msgs:
            if msg.get("error"):
                raise RuntimeError(msg["error"])
            for block in msg.get("result", {}).get("content", []):
                data = json.loads(block.get("text", "{}"))
                return data.get("results", [])
        return []
    finally:
        client.close()


def github_repos(owner: str) -> list[dict]:
    out = subprocess.check_output(
        ["gh", "repo", "list", owner, "--limit", "100", "--json", "name,url,isPrivate"],
        text=True,
    )
    repos = json.loads(out)
    return [r for r in repos if not r.get("isPrivate")]


def normalize_git_url(url: str) -> str:
    u = url.rstrip("/")
    if u.endswith(".git"):
        return u
    return u + ".git"


def repo_git_url(repo_url: str) -> str:
    return normalize_git_url(repo_url)


def find_by_url(projects: list[dict], git_url: str) -> dict | None:
    target = normalize_git_url(git_url).lower()
    for p in projects:
        scm = (p.get("scm_url") or "").lower()
        if normalize_git_url(scm) == target:
            return p
    return None


def find_by_name(projects: list[dict], name: str) -> dict | None:
    for p in projects:
        if p.get("name") == name:
            return p
    return None


def create_project(session: requests.Session, name: str, scm_url: str) -> dict:
    body = {
        "name": name,
        "organization": AAP_ORG_ID,
        "scm_type": "git",
        "scm_url": scm_url,
        "scm_branch": "main",
        "scm_clean": True,
        "scm_update_on_launch": True,
    }
    r = session.post(f"{AAP_BASE}/api/controller/v2/projects/", json=body, timeout=60)
    r.raise_for_status()
    return r.json()


def update_project_scm(session: requests.Session, project_id: int, scm_url: str) -> dict:
    r = session.patch(
        f"{AAP_BASE}/api/controller/v2/projects/{project_id}/",
        json={"scm_url": scm_url, "scm_branch": "main"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def sync_project_update(session: requests.Session, project_id: int) -> None:
    r = session.post(f"{AAP_BASE}/api/controller/v2/projects/{project_id}/update/", timeout=120)
    if r.status_code in (200, 201, 202):
        print(f"  sync started for project id={project_id}")
    else:
        print(f"  sync skipped id={project_id}: HTTP {r.status_code}")


def main() -> int:
    if not AAP_PASSWORD and not AAP_GATEWAY_TOKEN:
        print("Set AAP_PASSWORD or AAP_GATEWAY_TOKEN", file=sys.stderr)
        return 1

    session = _session()
    token = gateway_token(session)
    print("MCP: projects_list …")
    projects = mcp_projects_list(token)
    print(f"  existing projects: {len(projects)}")

    repos = github_repos(GITHUB_OWNER)
    print(f"GitHub: {len(repos)} public repos for {GITHUB_OWNER}")

    created = updated = skipped = 0
    for repo in repos:
        name = repo["name"]
        scm_url = repo_git_url(repo["url"])
        by_url = find_by_url(projects, scm_url)
        by_name = find_by_name(projects, name)

        if by_url:
            print(f"OK  [{name}] already linked ({scm_url})")
            skipped += 1
            continue

        if by_name:
            pid = by_name["id"]
            old = by_name.get("scm_url", "")
            print(f"PATCH [{name}] id={pid} {old} -> {scm_url}")
            update_project_scm(session, pid, scm_url)
            sync_project_update(session, pid)
            updated += 1
            by_name["scm_url"] = scm_url
            continue

        print(f"CREATE [{name}] {scm_url}")
        proj = create_project(session, name, scm_url)
        projects.append(proj)
        sync_project_update(session, proj["id"])
        created += 1

    print(f"\nDone: created={created} updated={updated} skipped={skipped}")
    print("Note: MCP exposes projects_list only; creates use Controller API.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
