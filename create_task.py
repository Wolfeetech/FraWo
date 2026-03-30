import sys

try:
    # Handle the Odoo Shell environment
    task_model = env['project.task']
    task = task_model.create({
        'name': 'Endgeräte Franz onboarden',
        'description': '<ul><li>[ ] Surface Go aushändigen und Passwörter testen</li><li>[ ] Nextcloud Mail-App Testnachricht senden</li><li>[ ] AnyDesk-ID verifizieren</li><li>[ ] Portal als Startseite in Kiosk-Mode fixieren</li></ul>',
    })
    env.cr.commit()
    print(f"Task created successfully with ID {task.id}")
except Exception as e:
    print(f"Failed to create task: {e}")
