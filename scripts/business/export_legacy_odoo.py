import psycopg2
import json

DB_USER = 'odoo'
DB_PASS = 'odoo_db_pass_final_v1'
DB_HOST = 'db'
SOURCE_DBS = ['FraWo_Live', 'Recovery_DB']
OUTPUT_FILE = '/tmp/odoo_migration_data.json'

data = []

for db in SOURCE_DBS:
    print(f"Exporting from {db}...")
    try:
        conn = psycopg2.connect(dbname=db, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()
        
        # Check if kanban_state or state exists
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'project_task' AND column_name IN ('kanban_state', 'state')")
        state_col = cur.fetchone()[0]
        
        query = f"""
            SELECT p.name as proj_name, t.name as task_name, t.description, t.priority, t.{state_col}, t.stage_id
            FROM project_task t 
            JOIN project_project p ON t.project_id = p.id
        """
        cur.execute(query)
        tasks = cur.fetchall()
        for row in tasks:
            # Handle potential JSONB project names
            p_name = row[0]
            if isinstance(p_name, dict):
                p_name = p_name.get('en_US', p_name.get('de_DE', str(p_name)))
            elif isinstance(p_name, str) and p_name.startswith('{'):
                try: p_name = json.loads(p_name).get('en_US', p_name)
                except: pass
            
            data.append({
                'source_db': db,
                'project_name': p_name,
                'task_name': row[1],
                'description': row[2],
                'priority': row[3],
                'state': row[4],
                'stage_id': row[5]
            })
        conn.close()
    except Exception as e:
        print(f"Error exporting from {db}: {e}")

with open(OUTPUT_FILE, 'w') as f:
    json.dump(data, f)
print(f"Successfully exported {len(data)} tasks to {OUTPUT_FILE}")
