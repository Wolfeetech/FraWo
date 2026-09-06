{
    "name": "FraWo Agent",
    "version": "19.0.1.0.1",
    "summary": "Autonomer Task-Agent: formatiert neue Tasks nach CI via lokalem Ollama",
    "author": "FraWo GbR",
    "license": "LGPL-3",
    "depends": ["project", "mail", "maintenance", "website", "spreadsheet_dashboard"],
    "data": [
        "security/ir.model.access.csv",
        "data/config_params.xml",
        "data/ir_cron.xml",
        "views/agent_log_views.xml",
        "views/anker_tracker_views.xml",
        "views/anker_tracker_templates.xml",
        "views/it_equipment_views.xml",
        "views/radio_vote_views.xml",
        "views/project_task_search_views.xml",
        "views/project_dashboard_views.xml",
        "views/website_homepage_ci3.xml",
    ],
    # Asset-Bündel sind seit Odoo 15 Manifest-Einträge und keine vererbbaren
    # QWeb-Views mehr — <template inherit_id="web.assets_frontend"> bricht ab.
    "assets": {
        "web.assets_frontend": [
            "frawo_agent/static/src/css/ci3_frontend.css",
            "frawo_agent/static/src/js/ci3_frontend.js",
        ],
        "web.assets_backend": [
            "frawo_agent/static/src/css/ci3_backend.css",
        ],
    },
    "post_init_hook": "post_init",
    "application": False,
    "installable": True,
}
