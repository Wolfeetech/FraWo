company = env['res.company'].search([], limit=1)
print(f"Company Email: {company.email}")
admin = env['res.users'].search([('login', '=', 'admin')], limit=1)
print(f"Admin Email: {admin.email}")
