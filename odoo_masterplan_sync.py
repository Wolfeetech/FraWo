#!/usr/bin/env python3
"""
FRAWO Homeserver 2027 — Odoo Masterplan & Roadmap Sync
======================================================
Importiert den gesamten Masterplan und die offenen Operator-Aufgaben
als strukturierte Projekte und Tasks in Odoo (XML-RPC API).

Ziel: Odoo wird die neue Single Source of Truth (SSOT) für alle
Infrastruktur-Vorhaben. Markdown-Dateien werden danach eingefroren.

Sicherheit: Passwort wird interaktiv abgefragt, nie gespeichert.
"""

import xmlrpc.client
import getpass
import sys

# ─── Konfiguration ───────────────────────────────────────────────────
URL = "http://10.1.0.22:8069"
DB  = "FraWo_GbR"
DEFAULT_USER = "w.prinz1101@gmail.com"

# ─── Projekt-Struktur (aus MASTERPLAN.md & EXECUTIVE_ROADMAP.md) ─────
# Jedes Projekt bildet eine "Lane" oder einen strategischen Strang ab.
PROJECTS = [
    {
        "name": "🏗️ Homeserver 2027: MVP Closeout (Lane A)",
        "description": "Interner Business-MVP auf READY ziehen. Portal, Vaultwarden, Nextcloud, Paperless, Odoo, STRATO-Mail, lokale Backups.",
        "tasks": [
            {
                "name": "🔑 Vaultwarden Recovery-Material verifizieren",
                "description": "<p><strong>Lane:</strong> A — MVP Closeout</p>"
                    "<ul>"
                    "<li>[ ] Zwei getrennte physische Offline-Kopien des Recovery-Materials sicherstellen</li>"
                    "<li>[ ] Frischen Nachweis liefern</li>"
                    "</ul>"
                    "<p><strong>Done when:</strong> Zwei Offline-Kopien real vorhanden und nachgewiesen.</p>",
                "priority": "1",  # urgent
            },
            {
                "name": "📱 Geräte-Rollout (Franz Surface & iPhone)",
                "description": "<p><strong>Lane:</strong> A — MVP Closeout</p>"
                    "<ul>"
                    "<li>[ ] 2FA-Pfad nach verlorenem Smartphone wiederherstellen</li>"
                    "<li>[ ] Franz Surface Laptop im echten Alltagspfad prüfen</li>"
                    "<li>[ ] Franz iPhone im echten Alltagspfad prüfen</li>"
                    "<li>[ ] Sichtbaren Nachweis erstellen</li>"
                    "</ul>"
                    "<p><strong>Blocked by:</strong> Verlorenes Smartphone / fehlender 2FA-Pfad.</p>",
                "priority": "1",
            },
            {
                "name": "📧 STRATO Mail-Modell final verifizieren",
                "description": "<p><strong>Lane:</strong> A — MVP Closeout</p>"
                    "<ul>"
                    "<li>[x] webmaster@frawo-tech.de technisch verifiziert</li>"
                    "<li>[x] franz@frawo-tech.de technisch verifiziert</li>"
                    "<li>[ ] info@frawo-tech.de technisch prüfen</li>"
                    "<li>[ ] noreply@frawo-tech.de technisch prüfen</li>"
                    "<li>[ ] Sichtbare SMTP-Testmails aus Nextcloud, Paperless & Odoo</li>"
                    "</ul>",
                "priority": "0",  # normal
            },
            {
                "name": "👤 Wolf & Franz Login-Walkthrough",
                "description": "<p><strong>Lane:</strong> A — MVP Closeout</p>"
                    "<ul>"
                    "<li>[ ] Wolf-Login Vault, Nextcloud, Paperless, Odoo sichtbar</li>"
                    "<li>[ ] Franz-Login Vault, Nextcloud, Paperless, Odoo sichtbar</li>"
                    "</ul>"
                    "<p><strong>Done when:</strong> release-mvp-gate meldet MVP_READY.</p>",
                "priority": "0",
            },
            {
                "name": "🔐 SPF / DKIM / DMARC dokumentieren & testen",
                "description": "<p><strong>Lane:</strong> A — MVP Closeout (Mail-Sicherheit)</p>"
                    "<ul>"
                    "<li>[x] DMARC sichtbar (p=reject)</li>"
                    "<li>[ ] SPF-Record im Live-Check prüfen</li>"
                    "<li>[ ] DKIM-Signatur verifizieren</li>"
                    "</ul>",
                "priority": "0",
            },
        ],
    },
    {
        "name": "🌐 Homeserver 2027: Website Release (Lane B)",
        "description": "Erster öffentlicher Release von www.frawo-tech.de als Odoo-Website mit Radio-Präsenz. Kein Admin-UI öffentlich.",
        "tasks": [
            {
                "name": "🔒 TLS/HTTPS für www.frawo-tech.de aktivieren",
                "description": "<p><strong>Lane:</strong> B — Website/Public</p>"
                    "<ul>"
                    "<li>[x] Caddy Reverse Proxy konfiguriert (Zero Trust Blocking aktiv)</li>"
                    "<li>[x] Odoo proxy_mode = True gesetzt</li>"
                    "<li>[ ] Port 80/443 Forwarding im Gateway auf 10.1.0.20 setzen</li>"
                    "<li>[ ] Let's Encrypt Zertifikat automatisch ausstellen lassen</li>"
                    "<li>[ ] HTTPS End-to-End verifizieren</li>"
                    "</ul>",
                "priority": "1",
            },
            {
                "name": "📻 Sichtbare Radio-Präsenz auf der Website",
                "description": "<p><strong>Lane:</strong> B — Website/Public</p>"
                    "<ul>"
                    "<li>[x] /radio/public/frawo-funk Pfad intern verifiziert</li>"
                    "<li>[ ] Öffentliche Sichtbarkeit nach TLS-Aktivierung bestätigen</li>"
                    "</ul>",
                "priority": "0",
            },
            {
                "name": "🔄 DNS Rollback dokumentieren",
                "description": "<p><strong>Lane:</strong> B — Website/Public</p>"
                    "<ul>"
                    "<li>[ ] Rollback-Pfad für DNS/TLS/Hostwechsel dokumentieren</li>"
                    "<li>[ ] Trockenübung durchführen</li>"
                    "</ul>",
                "priority": "0",
            },
        ],
    },
    {
        "name": "🛡️ Homeserver 2027: Security & Infra (Lane C)",
        "description": "PBS Vollzertifizierung, Gateway-Cutover, Netzwerk-Governance. Blockiert nicht den MVP, aber wichtig für Produktion.",
        "tasks": [
            {
                "name": "🌐 Tailscale Route 10.1.0.0/24 freigeben",
                "description": "<p><strong>Lane:</strong> C — Security/Infra</p>"
                    "<ul>"
                    "<li>[x] Route bei toolbox approven</li>"
                    "<li>[x] Verifiziert: Remote-Clients erreichen 10.1.0.20</li>"
                    "</ul>"
                    "<p><strong>Status: ERLEDIGT ✅</strong></p>",
                "priority": "0",
            },
            {
                "name": "🌍 Tailscale Split-DNS auf 10.1.0.20",
                "description": "<p><strong>Lane:</strong> C — Security/Infra</p>"
                    "<ul>"
                    "<li>[x] Restricted nameserver für hs27.internal auf 10.1.0.20</li>"
                    "<li>[x] Verifiziert: odoo.hs27.internal löst auf 10.1.0.20 auf</li>"
                    "</ul>"
                    "<p><strong>Status: ERLEDIGT ✅</strong></p>",
                "priority": "0",
            },
            {
                "name": "🗄️ PBS Guarded Rebuild (VM 240)",
                "description": "<p><strong>Lane:</strong> C — Security/Infra</p>"
                    "<ul>"
                    "<li>[ ] Dedizierten Boot-USB und Datastore bereitstellen</li>"
                    "<li>[ ] Seriennummern im PBS-Device-Contract freigeben</li>"
                    "<li>[ ] Guarded Datastore-Prepare ausführen</li>"
                    "<li>[ ] VM 240 sauber rebuilden</li>"
                    "<li>[ ] Ersten echten Proof-Backup und Restore-Drill nachweisen</li>"
                    "</ul>",
                "priority": "0",
            },
            {
                "name": "🔌 AdGuard Home als primärer LAN-DNS",
                "description": "<p><strong>Lane:</strong> C — Security/Infra</p>"
                    "<ul>"
                    "<li>[ ] UCG-Gateway DNS auf 10.1.0.20 umstellen</li>"
                    "<li>[ ] Pilot-Clients definieren und testen</li>"
                    "<li>[ ] DNS-Rollback dokumentieren</li>"
                    "</ul>",
                "priority": "0",
            },
            {
                "name": "🌉 Gateway-Cutover auf UCG-Ultra (Phase 7)",
                "description": "<p><strong>Lane:</strong> C — Security/Infra</p>"
                    "<ul>"
                    "<li>[x] UCG am Anker aktiv, VLAN-Schema deployed</li>"
                    "<li>[ ] Firewall-Regeln zwischen VLANs setzen</li>"
                    "<li>[ ] Proxmox VLAN-Trunk-Migration (192.168.2.x → 10.1.0.x)</li>"
                    "<li>[ ] WireGuard VPN zu Stockenweiler</li>"
                    "<li>[ ] StudioPC in VLAN 100 migrieren</li>"
                    "</ul>"
                    "<p><strong>Blocked by:</strong> Bridge-Route wird durch UCG-WAN-Overlap (EasyBox) überschattet.</p>",
                "priority": "0",
            },
        ],
    },
    {
        "name": "🏠 Homeserver 2027: Stockenweiler (Lane D)",
        "description": "Elternhaushalt als erster externer Testkunde. Tailscale-only, kein WAN. Cold-Standby DR-Knoten.",
        "tasks": [
            {
                "name": "🖥️ Stockenweiler Cold-Standby DR vorbereiten",
                "description": "<p><strong>Lane:</strong> D — Stockenweiler</p>"
                    "<ul>"
                    "<li>[x] Server entlastet (7+ GB RAM frei, Zombie-Prozesse beendet)</li>"
                    "<li>[x] Radio/Media/DB Stacks gestoppt und Autostart entfernt</li>"
                    "<li>[ ] PBS oder rsync für nächtliche Datenspiegelung konfigurieren</li>"
                    "<li>[ ] deploy_standby.sh Notfall-Skript erstellen</li>"
                    "<li>[ ] DR-Cutover-Dokumentation schreiben</li>"
                    "</ul>",
                "priority": "0",
            },
            {
                "name": "🏡 Rentner OS v1: Remote-Support aufbauen",
                "description": "<p><strong>Lane:</strong> D — Stockenweiler</p>"
                    "<ul>"
                    "<li>[ ] Geräte- und Providerbestand erfassen</li>"
                    "<li>[ ] Secret-Bereich 'Stockenweiler' in Vaultwarden/FraWo anlegen</li>"
                    "<li>[ ] Ersten Remote-Support-Pfad (Tailscale + AnyDesk) testen</li>"
                    "<li>[ ] Dokumenten-/Scanpfad nur über Standard-Workflow anbinden</li>"
                    "</ul>"
                    "<p><strong>Zugriffsmodell:</strong> Tailscale-only, AnyDesk als GUI-Fallback, keine WAN-Ports.</p>",
                "priority": "0",
            },
        ],
    },
    {
        "name": "📻 Homeserver 2027: Radio & Media (Lane E)",
        "description": "Radio/AzuraCast und Jellyfin Medienserver. Aktuell im Hold-Modus.",
        "tasks": [
            {
                "name": "🍓 Raspberry Pi Radio Node integrieren",
                "description": "<p><strong>Lane:</strong> E — Radio/Media (HOLD)</p>"
                    "<ul>"
                    "<li>[ ] SSH-/Betriebspfad auf dem Pi wiederherstellen</li>"
                    "<li>[ ] SMB-/Stationspfad und Medienlayout verifizieren</li>"
                    "<li>[ ] SMTP-Benachrichtigungspfad für AzuraCast finalisieren</li>"
                    "</ul>",
                "priority": "0",
            },
            {
                "name": "📺 Jellyfin Client-Rollout",
                "description": "<p><strong>Lane:</strong> E — Radio/Media (HOLD)</p>"
                    "<ul>"
                    "<li>[x] Jellyfin läuft auf CT 100 toolbox</li>"
                    "<li>[x] media.hs27.internal liefert Jellyfin intern</li>"
                    "<li>[ ] Zugänge in Vaultwarden/FraWo/Media übernehmen</li>"
                    "<li>[ ] Thomson/Google TV Clients verbinden</li>"
                    "</ul>",
                "priority": "0",
            },
        ],
    },
]


def main():
    print("=" * 60)
    print("  🚀 FRAWO Homeserver 2027 — Odoo Masterplan Sync")
    print("=" * 60)
    print(f"\n  Ziel:  {URL}")
    print(f"  DB:    {DB}")
    print()

    username = input(f"  Odoo Login [{DEFAULT_USER}]: ").strip() or DEFAULT_USER
    password = getpass.getpass("  Odoo Passwort: ")

    # ─── Authentifizierung ────────────────────────────────────────
    print("\n⏳ Verbinde...")
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    try:
        uid = common.authenticate(DB, username, password, {})
        if not uid:
            print("❌ Login fehlgeschlagen!")
            sys.exit(1)
        print(f"✅ Authentifiziert als UID {uid}")
    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

    # ─── Wolfi als Bearbeiter finden ──────────────────────────────
    try:
        user_ids = models.execute_kw(
            DB, uid, password, "res.users", "search",
            [[("name", "ilike", "Wolf")]]
        )
        assigned_user = user_ids[0] if user_ids else uid
        print(f"✅ Bearbeiter 'Wolfi' gefunden (UID {assigned_user})")
    except Exception:
        assigned_user = uid
        print(f"⚠️  Bearbeiter nicht gefunden, nutze Login-User (UID {uid})")

    # ─── Projekte und Tasks anlegen ───────────────────────────────
    total_tasks = 0
    for project_def in PROJECTS:
        print(f"\n{'─' * 50}")
        print(f"📂 Projekt: {project_def['name']}")

        # Prüfe ob Projekt schon existiert
        existing = models.execute_kw(
            DB, uid, password, "project.project", "search",
            [[("name", "=", project_def["name"])]]
        )
        if existing:
            project_id = existing[0]
            print(f"   ♻️  Projekt existiert bereits (ID {project_id})")
        else:
            project_id = models.execute_kw(
                DB, uid, password, "project.project", "create",
                [{"name": project_def["name"], "description": project_def["description"]}]
            )
            print(f"   ✅ Projekt angelegt (ID {project_id})")

        # Tasks anlegen
        for task_def in project_def["tasks"]:
            # Prüfe ob Task schon existiert
            existing_task = models.execute_kw(
                DB, uid, password, "project.task", "search",
                [[("name", "=", task_def["name"]), ("project_id", "=", project_id)]]
            )
            if existing_task:
                print(f"   ♻️  Task existiert: {task_def['name']}")
                continue

            task_data = {
                "name": task_def["name"],
                "description": task_def["description"],
                "project_id": project_id,
                "user_ids": [assigned_user],
                "priority": task_def.get("priority", "0"),
            }
            try:
                task_id = models.execute_kw(
                    DB, uid, password, "project.task", "create", [task_data]
                )
                print(f"   ✅ Task angelegt: {task_def['name']} (ID {task_id})")
                total_tasks += 1
            except Exception as e:
                print(f"   ❌ Fehler: {task_def['name']}: {e}")

    print(f"\n{'=' * 60}")
    print(f"  🎉 Import abgeschlossen!")
    print(f"  📊 {len(PROJECTS)} Projekte, {total_tasks} neue Tasks")
    print(f"  👤 Alle Tasks zugewiesen an: Wolfi")
    print(f"\n  👉 Öffne Odoo Projektmanagement um das Board zu sehen!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
