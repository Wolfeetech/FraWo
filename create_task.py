runtime_env = globals().get("env")

if runtime_env is None:
    print("Failed to create task: this script must run inside Odoo shell where 'env' is available")
else:
    try:
        task_model = runtime_env["project.task"]
        task = task_model.create(
            {
                "name": "Endgeraete Franz onboarden",
                "description": (
                    "<ul>"
                    "<li>[ ] Surface Go aushaendigen und Passwoerter testen</li>"
                    "<li>[ ] Nextcloud Mail-App Testnachricht senden</li>"
                    "<li>[ ] AnyDesk-ID verifizieren</li>"
                    "<li>[ ] Portal als Startseite im Kiosk-Modus fixieren</li>"
                    "</ul>"
                ),
            }
        )
        runtime_env.cr.commit()
        print(f"Task created successfully with ID {task.id}")
    except Exception as exc:
        print(f"Failed to create task: {exc}")
