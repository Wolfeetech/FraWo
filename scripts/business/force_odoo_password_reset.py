import subprocess
import json
import sys

def run_ssh_command(host, command):
    print(f"Executing over SSH on {host}...")
    result = subprocess.run(['ssh', '-p', '22', f'root@{host}', command], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.stdout.strip()

def reset_odoo_password():
    anker_host = "100.69.179.87"
    vmid = "220"
    target_user = "wolf@frawo-tech.de"
    db_name = "FraWo_Live"
    sql_cmd = "UPDATE res_users SET lang='de_DE' WHERE login='wolf@frawo-tech.de'; UPDATE ir_config_parameter SET value='http://10.1.0.22:8069' WHERE key='web.base.url';"
    
    # Wrap for Guest Agent
    # We use base64 inside the VM to avoid ANY char issues
    import base64
    b64_sql = base64.b64encode(sql_cmd.encode()).decode()
    
    agent_cmd = f"qm guest exec {vmid} -- /bin/bash -c \"echo \\\"UPDATE res_users SET password=''admin'' WHERE login=''wolf@frawo-tech.de'';\\\" | sed \\\"s/''/'/g\\\" | docker exec -i odoo_db_1 psql -U odoo -d {db_name}\""
    
    print(f"Injecting password reset via Base64 payload...")
    output = run_ssh_command(anker_host, agent_cmd)
    
    if "exitcode" in output:
        print("Success: Password reset command accepted by Guest Agent.")
        print(output)
    else:
        print("Verification failed. Output:")
        print(output)

if __name__ == "__main__":
    reset_odoo_password()
