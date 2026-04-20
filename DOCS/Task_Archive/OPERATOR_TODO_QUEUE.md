# Operator Todo Queue

Stand: `2026-04-20` | Aktualisiert von: Codex

---

## Kanban Board

### Blocked

| Task | Warum blockiert | Naechster reale Hebel |
|------|-----------------|----------------------|
| `radio_node_recovery` | `radio-node` antwortet weder auf `192.168.2.155` noch auf `100.64.23.77`; Frontdoor `:8448` liefert `502` | Pi physisch pruefen: Strom, LAN, Boot |
| `odoo_vm220_console_recovery` | `odoo.hs27.internal` liefert `502`; `VM 220` antwortet auf Ping, aber `22/tcp` und `8069/tcp` sind `connection refused` | Proxmox-Konsole fuer `VM 220` oeffnen und `DOCS/Handover/VM220_ODOO_CONSOLE_RECOVERY_RUNBOOK.md` abarbeiten |
| `split_dns_finalization` | `hs27.internal` ist technisch vorbereitet, aber der restricted nameserver ist im Tailscale Admin noch nicht final gesetzt | `100.82.26.53` in Tailscale Admin DNS eintragen oder lokalen NRPT-Helfer erhoeht ausfuehren |
| `wolfstudiopc_repo_path` | `wolfstudiopc` ist online, aber `SSH` auf `22/tcp` ist geschlossen | Windows OpenSSH aktivieren oder lokale Admin-Session bereitstellen |
| `public_edge_https_release` | direkter IPv4-/ACME-Pfad auf `VM220` bleibt durch DS-Lite blockiert; HTTPS-Baseline fuer die Website ist deshalb noch rot | Cloudflare-Proxy/Tunnel fuer `frawo-tech.de` und `www.frawo-tech.de` auf `VM220` final entscheiden und aktivieren; danach `scripts/run_https_baseline_track.ps1` gruen ziehen |

### Next

| Task | Lane | Einstieg |
|------|------|---------|
| `radio_node_recovery` | Lane E | `C:\Users\Admin\Workspace\Radio_Node_Recovery_Runbook_2026-04-19.md` |
| `odoo_vm220_console_recovery` | Lane C | `DOCS/Handover/VM220_ODOO_CONSOLE_RECOVERY_RUNBOOK.md` |
| `split_dns_finalization` | Lane C | `https://login.tailscale.com/admin/dns` |
| `public_edge_https_release` | Lane B | `DOCS/Handover/CLOUDFLARE_TUNNEL_FINALIZATION.md` |
| `windows_gui_updates_closeout` | Lane C | `scripts/update_windows_operator_workstation.ps1` |
| `mobile_off_lan_validation` | Lane C | Handy off-LAN mit Tailscale gegen `portal.hs27.internal`, `odoo.hs27.internal`, `ha.hs27.internal` testen |
| `document_flow_acceptance` | Lane C | Eine Test-PDF ueber Nextcloud/Paperless einmal echt durchspielen |

### Doing

| Task | Gestartet | Naechster Schritt |
|------|-----------|-----------------|
| `public_edge_decision_package` | 2026-04-20 | Cloudflare/VM220 als bevorzugten HTTPS-Baseline-Pfad in Runbooks und Statusdateien festziehen |

### Done

| Task | Abgeschlossen |
|------|---------------|
| `repo_reconcile_and_push` | 2026-04-19 |
| `toolbox_frontdoor_recovery` | 2026-04-19 |
| `toolbox_dns_recovery` | 2026-04-19 |
| `media_frontdoor_recovery` | 2026-04-19 |
| `recovery_dns_ssot_commit` | 2026-04-19 |
| `ssot_realign_after_recovery` | 2026-04-20 |

---

## Operator Notes

- `radio-node` ist aktuell kein DNS- oder Proxy-Thema mehr. Die Gegenprobe von `toolbox` schlaegt ebenfalls fehl. Das ist sehr wahrscheinlich ein Pi-/Power-/Boot-/LAN-Problem.
- `odoo.hs27.internal` ist im aktuellen Incident ebenfalls kein DNS-Thema mehr: `10.1.0.22` antwortet auf Ping, aber `22/tcp`, `80/tcp`, `443/tcp` und `8069/tcp` liefern `connection refused`.
- Fuer entfernte Tailscale-Clients muss der restricted nameserver fuer `hs27.internal` auf `100.82.26.53` zeigen, nicht auf `10.1.0.20`.
- Fuer Lane B ist der bevorzugte HTTPS-/Release-Pfad jetzt `Cloudflare -> VM220`; echter direkter IPv4-/Dual-Stack-Cutover bleibt nur Alternativpfad.
- Der aktuelle Erfolgspunkt fuer Lane B ist zuerst gueltiges HTTPS; Design und Content duerfen bis spaeter vorlaeufig bleiben.
- Der Repo-Stand ist sauber: `main` ist mit `origin/main` synchron.

## Definition Of Done

Eine Task gilt erst als erledigt, wenn:

- ein technischer Check oder sichtbarer Operator-Check gruen ist
- die relevante SSOT-Datei nachgezogen wurde
- keine Secrets ins Repo geschrieben wurden
- der naechste echte Restpunkt klar benannt ist
