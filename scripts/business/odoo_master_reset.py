import subprocess
import base64

# Configuration
NODE_IP = "100.69.179.87" # Anker Host
VMID = "220" # Odoo VM
DB_LIST = ["FraWo_Live", "FraWo_GbR", "FraWo_GbR_Backup", "Recovery_DB"]
NEW_PASS = "admin"

def reset_passwords():
    print(f"Starting Master Odoo Password Reset on Host {NODE_IP}...")
    
    for db in DB_LIST:
        print(f"Processing Database: {db}...")
        # Construct exact SQL command
        sql = f"UPDATE res_users SET password='{NEW_PASS}' WHERE login='admin';"
        
        # We need a clean command that doesn't trigger shell escaping in Python -> SSH -> QM -> Docker -> Psql
        # Better: QM Guest Exec with target binary and args
        
        # Direct implementation using python3 inside the VM to avoid SHELL issues
        sql_escaped = sql.replace("'", "'\\''")
        remote_cmd = f"ssh -p 22 root@{NODE_IP} \"qm guest exec {VMID} -- /usr/bin/python3 -c \\\"import subprocess; subprocess.run(['/usr/bin/docker', 'exec', 'odoo_db_1', 'psql', '-U', 'odoo', '-d', '{db}', '-c', '{sql}'])\\\"\""
        
        try:
            result = subprocess.run(remote_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f" -> SUCCESS: {db} password updated.")
            else:
                print(f" -> ERROR on {db}: {result.stderr}")
        except Exception as e:
            print(f" -> FAILED to execute on {db}: {e}")

if __name__ == "__main__":
    reset_passwords()
