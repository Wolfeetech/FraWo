import argparse
import sys
from odoo_rpc_client import connect

def get_session():
    try:
        return connect()
    except Exception as e:
        print(f"Verbindungsfehler: {e}")
        sys.exit(1)

def list_projects():
    session = get_session()
    # Assuming 'project.project' is the Odoo model for projects
    try:
        project_ids = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.project', 'search',
            [[('active', '=', True)]]
        )
        if not project_ids:
            print("Keine aktiven Projekte gefunden.")
            return

        projects = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.project', 'read',
            [project_ids],
            {'fields': ['id', 'name', 'task_count']}
        )
        
        print("| ID | Name | Offene Aufgaben |")
        print("|---|---|---|")
        for p in projects:
            task_count = p.get('task_count', 0)
            print(f"| {p.get('id')} | {p.get('name')} | {task_count} |")
    except Exception as e:
        print(f"Fehler beim Abrufen der Projekte: {e}")

def create_project(name, description=""):
    session = get_session()
    try:
        new_project_id = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.project', 'create',
            [{
                'name': name,
                'description': description
            }]
        )
        print(f"Projekt erfolgreich erstellt. ID: {new_project_id}")
    except Exception as e:
        print(f"Fehler beim Erstellen des Projekts: {e}")

def list_tasks(project_identifier):
    session = get_session()
    try:
        # Check if project_identifier is an ID or name
        domain = []
        if project_identifier.isdigit():
            domain = [('project_id', '=', int(project_identifier))]
        else:
            domain = [('project_id.name', 'ilike', project_identifier)]
            
        task_ids = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.task', 'search',
            [domain]
        )
        
        if not task_ids:
            print(f"Keine Aufgaben gefunden für Projekt '{project_identifier}'.")
            return

        tasks = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.task', 'read',
            [task_ids],
            {'fields': ['id', 'name', 'stage_id', 'user_ids']}
        )
        
        print(f"| ID | Task | Stage | Zuweisung |")
        print(f"|---|---|---|---|")
        for t in tasks:
            stage = t.get('stage_id', [0, 'Unbekannt'])[1] if t.get('stage_id') else 'Unbekannt'
            users = ", ".join([u[1] for u in t.get('user_ids', [])]) if t.get('user_ids') else 'Nicht zugewiesen'
            print(f"| {t.get('id')} | {t.get('name')} | {stage} | {users} |")
            
    except Exception as e:
        print(f"Fehler beim Abrufen der Aufgaben: {e}")

def create_task(project_identifier, name, description=""):
    session = get_session()
    try:
        project_id = None
        if project_identifier.isdigit():
            project_id = int(project_identifier)
        else:
            p_ids = session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.project', 'search',
                [[('name', 'ilike', project_identifier)]],
                {'limit': 1}
            )
            if not p_ids:
                print(f"Projekt '{project_identifier}' nicht gefunden.")
                return
            project_id = p_ids[0]

        new_task_id = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.task', 'create',
            [{
                'name': name,
                'project_id': project_id,
                'description': description
            }]
        )
        print(f"Aufgabe erfolgreich erstellt. ID: {new_task_id}")
    except Exception as e:
        print(f"Fehler beim Erstellen der Aufgabe: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Odoo Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Befehle")

    parser_list_proj = subparsers.add_parser("list-projects")
    
    parser_create_proj = subparsers.add_parser("create-project")
    parser_create_proj.add_argument("name", help="Name des Projekts")
    parser_create_proj.add_argument("description", nargs="?", default="", help="Beschreibung")

    parser_list_tasks = subparsers.add_parser("list-tasks")
    parser_list_tasks.add_argument("project", help="Name oder ID des Projekts")

    parser_create_task = subparsers.add_parser("create-task")
    parser_create_task.add_argument("project", help="Name oder ID des Projekts")
    parser_create_task.add_argument("name", help="Name der Aufgabe")
    parser_create_task.add_argument("description", nargs="?", default="", help="Beschreibung der Aufgabe")

    args = parser.parse_args()

    if args.command == "list-projects":
        list_projects()
    elif args.command == "create-project":
        create_project(args.name, args.description)
    elif args.command == "list-tasks":
        list_tasks(args.project)
    elif args.command == "create-task":
        create_task(args.project, args.name, args.description)
    else:
        parser.print_help()
