# Odoo Shell Script to inspect done tasks in detail
project = env['project.project'].search([('name', 'ilike', 'Masterplan')], limit=1)
if not project:
    print("Project not found")
else:
    stage = env['project.task.type'].search([('project_ids', 'in', project.id), ('name', 'ilike', 'Erledigt')], limit=1)
    if not stage:
        print("Stage 'Erledigt' not found")
    else:
        print(f"Stage: {stage.name} (id={stage.id})")
        tasks = env['project.task'].search([('project_id', '=', project.id), ('stage_id', '=', stage.id)])
        print(f"Found {len(tasks)} tasks in '{stage.name}' stage.")
        
        # Let's inspect the first task to see all fields related to status
        if tasks:
            task = tasks[0]
            fields_to_check = ['name', 'kanban_state', 'active', 'state']
            available_fields = [f for f in fields_to_check if f in env['project.task']._fields]
            print(f"Checking fields: {available_fields}")
            
            for t in tasks:
                vals = []
                for f in available_fields:
                    vals.append(f"{f}: {getattr(t, f)}")
                print(f"Task {t.id} | " + " | ".join(vals))
