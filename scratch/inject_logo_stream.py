import subprocess
import base64
import os

# Path to the logo on StudioPC
logo_path = r'C:\WORKSPACE\FraWo\lifeboat\assets\logo.png'
temp_sql_pc = 'logo_update.sql'

with open(logo_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# SQL Command
sql = f"UPDATE res_company SET logo_web = '{encoded_string}' WHERE id = 1;"

# Write SQL to local temp file
with open(temp_sql_pc, 'w', encoding='utf-8') as f:
    f.write(sql)

print("Streaming SQL to server...")

# 1. Stream file to PVE host
with open(temp_sql_pc, 'rb') as f:
    subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "root@100.69.179.87", "cat > /tmp/logo_update.sql"], stdin=f, check=True)

# 2. Inject from PVE host into VM 220 (streaming via qm guest exec)
# Note: We use cat and pipe it into qm guest exec
inject_cmd = "cat /tmp/logo_update.sql | qm guest exec 220 -- bash -c 'docker exec -i odoo-db-1 psql -U odoo -d FraWo_GbR'"
subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "root@100.69.179.87", inject_cmd], check=True)

print("Logo successfully streamed and injected into Odoo DB.")

# Cleanup
if os.path.exists(temp_sql_pc):
    os.remove(temp_sql_pc)
