# Odoo Shell Script to set task states to 'really done' (1_done / done) for all tasks in the "Erledigt" stage.
project = env['project.project'].search([('name', 'ilike', 'Masterplan')], limit=1)
if not project:
    print("Project not found")
else:
    stage = env['project.task.type'].search([('project_ids', 'in', project.id), ('name', 'ilike', 'Erledigt')], limit=1)
    if not stage:
        print("Stage 'Erledigt' not found")
    else:
        print(f"Project: {project.name}")
        print(f"Stage: {stage.name} (id={stage.id})")
        tasks = env['project.task'].search([('project_id', '=', project.id), ('stage_id', '=', stage.id)])
        print(f"Found {len(tasks)} tasks in the '{stage.name}' stage.")
        
        updated_count = 0
        for task in tasks:
            updated = False
            vals = {}
            
            if 'state' in env['project.task']._fields and task.state != '1_done':
                vals['state'] = '1_done'
                updated = True
                
            if 'kanban_state' in env['project.task']._fields and task.kanban_state != 'done':
                vals['kanban_state'] = 'done'
                updated = True
                
            if updated:
                task.write(vals)
                print(f"Updated Task {task.id} | {task.name} -> state: 1_done, kanban_state: done")
                updated_count += 1
            else:
                print(f"Task {task.id} | {task.name} is already fully marked as done.")
                
        if updated_count > 0:
            env.cr.commit()
            print(f"Successfully committed updates for {updated_count} tasks.")
        else:
            print("No tasks needed updating.")
