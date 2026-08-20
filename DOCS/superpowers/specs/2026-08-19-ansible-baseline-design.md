# Ansible-Grundlinie für beide Proxmox-Server — Design

Zweite Etappe des "Profi-Aufräum"-Vorhabens (nach Schritt 1
Doku-Wirklichkeit-Abgleich und der RAM-Neuplanung ProDesk am
19.08.2026, siehe `project_frawo_2026-08-17_serverumzug.md`).

## Ziel

Den heute (19.08.2026) beim Blackbox-Audit hergestellten sicheren
Grundzustand beider Server **als Code festhalten**, damit er nicht
mehr lautlos abweichen kann — genau das Muster, das heute mehrfach
Zeit gekostet hat (Crontab zeigte auf gelöschte Pfade, Autostart fehlte
für 7 von 9 Diensten, Firewall-Doku stimmte nicht mit der Realität
überein).

**Bewusst NICHT Ziel dieser ersten Etappe:** neue Container/VMs damit
aufsetzen, Anwendungs-Deployments (Odoo, AzuraCast, n8n …) verwalten.
Das ist eine mögliche spätere Erweiterung, kein Teil dieser Spec.

## Umgang mit dem bestehenden `ansible/`-Ordner

Geprüft: 93 Dateien, fast vollständig für die abgeschaltete
"homeserver2027"/Raspberry-Pi-Generation (Host-Gruppen `nextcloud_vm`,
`odoo_vm`, `paperless_vm`, `raspberry_pi_radio`, `surface_go_frontend` —
keine davon existiert mehr in der aktuellen Landschaft, siehe NOW.md).

**Zwei Bausteine sind inhaltlich brauchbar und werden übernommen (nicht
neu erfunden):**
1. `ansible/playbooks/pve_autoheal.yml` — Kernel-Panic-Auto-Reboot +
   Watchdog für den Anker-Host. War bisher nur als Playbook vorhanden,
   nie dokumentiert ob/wann ausgeführt — wird als Teil der neuen
   Grundlinie mit übernommen (Anker-spezifisch, siehe unten).
2. SSH-LAN-only-Härtungsmuster aus
   `ansible/templates/network/90-homeserver2027-business-ssh-lan-only.conf.j2`
   — Grundidee (SSH nur auf internen Interfaces horchen lassen) wird
   übernommen, Umsetzung an die aktuellen Hosts angepasst.

   **Nachtrag (2026-08-20, während der Umsetzung):** dieser Punkt wurde
   NICHT umgesetzt, bewusst und nicht nur vergessen. `stock-pve`s
   `ansible_host` im Inventory ist seine Tailscale-Adresse
   (`100.91.20.116`); ein `ListenAddress {{ ansible_host }}` in sshd würde
   SSH auf Loopback + Tailscale einschränken und genau das LAN
   (`10.1.0.0/24`, `192.168.2.0/24`) aussperren, das erreichbar bleiben
   muss — das Gegenteil vom Ziel. Die `ssh_hardening`-Rolle setzt daher nur
   PasswordAuthentication/PermitRootLogin/PubkeyAuthentication, ohne
   ListenAddress-Einschränkung.

**Alles andere** (Nextcloud/Odoo/Paperless-VM-Playbooks, Surface-Go-
Kiosk-Templates, Raspberry-Pi-Radio-Integration) wandert komplett nach
`archive/ansible-homeserver2027/` — nicht gelöscht, aber aus dem
aktiven `ansible/`-Baum raus.

## Struktur (neu)

```
ansible/
  inventory/
    hosts.yml            # 2 Hosts: stock-pve, anker-pve
    group_vars/
      all.yml             # gemeinsame Grundeinstellungen
      all/vault.yml        # verschlüsselt (ansible-vault), Passwörter
    host_vars/
      stock-pve.yml
      anker-pve.yml         # zusätzlich: watchdog-Variablen
  playbooks/
    baseline.yml            # ruft die Rollen unten auf, für beide Hosts
  roles/
    ssh_hardening/           # PermitRootLogin/PasswordAuth/LAN-only
    firewall_baseline/        # pve-firewall Grundregeln (DROP-Default,
                               #   Monitoring-Ports, dokumentierte Ausnahmen)
    autostart_guests/         # onboot=1 + Start-Reihenfolge für LXC/VMs
                               #   (heutiger Fund: 7/9 Container ohne Autostart)
    unattended_updates/       # Paket-Updates automatisch einspielen
    fail2ban/                 # Installation + jail.local
    autoheal_anker/           # NUR für anker-pve (aus altem Ordner übernommen)
```

Jede Rolle: ein klarer Zweck, idempotent (mehrfaches Ausführen ändert
nichts mehr nach dem ersten Mal), einzeln testbar.

## Geheimnisse

`ansible-vault` für `group_vars/all/vault.yml` (z. B. das heute
rotierte Proxmox-root-Passwort, falls eine Rolle es je braucht).
Vault-Master-Passwort selbst **nicht im Repo** — wird direkt an Wolf
weitergegeben, Empfehlung: in Vaultwarden ablegen. `.gitignore` prüft
zusätzlich gegen versehentliches Committen der Klartext-Variante.

## Ablauf / Testreihenfolge

1. Erst gegen `anker-pve` mit `--check --diff` (Probe-Modus, ändert
   nichts, zeigt nur was sich ändern würde) — geringeres Risiko, kein
   Live-Publikum betroffen.
2. Ergebnis mit Wolf durchgehen.
3. Echter Lauf gegen `anker-pve`.
4. Gleiches Muster für `stock-pve` (Probe → durchsehen → echt) — dort
   läuft Radio/Odoo/Website live, deshalb zusätzliche Vorsicht.
5. Nach jedem echten Lauf: Kernfunktionen prüfen (Website, Radio-Stream,
   Odoo erreichbar) — gleiche Prüfmethode wie beim heutigen Audit.

## Nicht in dieser Version (bewusst zurückgestellt)

- Kein automatischer/zeitgesteuerter Ansible-Lauf (kein Cron/Timer) —
  erst manuell, bis Vertrauen in die Rollen besteht. Automatisierung
  danach als eigener, kleiner Folgeschritt.
- Kein Drift-Erkennung (regelmäßiger `--check`-Lauf, der meldet wenn
  die Realität abweicht) — sinnvolle spätere Erweiterung, nicht Teil
  dieser ersten Etappe.
- Keine Anwendungs-Konfiguration (Odoo, AzuraCast, Docker-Compose-
  Dienste) — nur Host-Betriebssystem-Ebene.
