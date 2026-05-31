# Odoo Shell Script to query and list all tasks and stages
project = env['project.project'].search([('name', 'ilike', 'Masterplan')], limit=1)
if not project:
    print("Project 'Masterplan' not found!")
    # Let's list all projects just in case
    for p in env['project.project'].search([]):
        print(f"Available Project: {p.name} (id={p.id})")
else:
    print(f"Project: {project.name} (id={project.id})")
    print("\n--- Stages in Project ---")
    stages = project.type_ids
    for stage in stages:
        print(f"Stage ID: {stage.id} | Name: {stage.name} | Sequence: {stage.sequence}")

    print("\n--- Tasks in Project ---")
    tasks = env['project.task'].search([('project_id', '=', project.id)])
    for task in tasks:
        stage_name = task.stage_id.name if task.stage_id else "No Stage"
        print(f"Task ID: {task.id} | Name: {task.name} | Stage: {stage_name} | Priority: {task.priority}")
