# Odoo Shell Script to find the VT-Koffer task
tasks = env['project.task'].search([('name', 'ilike', 'koffer')])
if not tasks:
    tasks = env['project.task'].search([('name', 'ilike', 'streaming')])
if not tasks:
    tasks = env['project.task'].search([('name', 'ilike', 'pi')])

print(f"Found {len(tasks)} matching tasks:")
for task in tasks:
    project_name = task.project_id.name if task.project_id else "No Project"
    stage_name = task.stage_id.name if task.stage_id else "No Stage"
    print(f"Task ID: {task.id}")
    print(f"Name: {task.name}")
    print(f"Project: {project_name}")
    print(f"Stage: {stage_name}")
    print("Description snippet:")
    print(task.description[:500] if task.description else "No Description")
    print("-" * 40)
