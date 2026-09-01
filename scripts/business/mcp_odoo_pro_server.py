#!/usr/bin/env python3
"""
MCP Server for Odoo Pro (FraWo)
Exposes Odoo JSON-RPC as MCP tools for use in Antigravity IDE.

Environment Variables (loaded from .env):
  ODOO_RPC_URL   - e.g. http://10.1.0.112:8069
  ODOO_RPC_DB    - e.g. FraWo_GbR
  ODOO_RPC_USER  - e.g. wolf@frawo.tech
  ODOO_PASSWORD  - password (also checked as ODOO_RPC_PASSWORD)
"""

import os
import sys
import json
import xmlrpc.client
import traceback
from pathlib import Path

# Ensure UTF-8 I/O for MCP communication
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Load .env if present ──────────────────────────────────────────────────────
_env_file = Path("C:/Users/StudioPC/.ai-tools-shared/.env")
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip()
            if k not in os.environ or os.environ[k].startswith("${"):
                os.environ[k] = v

def _clean_val(val):
    if not val or (isinstance(val, str) and val.startswith("${") and val.endswith("}")):
        return None
    return val

ODOO_URL  = _clean_val(os.environ.get("ODOO_RPC_URL")) or _clean_val(os.environ.get("ODOO_URL")) or "http://10.1.0.112:8069"
if not ODOO_URL.startswith("http://") and not ODOO_URL.startswith("https://"):
    ODOO_URL = f"http://{ODOO_URL}"
ODOO_DB   = _clean_val(os.environ.get("ODOO_RPC_DB")) or _clean_val(os.environ.get("ODOO_DB_GBR")) or "FraWo_GbR"
ODOO_USER = _clean_val(os.environ.get("ODOO_RPC_USER")) or _clean_val(os.environ.get("ODOO_USER")) or "agent@frawo.tech"
ODOO_PASS = (_clean_val(os.environ.get("ODOO_RPC_PASSWORD"))
             or _clean_val(os.environ.get("ODOO_PASSWORD")) or "JarvisAgent2026!FraWo")

# ── Odoo XML-RPC helpers ──────────────────────────────────────────────────────
def _connect():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
    uid    = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    if not uid:
        raise RuntimeError(f"Odoo auth failed for {ODOO_USER}@{ODOO_DB} ({ODOO_URL})")
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
    return uid, models

def odoo_execute(model, method, args=None, kwargs=None):
    uid, models = _connect()
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS,
                             model, method,
                             args or [],
                             kwargs or {})

def odoo_search_read(model, domain, fields, limit=50, order="id desc"):
    return odoo_execute(model, "search_read",
                        [domain],
                        {"fields": fields, "limit": limit, "order": order})

# ── MCP protocol (stdio) ──────────────────────────────────────────────────────
def send(obj):
    line = json.dumps(obj, ensure_ascii=False)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()

def err_response(req_id, code, msg):
    send({"jsonrpc": "2.0", "id": req_id,
          "error": {"code": code, "message": msg}})

# ── Tool definitions ──────────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "odoo_get_open_tasks",
        "description": "Get all open tasks from Odoo across all projects (excluding Done/Cancelled stages).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Optional: filter by project name (partial match)"},
                "limit": {"type": "integer", "description": "Max results (default 50)"}
            }
        }
    },
    {
        "name": "odoo_get_project_tasks",
        "description": "Get tasks for a specific Odoo project by name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Project name (partial match)"},
                "stage":        {"type": "string", "description": "Optional stage filter"}
            },
            "required": ["project_name"]
        }
    },
    {
        "name": "odoo_update_task",
        "description": "Update an Odoo task field (e.g. stage, description, date_deadline).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Task ID"},
                "values":  {"type": "object",  "description": "Dict of field->value to write"}
            },
            "required": ["task_id", "values"]
        }
    },
    {
        "name": "odoo_create_task",
        "description": "Create a new task in an Odoo project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_name": {"type": "string"},
                "name":         {"type": "string"},
                "description":  {"type": "string"},
                "stage_name":   {"type": "string"}
            },
            "required": ["project_name", "name"]
        }
    },
    {
        "name": "odoo_get_projects",
        "description": "List all active Odoo projects.",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "odoo_post_task_note",
        "description": "Post a clean internal note or message to an Odoo task chatter. Formats text/HTML cleanly so no raw tags appear.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The Odoo Task ID"},
                "body": {"type": "string", "description": "The note content (plain text, markdown, or clean HTML)"},
                "is_note": {"type": "boolean", "description": "If true (default), posts as internal note. If false, posts as public comment."}
            },
            "required": ["task_id", "body"]
        }
    },
    {
        "name": "odoo_execute_python",
        "description": "Execute arbitrary Python code in Odoo context (env available). Returns printed output.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Python code. Use env['model'].search() etc."}
            },
            "required": ["command"]
        }
    }
]

# ── Tool handlers ─────────────────────────────────────────────────────────────
def handle_odoo_get_open_tasks(args):
    done_stages = ["Done", "Erledigt", "✅ Erledigt", "Abgeschlossen", "Cancelled"]
    domain = [("stage_id.name", "not in", done_stages), ("project_id", "!=", False)]
    if args.get("project_name"):
        domain.append(("project_id.name", "ilike", args["project_name"]))
    limit = args.get("limit", 50)
    tasks = odoo_search_read("project.task", domain,
                             ["name", "project_id", "stage_id", "priority",
                              "date_deadline", "description"],
                             limit=limit, order="priority desc, date_deadline asc")
    lines = []
    for t in tasks:
        lines.append(
            f"#{t['id']} | {t['priority']} | "
            f"{t['project_id'][1] if t['project_id'] else '-'} | "
            f"{t['stage_id'][1] if t['stage_id'] else '-'} | "
            f"{t['name']}"
        )
    return "\n".join(lines) if lines else "No open tasks found."

def handle_odoo_get_project_tasks(args):
    if "project_id" in args:
        proj_ids = [args["project_id"]]
        projs = odoo_search_read("project.project", [("id", "=", args["project_id"])], ["id", "name"])
    else:
        proj_name = args.get("project_name", "")
        projs = odoo_search_read("project.project", [("name", "ilike", proj_name)], ["id","name"], limit=5)
        if not projs:
            return f"No project found matching '{proj_name}'"
        proj_ids = [p["id"] for p in projs]
    
    domain = [("project_id", "in", proj_ids)]
    if args.get("stage"):
        domain.append(("stage_id.name", "ilike", args["stage"]))
    tasks = odoo_search_read("project.task", domain,
                             ["name", "stage_id", "priority", "date_deadline"],
                             limit=100)
    lines = [f"Project(s): {[p['name'] for p in projs]}\n"]

    for t in tasks:
        lines.append(f"  #{t['id']} [{t['stage_id'][1] if t['stage_id'] else '?'}] {t['name']}")
    return "\n".join(lines)

def handle_odoo_update_task(args):
    task_id = int(args["task_id"])
    values  = args["values"]
    # Resolve stage name -> id if needed
    if "stage_id" in values and isinstance(values["stage_id"], str):
        stages = odoo_search_read("project.task.type", [("name", "ilike", values["stage_id"])], ["id","name"], limit=3)
        if stages:
            values["stage_id"] = stages[0]["id"]
    odoo_execute("project.task", "write", [[task_id], values])
    return f"Task #{task_id} updated: {values}"

def handle_odoo_create_task(args):
    proj_name = args["project_name"]
    projs = odoo_search_read("project.project", [("name", "ilike", proj_name)], ["id","name"], limit=3)
    if not projs:
        return f"No project found matching '{proj_name}'"
    proj_id = projs[0]["id"]
    vals = {"name": args["name"], "project_id": proj_id}
    if args.get("description"):
        vals["description"] = args["description"]
    if args.get("stage_name"):
        stages = odoo_search_read("project.task.type", [("name", "ilike", args["stage_name"])], ["id"], limit=3)
        if stages:
            vals["stage_id"] = stages[0]["id"]
    task_id = odoo_execute("project.task", "create", [vals])
    return f"Task created: #{task_id} in '{projs[0]['name']}'"

def handle_odoo_get_projects(args):
    projs = odoo_search_read("project.project", [("active", "=", True)],
                             ["name", "task_count"], limit=100, order="name asc")
    lines = [f"#{p['id']} | {p['name']} ({p.get('task_count',0)} tasks)" for p in projs]
    return "\n".join(lines)

def handle_odoo_execute_python(args):
    """Execute python snippet with env available."""
    code = args["command"]
    import io, contextlib
    uid, models = _connect()
    # Build a minimal env-like proxy
    class _Model:
        def __init__(self, name):
            self._name = name
        def search(self, domain, **kw):
            ids = odoo_execute(self._name, "search", [domain], kw)
            return _RecordSet(self._name, ids)
        def search_read(self, domain, fields, **kw):
            return odoo_execute(self._name, "search_read", [domain], {"fields": fields, **kw})
    class _RecordSet:
        def __init__(self, model, ids):
            self._model = model
            self._ids   = ids
        def __iter__(self):
            recs = odoo_execute(self._model, "read", [self._ids])
            return iter([type("R", (), r)() for r in recs])
        @property
        def id(self): return self._ids[0] if self._ids else None
    class _Env:
        def __getitem__(self, name): return _Model(name)
    buf = io.StringIO()
    local_vars = {"env": _Env(), "odoo_execute": odoo_execute}
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<mcp>", "exec"), local_vars)
        return buf.getvalue() or "(no output)"
    except Exception as e:
        return f"Error: {e}\n{traceback.format_exc()}"

def handle_odoo_post_task_note(args):
    """Post clean chatter note to a task (formats HTML/Markdown so no raw tags show)."""
    import re, html
    task_id = int(args["task_id"])
    body = args["body"].strip()
    is_note = args.get("is_note", True)

    # If it's already structured HTML, ensure it is unescaped
    if body.startswith("<p>") or body.startswith("<div>") or body.startswith("<ul>"):
        clean_body = body
    else:
        # Markdown to clean HTML conversion
        text = html.escape(body)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        lines = text.split('\n')
        in_list = False
        out_lines = []
        for line in lines:
            trimmed = line.strip()
            if trimmed.startswith('- ') or trimmed.startswith('• '):
                if not in_list:
                    out_lines.append('<ul>')
                    in_list = True
                out_lines.append(f'<li>{trimmed[2:]}</li>')
            else:
                if in_list:
                    out_lines.append('</ul>')
                    in_list = False
                if trimmed:
                    out_lines.append(f'<p>{trimmed}</p>')
        if in_list:
            out_lines.append('</ul>')
        clean_body = ''.join(out_lines) if out_lines else f'<p>{text}</p>'

    msg_id = odoo_execute("mail.message", "create", [{
        "model": "project.task",
        "res_id": task_id,
        "body": clean_body,
        "message_type": "comment",
        "subtype_id": 2 if is_note else 1,
    }])
    return f"Chatter note #{msg_id} successfully posted to Task #{task_id}"

HANDLERS = {
    "odoo_get_open_tasks":    handle_odoo_get_open_tasks,
    "odoo_get_project_tasks": handle_odoo_get_project_tasks,
    "odoo_update_task":       handle_odoo_update_task,
    "odoo_create_task":       handle_odoo_create_task,
    "odoo_get_projects":      handle_odoo_get_projects,
    "odoo_post_task_note":    handle_odoo_post_task_note,
    "odoo_execute_python":    handle_odoo_execute_python,
}

# ── Main MCP loop ─────────────────────────────────────────────────────────────
def main():
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
        except json.JSONDecodeError:
            continue

        req_id  = req.get("id")
        method  = req.get("method", "")
        params  = req.get("params", {})

        if method == "initialize":
            send({
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "odoo-pro", "version": "1.0.0"},
                    "capabilities": {"tools": {}}
                }
            })
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments") or params.get("input") or {}
            handler   = HANDLERS.get(tool_name)
            if not handler:
                err_response(req_id, -32601, f"Unknown tool: {tool_name}")
                continue
            try:
                result_text = handler(tool_args)
                send({
                    "jsonrpc": "2.0", "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": str(result_text)}],
                        "isError": False
                    }
                })
            except Exception as e:
                err_response(req_id, -32000, f"{e}\n{traceback.format_exc()}")
        elif method == "ping":
            if req_id is not None:
                send({"jsonrpc": "2.0", "id": req_id, "result": {}})
        elif method == "notifications/initialized" or method.startswith("notifications/"):
            pass  # ignore notifications
        else:
            # Unknown method — ignore silently or send error
            if req_id is not None:
                err_response(req_id, -32601, f"Method not found: {method}")

if __name__ == "__main__":
    main()
