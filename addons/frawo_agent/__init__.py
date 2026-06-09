from . import models


def post_init(env):
    """Cron als Agent-User (UID 7) laufen lassen, damit Chatter als Agent erscheint."""
    agent = env["res.users"].search([("login", "=", "agent@frawo.tech")], limit=1)
    cron = env.ref("frawo_agent.cron_agent_queue", raise_if_not_found=False)
    if agent and cron:
        cron.user_id = agent.id
