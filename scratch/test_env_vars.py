import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

print("Env Path:", env_path)
print("Env Path Exists:", env_path.exists())
print("ODOO_URL:", os.getenv('ODOO_URL'))
print("ODOO_USER:", os.getenv('ODOO_USER'))
print("ODOO_PASSWORD:", os.getenv('ODOO_PASSWORD'))
print("ODOO_DB_GBR:", os.getenv('ODOO_DB_GBR'))
