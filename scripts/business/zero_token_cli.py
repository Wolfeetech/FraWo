"""
Zero-Token Direct Odoo CLI & Command Engine for FraWo
Runs deterministically with 0 LLM tokens, 100% locally and instantly.
"""
import sys
from pathlib import Path

# Add shared business path
sys.path.insert(0, r"C:\Users\StudioPC\FraWo\scripts\business")
import mcp_odoo_pro_server as s

def get_today_focus():
    """Returns today's active tasks and events without LLM invocation."""
    today = "2026-09-01"
    
    # 1. Active Focus Tasks
    in_work = s.odoo_search_read('project.task', [
        ('active', '=', True),
        ('stage_id', '=', 3) # In Arbeit
    ], ['id', 'name', 'project_id', 'date_deadline', 'priority'], limit=10)
    
    # 2. Upcoming deadlines this week (KW 36)
    kw36 = s.odoo_search_read('project.task', [
        ('active', '=', True),
        ('stage_id', '=', 2), # In Planung
        ('date_deadline', '>=', today),
        ('date_deadline', '<=', '2026-09-06 23:59:59')
    ], ['id', 'name', 'project_id', 'date_deadline'], limit=10)
    
    # 3. Blocked tasks
    blocked = s.odoo_search_read('project.task', [
        ('active', '=', True),
        ('stage_id', '=', 5) # Blockiert
    ], ['id', 'name', 'project_id'], limit=5)

    out = []
    out.append("📅 FRAWO TAGES-COCKPIT (0-Token Direct)\n")
    out.append("⚡ HEUTE IM FOKUS:")
    if in_work:
        for t in in_work:
            out.append(f"  • #{t['id']}: {t['name']}")
    else:
        out.append("  Keine dringenden Aufgaben in Arbeit.")

    out.append("\n📌 DIESE WOCHE (KW 36):")
    if kw36:
        for t in kw36:
            dl = (t.get('date_deadline') or '')[:10]
            out.append(f"  • #{t['id']} ({dl}): {t['name']}")
    else:
        out.append("  Keine weiteren Fristen diese Woche.")

    out.append("\n🛑 BLOCKIERT (Wartet auf Externe):")
    if blocked:
        for t in blocked:
            out.append(f"  • #{t['id']}: {t['name']}")
            
    return "\n".join(out)

def mark_task_done(task_id):
    """Directly closes a task in Odoo with 0 tokens."""
    try:
        tid = int(task_id)
        s.odoo_execute('project.task', 'write', [[tid], {'stage_id': 6}])
        s.odoo_execute('project.task', 'message_post', [[tid]], {
            'body': "✅ [Direct-CLI] Aufgabe als erledigt markiert.",
            'message_type': 'comment'
        })
        return f"✅ Aufgabe #{tid} wurde erfolgreich auf 'Erledigt' gesetzt!"
    except Exception as e:
        return f"❌ Fehler beim Schließen von #{task_id}: {e}"

def get_cashflow_summary():
    """Returns financial status and open invoices with 0 tokens."""
    invoices = s.odoo_search_read('account.move', [
        ('move_type', '=', 'out_invoice'),
        ('state', '=', 'posted'),
        ('payment_state', 'in', ['not_paid', 'partial'])
    ], ['id', 'name', 'partner_id', 'amount_total', 'invoice_date_due'])
    
    out = ["💶 OFFENE RECHNUNGEN (Cashflow):\n"]
    if invoices:
        for inv in invoices:
            p = inv['partner_id'][1] if inv.get('partner_id') else 'Kunde'
            out.append(f"• {inv['name']} ({p}): {inv['amount_total']:.2f} € | Fällig: {inv.get('invoice_date_due')}")
    else:
        out.append("Alle Ausgangsrechnungen sind bezahlt!")
    return "\n".join(out)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ['heute', 'today', 'status']:
            print(get_today_focus())
        elif cmd in ['kasse', 'cashflow', 'rechnungen']:
            print(get_cashflow_summary())
        elif cmd == 'done' and len(sys.argv) > 2:
            print(mark_task_done(sys.argv[2]))
        else:
            print("Unbekannter Befehl. Optionen: heute | kasse | done <ID>")
    else:
        print(get_today_focus())
