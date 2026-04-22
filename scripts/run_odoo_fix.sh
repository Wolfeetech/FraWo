qm guest exec 220 -- bash -c "docker exec -i odoo-web-1 odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=odoo_db_pass_final_v1 --no-http" <<INNER
user = env['res.users'].search([('login', '=', 'agent@frawo-tech.de')])
if user:
    print('Found user ID %s' % user.id)
    user.write({'groups_id': [(4, env.ref('base.group_user').id), (4, env.ref('base.group_system').id)], 'active': True})
    env.cr.commit()
    print('FIXED')
else:
    print('NOT FOUND')
INNER
