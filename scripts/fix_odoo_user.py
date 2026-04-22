user = env['res.users'].search([('login', '=', 'agent@frawo-tech.de')])
if user:
    print(f"Found user {user.name} (ID: {user.id})")
    group_user = env.ref('base.group_user')
    group_system = env.ref('base.group_system')
    if group_user not in user.groups_id:
        user.write({'groups_id': [(4, group_user.id)]})
        print("Added base.group_user")
    if group_system not in user.groups_id:
        user.write({'groups_id': [(4, group_system.id)]})
        print("Added base.group_system")
    user.write({'active': True})
    print("User is now active and has permissions.")
    env.cr.commit()
else:
    print("User agent@frawo-tech.de not found.")
