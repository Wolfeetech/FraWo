import psycopg2
import json

# Connection parameters
DB_USER = 'odoo'
DB_HOST = '10.1.0.22'  # We will run this via docker exec on the db container, so localhost there
DB_PORT = '5432'

SOURCE_DBS = ['FraWo_Live', 'Recovery_DB']
TARGET_DB = 'FraWo_GbR'

# Mapping Strategy from Plan
# Project IDs in FraWo_GbR:
# 1: Masterplan
# 2: Lane A (Heritage)
# 3: Lane B (Website)
# 4: Lane C (Security)
# 5: Lane D (Stockenweiler)
# 7: Lane Z (Archive) - Needs to be created if not exists

MAPPING = {
    # Recovery_DB 
    "🚀 Homeserver 2027: Masterplan": 1,
    
    # FraWo_Live
    "Lane B: Website & Public Edge": 3,
    "Website & Public Edge": 3,
    "Lane A: Heritage & History": 2,
    "FraWo GbR - Heritage & History": 2,
    "Heritage & Founding": 2,
    "Security & PBS": 4,
    "Lane C: Security & PBS": 4,
    "Stockenweiler Migration": 5,
    "Lane D: Stockenweiler Migration": 5,
    "FraWo Homeserver 2027": 1,
    
    # Standard/Archive Tasks
    "Office Design": 7,
    "Home Make Over": 7,
    "Renovations": 7,
    "Research & Development": 1, # Moving R&D to Masterplan as it fits infrastructure
}

def migrate():
    try:
        # Connect to target first to ensure project 7 exists
        target_conn = psycopg2.connect(dbname=TARGET_DB, user=DB_USER, host='localhost', port=DB_PORT)
        target_cur = target_conn.cursor()
        
        # Ensure Archive Project exists
        target_cur.execute("SELECT id FROM project_project WHERE id = 7")
        if not target_cur.fetchone():
            print("Creating Lane Z: Archive...")
            target_cur.execute("""
                INSERT INTO project_project (id, name, active, color, company_id, privacy_visibility) 
                VALUES (7, '{"de_DE": "Lane Z: Archiv / Historie", "en_US": "Lane Z: Archive / Legacy"}', true, 1, 1, 'followers')
            """)
            target_conn.commit()

        for source_db in SOURCE_DBS:
            print(f"--- Migrating from {source_db} ---")
            source_conn = psycopg2.connect(dbname=source_db, user=DB_USER, host='localhost', port=DB_PORT)
            source_cur = source_conn.cursor()
            
            # Fetch all projects and tasks
            source_cur.execute("SELECT id, name FROM project_project")
            projects = source_cur.fetchall()
            
            for p_id, p_name_raw in projects:
                # Odoo stores names as JSONB or multi-lang strings
                p_name = p_name_raw
                if isinstance(p_name_raw, dict):
                    p_name = p_name_raw.get('en_US', p_name_raw.get('de_DE', str(p_name_raw)))
                elif isinstance(p_name_raw, str) and p_name_raw.startswith('{'):
                    try:
                        p_data = json.loads(p_name_raw)
                        p_name = p_data.get('en_US', p_data.get('de_DE', p_name_raw))
                    except: pass
                
                target_p_id = MAPPING.get(p_name, 7) # Default to Archive
                
                print(f"Migrating tasks from project '{p_name}' -> Target ID {target_p_id}")
                
                source_cur.execute("SELECT name, description, user_id, stage_id, kanban_state, priority FROM project_task WHERE project_id = %s", (p_id,))
                tasks = source_cur.fetchall()
                
                for t_name, t_desc, t_user, t_stage, t_kanban, t_prio in tasks:
                    # User ID 6 is 'Wolf' in FraWo_GbR
                    target_cur.execute("""
                        INSERT INTO project_task (name, description, project_id, user_id, stage_id, kanban_state, priority, active, company_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, true, 1)
                    """, (t_name, t_desc, 6, t_stage, t_kanban, t_prio))
            
            source_conn.close()
            target_conn.commit()
            print(f"Finished migration from {source_db}")

        target_conn.close()
        print("Migration complete!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    migrate()
