import os
import subprocess

# Configuration
NODE_IP = "100.69.179.87"
VM_ID = "220"
DB = "FraWo_GbR"

def final_nuke():
    print(f"Starting Final Odoo Nuke on {DB}...")
    
    sql_content = """
-- 1. Ensure Projects exist
INSERT INTO project_project (name, user_id, active, color) VALUES ('Lane A: Heritage & History', 8, true, 1) ON CONFLICT DO NOTHING;
INSERT INTO project_project (name, user_id, active, color) VALUES ('Lane B: Website & Public Edge', 8, true, 2) ON CONFLICT DO NOTHING;
INSERT INTO project_project (name, user_id, active, color) VALUES ('Lane C: Security & PBS', 8, true, 3) ON CONFLICT DO NOTHING;
INSERT INTO project_project (name, user_id, active, color) VALUES ('Lane D: Stockenweiler Migration', 8, true, 4) ON CONFLICT DO NOTHING;
INSERT INTO project_project (name, user_id, active, color) VALUES ('FraWo Homeserver 2027', 8, true, 5) ON CONFLICT DO NOTHING;

-- 2. Archive legacy masterplan tile
UPDATE project_project SET active = false WHERE name = '🚀 Homeserver 2027: Masterplan';

-- 3. Enable Discounts
INSERT INTO res_groups_users_rel (gid, uid) 
SELECT g.id, 8 FROM res_groups g WHERE g.name = 'Discount on lines' 
ON CONFLICT DO NOTHING;
"""
    
    # Save local temporary SQL file
    local_sql = "c:\\Users\\StudioPC\\Workspace\\FraWo\\scripts\\business\\force_unify.sql"
    with open(local_sql, "w", encoding="utf-8") as f:
        f.write(sql_content)
        
    print("Uploading SQL payload to host...")
    # Upload to host
    scp_cmd = f"scp -P 22 {local_sql} root@{NODE_IP}:/tmp/force_unify.sql"
    subprocess.run(scp_cmd, shell=True)
    
    print("Executing SQL injection inside Odoo VM...")
    # Execute injection
    exec_cmd = f"ssh -p 22 root@{NODE_IP} 'qm guest exec {VM_ID} -- /bin/bash -c \"/usr/bin/docker exec -i odoo_db_1 psql -U odoo -d {DB}\" < /tmp/force_unify.sql'"
    result = subprocess.run(exec_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(" -> SUCCESS: Odoo Cockpit Unified and Discounts Activated.")
        print(result.stdout)
    else:
        print(f" -> ERROR: {result.stderr}")

if __name__ == "__main__":
    final_nuke()
