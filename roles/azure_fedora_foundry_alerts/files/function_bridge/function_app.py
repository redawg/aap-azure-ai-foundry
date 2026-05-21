"""Azure Monitor webhook → Microsoft Foundry agent (Responses API)."""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

FOUNDRY_ENDPOINT = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "").rstrip("/")
FOUNDRY_AGENT = os.environ.get("FOUNDRY_AGENT_NAME", "aap-automation-agent")
API_VERSION = os.environ.get("FOUNDRY_RESPONSES_API_VERSION", "v1")
SCOPE = os.environ.get("FOUNDRY_AZURE_SCOPE", "https://ai.azure.com/.default")


def _get_bearer_token() -> str:
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential().get_token(SCOPE).token


def _alert_to_prompt(body: dict) -> str:
    return (
        "Azure Monitor alert received. Analyze the payload and recommend an "
        "Ansible Automation Platform job template (use MCP tools when available).\n\n"
        f"```json\n{json.dumps(body, indent=2)}\n```"
    )


def _invoke_foundry_agent(alert_body: dict) -> tuple[int, str]:
    if not FOUNDRY_ENDPOINT:
        return 500, "FOUNDRY_PROJECT_ENDPOINT not configured"

    token = _get_bearer_token()
    url = f"{FOUNDRY_ENDPOINT}/openai/v1/responses?api-version={API_VERSION}"
    payload = {
        "input": _alert_to_prompt(alert_body),
        "extra_body": {
            "agent": {
                "name": FOUNDRY_AGENT,
                "type": "agent_reference",
            }
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, resp.read().decode("utf-8")[:4000]
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")[:4000]


@app.route(route="AlertToFoundry", methods=["POST"])
def alert_to_foundry(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        body = {"raw": req.get_body().decode("utf-8", errors="replace")}

    logging.info("Alert payload keys: %s", list(body.keys()) if isinstance(body, dict) else type(body))
    status, result = _invoke_foundry_agent(body if isinstance(body, dict) else {"alert": body})
    if status >= 400:
        logging.error("Foundry invoke failed HTTP %s: %s", status, result)
        return func.HttpResponse(result, status_code=status)
    return func.HttpResponse(result, status_code=200, mimetype="application/json")
