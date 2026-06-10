from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Erzwingt den Cron-Fix auf BESTEHENDEN Instanzen.

    data/ir_cron.xml liegt in <data noupdate="1">, daher greift das per XML
    gesetzte numbercall=-1 beim Upgrade nicht auf den vorhandenen Datensatz.
    Ohne diesen Fix lief der Cron nur 1x (numbercall lief auf 0) und deaktivierte
    sich selbst. Dieses Skript holt das nach.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    cron = env.ref("frawo_agent.cron_agent_queue", raise_if_not_found=False)
    if cron:
        cron.write({"numbercall": -1, "active": True})

    # Aufraeumen: nie benutzter "Agent-Queue"-Tag (XML entfernt). Da der Datensatz
    # in <data noupdate="1"> angelegt wurde, defensiv hier loeschen, falls die
    # Odoo-Orphan-Bereinigung ihn nicht schon entfernt hat.
    tag = env.ref("frawo_agent.tag_agent_queue", raise_if_not_found=False)
    if tag:
        tag.unlink()
