import os
import subprocess

# Configuration
NODE_IP = "100.69.179.87"
VM_ID = "220"
TARGET_DB = "FraWo_GbR"
WOLF_ID = 6

def unbreakable_transfer():
    print(f"Starting Unbreakable Data Bridge to {TARGET_DB}...")
    
    # 1. Definitive SQL Payload
    sql_payload = """
-- Mission Recovery Script
-- Lane IDs (Verified in Previous UI Audits)

-- Heritage & History (Lane A)
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'Lane A: Heritage & History' LIMIT 1), user_ids = array[7], active = true
WHERE name ILIKE '%Gründung%' OR name ILIKE '%Notar%' OR name ILIKE '%Heritage%';

-- Website & Public Edge (Lane B)
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'Lane B: Website & Public Edge' LIMIT 1), user_ids = array[7], active = true
WHERE name ILIKE '%Website%' OR name ILIKE '%Cloudflare%' OR name ILIKE '%Caddy%' OR name ILIKE '%Domain%';

-- Security & PBS (Lane C)
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'Lane C: Security & PBS' LIMIT 1), user_ids = array[7], active = true
WHERE name ILIKE '%Security%' OR name ILIKE '%Backup%' OR name ILIKE '%PBS%' OR name ILIKE '%Vaultwarden%';

-- Stockenweiler (Lane D)
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'Lane D: Stockenweiler Migration' LIMIT 1), user_ids = array[7], active = true
WHERE name ILIKE '%Stockenweiler%' OR name ILIKE '%Remote%' OR name ILIKE '%Hardware%';

-- Everything Else -> Homeserver
UPDATE project_task SET project_id = (SELECT id FROM project_project WHERE name = 'FraWo Homeserver 2027' LIMIT 1), user_ids = array[7], active = true
WHERE project_id IS NULL OR project_id NOT IN (SELECT id FROM project_project WHERE name LIKE 'Lane %');

-- Ensure Starred for Wolf (User 7 IS the active wolf ID from UI check)
UPDATE project_project SET favorite_user_ids = array_append(favorite_user_ids, 7) WHERE NOT 7 = ANY(COALESCE(favorite_user_ids, ARRAY[]::integer[]));
"""
    
    local_path = "c:\\Users\\StudioPC\\Workspace\\FraWo\\scripts\\business\\recovery_bridge.sql"
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(sql_payload)
        
    print("Uploading SQL payload via SCP...")
    scp_cmd = f"scp -o StrictHostKeyChecking=no -P 22 {local_path} root@{NODE_IP}:/tmp/recovery_bridge.sql"
    subprocess.run(scp_cmd, shell=True)
    
    print("Executing injection on Host -> VM...")
    # Inject using file-stream to avoid any shell interpretation
    inject_cmd = f"ssh -o StrictHostKeyChecking=no -p 22 root@{NODE_IP} 'qm guest exec {VM_ID} -- /usr/bin/docker exec -i odoo_db_1 psql -U odoo -d {TARGET_DB}' < /tmp/recovery_bridge.sql"
    result = subprocess.run(inject_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Success: Cockpit filled and categorized.")
        print(result.stdout)
    else:
        print(f"Error: {result.stderr}")

if __name__ == "__main__":
    unbreakable_transfer()
