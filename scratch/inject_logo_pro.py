import subprocess
import base64

# Path to the logo on StudioPC
logo_path = r'C:\WORKSPACE\FraWo\lifeboat\assets\logo.png'

with open(logo_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# SQL Command
sql = f"UPDATE res_company SET logo_web = '{encoded_string}' WHERE id = 1;"

# Execute via SSH to PVE then qm guest exec
# We use a temporary file on the PVE host to avoid command line length limits
temp_sql_file = "/tmp/logo_update.sql"

# 1. Write SQL to PVE host
subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "root@100.69.179.87", f"echo \"{sql}\" > {temp_sql_file}"], check=True)

# 2. Execute SQL in VM 220
cmd = f"qm guest exec 220 -- bash -c \"docker exec -i odoo-db-1 psql -U odoo -d FraWo_GbR < {temp_sql_file}\""
subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "root@100.69.179.87", cmd], check=True)

print("Logo successfully updated in Odoo DB.")
