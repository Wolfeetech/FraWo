with open('scripts/sync_website_project_to_odoo.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("'priority': '2'", "'priority': '1'")

with open('scripts/sync_website_project_to_odoo.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('priority fixed!')
