#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Odoo DevOps-Agent task poller -> OpenClaw bridge.

Polls Odoo for project.task records tagged "DevOps-Agent" sitting in the
Backlog stage, hands each one to the local OpenClaw gateway
(docker exec ... openclaw agent), posts the reply back into the task's
chatter, and tags the task so it is not reprocessed. Runs as a systemd
oneshot on CT150, triggered by a timer. Credentials come from the
environment (EnvironmentFile). Mirrors the existing odoo_discuss_bridge.py
pattern on this host.

Poll-based by design: Odoo (CT140/Rothkreuz) cannot currently reach CT150
directly (cross-site routing issue, tracked separately), so CT150 pulls
instead of Odoo pushing.
"""
import html
import json
import os
import re
import subprocess
import sys
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "http://10.1.0.112:8069")
ODOO_DB = os.environ.get("ODOO_DB", "FraWo_GbR")
OC_LOGIN = os.environ["DEVOPS_ODOO_LOGIN"]
OC_PASSWORD = os.environ["DEVOPS_ODOO_PASSWORD"]
DEVOPS_TAG_ID = int(os.environ.get("DEVOPS_TAG_ID", "75"))
BACKLOG_STAGE_ID = int(os.environ.get("DEVOPS_BACKLOG_STAGE_ID", "1"))
DONE_TAG_NAME = os.environ.get("DEVOPS_DONE_TAG_NAME", "ServAssi-Ausgeloest")
AGENT_TIMEOUT = int(os.environ.get("BRIDGE_AGENT_TIMEOUT", "300"))

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def kw(model, method, args, kwargs=None):
    return models.execute_kw(ODOO_DB, UID, OC_PASSWORD, model, method, args, kwargs or {})


def strip_html(body: str) -> str:
    body = re.sub(r"<br\s*/?>", "\n", body)
    body = re.sub(r"</p>\s*<p[^>]*>", "\n\n", body)
    body = re.sub(r"<[^>]+>", "", body)
    return html.unescape(body).strip()


def get_or_create_done_tag() -> int:
    ids = kw("project.tags", "search", [[["name", "=", DONE_TAG_NAME]]], {"limit": 1})
    if ids:
        return ids[0]
    return kw("project.tags", "create", [{"name": DONE_TAG_NAME}])


def ask_agent(text: str, session_key: str) -> str:
    cmd = [
        "docker", "exec", "openclaw",
        "openclaw", "agent",
        "--message", text,
        "--session-key", session_key,
        "--json",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=AGENT_TIMEOUT)
    if out.returncode != 0:
        raise RuntimeError(f"openclaw agent rc={out.returncode}: {out.stderr[-400:]}")
    raw = out.stdout.strip()
    start = raw.find("{")
    payload = json.loads(raw[start:]) if start >= 0 else {}
    for key in ("text", "reply", "message", "content"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    result = payload.get("result") or {}
    if isinstance(result, dict):
        for key in ("text", "reply", "message", "content"):
            val = result.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        payloads = result.get("payloads")
        if isinstance(payloads, list):
            texts = [p.get("text", "") for p in payloads if isinstance(p, dict)]
            joined = "\n".join(t for t in texts if t).strip()
            if joined:
                return joined
    raise RuntimeError(f"no reply text in agent output: {raw[:400]}")


def main() -> int:
    global UID
    UID = common.authenticate(ODOO_DB, OC_LOGIN, OC_PASSWORD, {})
    if not UID:
        print("FATAL: odoo auth failed", file=sys.stderr)
        return 1

    done_tag_id = get_or_create_done_tag()

    tasks = kw("project.task", "search_read",
               [[["tag_ids", "in", [DEVOPS_TAG_ID]],
                 ["stage_id", "=", BACKLOG_STAGE_ID],
                 ["tag_ids", "not in", [done_tag_id]]]],
               {"fields": ["id", "name", "description"], "order": "id asc", "limit": 5})
    if not tasks:
        return 0

    for task in tasks:
        text = f"{task['name']}\n\n{strip_html(task.get('description') or '')}".strip()
        print(f"task {task['id']}: {task['name'][:120]!r}")
        try:
            try:
                reply = ask_agent(
                    f"[Odoo DevOps-Agent Task #{task['id']}] {text}",
                    session_key=f"odoo-devops-{task['id']}",
                )
                body = f"🤖 ServAssi:<br/>{html.escape(reply).replace(chr(10), '<br/>')}"
            except Exception as exc:  # noqa: BLE001 - report failure into the chatter
                print(f"agent error: {exc}", file=sys.stderr)
                body = ("⚠️ Ich konnte diesen Task gerade nicht verarbeiten "
                         f"(technischer Fehler). Details im Log auf CT150.")
            kw("project.task", "message_post", [[task["id"]]],
               {"body": body, "message_type": "comment", "subtype_xmlid": "mail.mt_comment"})
            kw("project.task", "write", [[task["id"]], {"tag_ids": [(4, done_tag_id)]}])
            print(f"handled task {task['id']} ({len(body)} chars)")
        except Exception as exc:  # noqa: BLE001 - a single vanished/broken record must not kill the run
            print(f"skipping task {task['id']}: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
