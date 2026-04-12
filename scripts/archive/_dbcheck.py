import subprocess
r = subprocess.run(['docker', 'exec', 'odoo_db_1', 'psql', '-U', 'odoo', '-d', 'FraWo_GbR', '-c', 'SELECT left(arch_db::text, 50) FROM ir_ui_view WHERE id=3644'], capture_output=True, text=True)
print(repr(r.stdout[:400]))