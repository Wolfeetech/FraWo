import subprocess
# Replace all HTML entities with real UTF-8 characters in the DB directly via psql
sql = '''
UPDATE ir_ui_view 
SET arch_db = replace(
  replace(
    replace(
      replace(
        replace(
          replace(
            replace(arch_db::text, '&uuml;', u'\u00fc'),
            '&auml;', u'\u00e4'),
          '&ouml;', u'\u00f6'),
        '&Uuml;', u'\u00dc'),
      '&Auml;', u'\u00c4'),
    '&Ouml;', u'\u00d6'),
  '&szlig;', u'\u00df')::xml
WHERE id IN (3644, 3637);
'''
r = subprocess.run(
    ['docker', 'exec', '-e', 'PGPASSWORD=odoo_db_pass_final_v1', 'odoo_db_1',
     'psql', '-U', 'odoo', '-d', 'FraWo_GbR', '-c', sql],
    capture_output=True, text=True
)
print('stdout:', r.stdout)
print('stderr:', r.stderr[:200])