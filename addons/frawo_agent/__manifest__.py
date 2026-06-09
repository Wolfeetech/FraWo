{
    "name": "FraWo Agent",
    "version": "17.0.1.0.0",
    "summary": "Autonomer Task-Agent: formatiert neue Tasks nach CI via lokalem Ollama",
    "author": "FraWo GbR",
    "license": "LGPL-3",
    "depends": ["project", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/config_params.xml",
        "data/agent_queue_tag.xml",
        "data/ir_cron.xml",
        "views/agent_log_views.xml",
    ],
    "post_init_hook": "post_init",
    "application": False,
    "installable": True,
}
