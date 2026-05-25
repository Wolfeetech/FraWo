import os
import sys
import re
import base64
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath('.'))

from scripts.business.odoo_rpc_client import connect

CANONICAL_PROJECT_NAME = "🚀 Homeserver 2027: Masterplan"
DOCUMENTATION_TASK_NAME = "📚 System-Dokumentation & SSOT (Masterplan, Live-Context, Status)"
WOLF_LOGIN = "wolf@frawo-tech.de"
AGENT_LOGIN = "agent@frawo-tech.de"

def md_to_html(md_text):
    # Simple converter for formatting documentation nicely in Odoo
    html = md_text
    # Escape HTML special chars
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Code blocks
    html = re.sub(r'```(\w*)\n(.*?)\n```', r'<pre style="background: #f4f4f4; padding: 10px; border-left: 3px solid #ccc; font-family: monospace; overflow-x: auto;">\2</pre>', html, flags=re.DOTALL)
    
    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1 style="color: #064e3b; border-bottom: 2px solid #064e3b; padding-bottom: 5px;">\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2 style="color: #a855f7; border-bottom: 1px solid #ddd; padding-bottom: 3px;">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3 style="color: #374151;">\1</h3>', html, flags=re.MULTILINE)
    
    # Bullet points
    html = re.sub(r'^\s*-\s+\[ \]\s+(.*?)$', r'<li style="list-style-type: none;">☐ \1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\s*-\s+\[x\]\s+(.*?)$', r'<li style="list-style-type: none; color: #10b981; font-weight: bold;">☑ \1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\s*-\s+(.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Inline formatting
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'`(.*?)`', r'<code style="background: #eee; padding: 2px 4px; font-family: monospace; border-radius: 3px;">\1</code>', html)
    
    # Tables
    # Simple line-by-line replacement for markdown tables
    lines = html.split('\n')
    in_table = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('|') and '|' in line:
            if not in_table:
                new_lines.append('<table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd; margin: 10px 0;">')
                in_table = True
            
            # Skip separator line (e.g. |---|---|)
            if re.match(r'^\s*\|\s*:-*-:|:-*-:|-*-', line) or '---' in line:
                continue
                
            cols = [col.strip() for col in line.split('|')[1:-1]]
            new_lines.append('<tr>')
            for col in cols:
                tag = 'th' if not new_lines[-2].startswith('<tr>') and in_table else 'td'
                bg = ' style="background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 8px;"' if tag == 'th' else ' style="border: 1px solid #ddd; padding: 8px;"'
                new_lines.append(f'<{tag}{bg}>{col}</{tag}>')
            new_lines.append('</tr>')
        else:
            if in_table:
                new_lines.append('</table>')
                in_table = False
            new_lines.append(line)
    if in_table:
        new_lines.append('</table>')
    html = '\n'.join(new_lines)
    
    # Convert line breaks
    html = html.replace('\n', '<br/>')
    return html

def main():
    print("Starte Odoo Dokumentations-Synchronisation...")
    session = connect(default_user=WOLF_LOGIN, prompt_for_username=False)
    print(f"Verbunden mit Odoo ({session.url}) | DB: {session.db}")
    
    # 1. Finde das Masterplan-Projekt
    project_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.project', 'search',
        [[['name', 'ilike', 'Masterplan']]]
    )
    if not project_ids:
        print("Masterplan Projekt existiert nicht! Lege es an...")
        project_id = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.project', 'create',
            [{'name': CANONICAL_PROJECT_NAME, 'privacy_visibility': 'employees'}]
        )
    else:
        project_id = project_ids[0]
        print(f"Masterplan Projekt gefunden (ID: {project_id})")

    # 2. Finde die Planungs-Stage
    stage_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.task.type', 'search',
        [[['project_ids', 'in', [project_id]], ['name', 'ilike', 'Planung']]]
    )
    stage_id = stage_ids[0] if stage_ids else False

    # 3. Finde Wolf und Agent
    user_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'res.users', 'search',
        [[['login', 'in', [WOLF_LOGIN, AGENT_LOGIN]]]]
    )
    # Map user id
    wolf_id = None
    agent_id = None
    users = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'res.users', 'read',
        [user_ids, ['login']]
    )
    for u in users:
        if u['login'] == WOLF_LOGIN:
            wolf_id = u['id']
        elif u['login'] == AGENT_LOGIN:
            agent_id = u['id']
            
    assignees = []
    if wolf_id: assignees.append(wolf_id)
    if agent_id: assignees.append(agent_id)

    # 4. Lies Dokumente ein
    docs = {
        "MASTERPLAN.md": "MASTERPLAN.md",
        "LIVE_CONTEXT.md": "LIVE_CONTEXT.md",
        "STATUS.md": "STATUS.md"
    }
    
    html_sections = []
    for title, filename in docs.items():
        if os.path.exists(filename):
            print(f"Lese {filename}...")
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            html_sections.append(f'<div style="border: 2px solid #ccc; padding: 15px; margin-bottom: 20px; border-radius: 5px; background-color: #fafafa;">')
            html_sections.append(f'<h1 style="background-color: #064e3b; color: white; padding: 10px; margin-top: 0; border-radius: 3px;">📖 {title}</h1>')
            html_sections.append(md_to_html(content))
            html_sections.append('</div>')
        else:
            print(f"Warnung: {filename} existiert nicht.")
            
    full_html = "".join(html_sections)
    
    # 5. Finde oder erstelle den Dokumentations-Task
    task_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.task', 'search',
        [[['project_id', '=', project_id], ['name', '=', DOCUMENTATION_TASK_NAME]]]
    )
    
    task_payload = {
        'name': DOCUMENTATION_TASK_NAME,
        'project_id': project_id,
        'description': full_html,
        'user_ids': [(6, 0, assignees)],
    }
    if stage_id:
        task_payload['stage_id'] = stage_id
        
    if task_ids:
        task_id = task_ids[0]
        print(f"Aktualisiere bestehenden Dokumentations-Task (ID: {task_id})...")
        session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.task', 'write',
            [[task_id], task_payload]
        )
    else:
        print("Erstelle neuen Dokumentations-Task...")
        task_id = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.task', 'create',
            [task_payload]
        )
        print(f"Task erstellt (ID: {task_id})")
        
    # 6. Lade Markdown-Dateien als Attachments hoch
    for title, filename in docs.items():
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                file_data = f.read()
            encoded_data = base64.b64encode(file_data).decode('utf-8')
            
            # Check if attachment already exists on this task
            attachment_ids = session.models.execute_kw(
                session.db, session.uid, session.secret,
                'ir.attachment', 'search',
                [[['res_model', '=', 'project.task'], ['res_id', '=', task_id], ['name', '=', filename]]]
            )
            
            attachment_payload = {
                'name': filename,
                'datas': encoded_data,
                'res_model': 'project.task',
                'res_id': task_id,
                'type': 'binary'
            }
            
            if attachment_ids:
                print(f"Aktualisiere Anhang {filename}...")
                session.models.execute_kw(
                    session.db, session.uid, session.secret,
                    'ir.attachment', 'write',
                    [[attachment_ids[0]], attachment_payload]
                )
            else:
                print(f"Erstelle Anhang {filename}...")
                session.models.execute_kw(
                    session.db, session.uid, session.secret,
                    'ir.attachment', 'create',
                    [attachment_payload]
                )
                
    print("Dokumentations-Synchronisation erfolgreich abgeschlossen!")

if __name__ == "__main__":
    main()
