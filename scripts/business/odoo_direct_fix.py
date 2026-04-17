import os
import subprocess

# Configuration
NODE_IP = "100.69.179.87" # Anker Host (Internal Tailscale)
VM_ID = "220" # Odoo VM
DB_LIST = ["FraWo_Live", "FraWo_GbR", "FraWo_GbR_Backup", "Recovery_DB"]
NEW_PASS = "admin"

def odoo_direct_fix():
    print(f"Starting Absolute Odoo Fix on Node {NODE_IP}...")
    
    # 1. Unify Passwords via direct SQL
    for db in DB_LIST:
        print(f"[{db}] Synchronizing credentials...")
        sql = f"UPDATE res_users SET password='{NEW_PASS}' WHERE login='admin';"
        # We wrap this in a single-quote payload for the VM execute
        vm_exec = f"docker exec odoo_db_1 psql -U odoo -d {db} -c \"{sql}\""
        cmd = f"ssh -o StrictHostKeyChecking=no -p 22 root@{NODE_IP} qm guest exec {VM_ID} -- /bin/bash -c '{vm_exec}'"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f" -> SUCCESS: {db} credentials unified.")
        else:
            print(f" -> FAILED: {result.stderr}")

    # 2. Activate Discount Feature in FraWo_GbR (Primary Browser DB)
    print("\n[FraWo_GbR] Activating 'Discount' Feature...")
    # SQL to enable group_discount_per_so_line for all internal users
    sql_discount = "INSERT INTO res_groups_users_rel (gid, uid) SELECT g.id, u.id FROM res_groups g, res_users u WHERE g.name = 'Discount on lines' AND u.login = 'wolf@frawo-tech.de' ON CONFLICT DO NOTHING;"
    vm_exec_discount = f"docker exec odoo_db_1 psql -U odoo -d FraWo_GbR -c \"{sql_discount}\""
    cmd_discount = f"ssh -o StrictHostKeyChecking=no -p 22 root@{NODE_IP} qm guest exec {VM_ID} -- /bin/bash -c '{vm_exec_discount}'"
    
    result = subprocess.run(cmd_discount, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(" -> SUCCESS: Invoice Discounts activated.")
    else:
        print(f" -> FAILED: {result.stderr}")

if __name__ == "__main__":
    odoo_direct_fix()
