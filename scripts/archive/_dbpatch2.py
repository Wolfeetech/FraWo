import subprocess
sql = "UPDATE ir_ui_view SET arch_db = replace(replace(replace(replace(replace(replace(replace(arch_db::text, '&uuml;', '\xc3\xbc'), '&auml;', '\xc3\xa4'), '&ouml;', '\xc3\xb6'), '&Uuml;', '\xc3\x9c'), '&Auml;', '\xc3\x84'), '&Ouml;', '\xc3\x96'), '&szlig;', '\xc3\x9f')::xml WHERE id IN (3644, 3637);"
r = subprocess.run(["docker","exec","-e","PGPASSWORD=odoo_db_pass_final_v1","odoo_db_1","psql","-U","odoo","-d","FraWo_GbR","-c",sql], capture_output=True, text=True)
print("out:", r.stdout)
print("err:", r.stderr[:300])