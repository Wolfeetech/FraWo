# Operator Todo Queue

Stand: `2026-04-19` | Aktualisiert von: Codex

---

## Kanban Board

### Blocked

| Task | Warum blockiert | Naechster reale Hebel |
|------|-----------------|----------------------|
| `radio_node_recovery` | `radio-node` antwortet weder auf `192.168.2.155` noch auf `100.64.23.77`; Frontdoor `:8448` liefert `502` | Pi physisch pruefen: Strom, LAN, Boot |
| `split_dns_finalization` | `hs27.internal` ist technisch vorbereitet, aber der restricted nameserver ist im Tailscale Admin noch nicht final gesetzt | `100.82.26.53` in Tailscale Admin DNS eintragen oder lokalen NRPT-Helfer erhoeht ausfuehren |
| `wolfstudiopc_repo_path` | `wolfstudiopc` ist online, aber `SSH` auf `22/tcp` ist geschlossen | Windows OpenSSH aktivieren oder lokale Admin-Session bereitstellen |

### Next

| Task | Lane | Einstieg |
|------|------|---------|
| `radio_node_recovery` | Lane E | `C:\Users\Admin\Workspace\Radio_Node_Recovery_Runbook_2026-04-19.md` |
| `split_dns_finalization` | Lane C | `https://login.tailscale.com/admin/dns` |
| `windows_gui_updates_closeout` | Lane C | `scripts/update_windows_operator_workstation.ps1` |
| `mobile_off_lan_validation` | Lane C | Handy off-LAN mit Tailscale gegen `portal.hs27.internal`, `odoo.hs27.internal`, `ha.hs27.internal` testen |
| `document_flow_acceptance` | Lane C | Eine Test-PDF ueber Nextcloud/Paperless einmal echt durchspielen |

### Doing

| Task | Gestartet | Naechster Schritt |
|------|-----------|-----------------|
| `ssot_realign_after_recovery` | 2026-04-19 | zentrale Plan-/Kontext-Dateien auf den echten Recovery- und DNS-Stand ziehen |

### Done

| Task | Abgeschlossen |
|------|---------------|
| `repo_reconcile_and_push` | 2026-04-19 |
| `toolbox_frontdoor_recovery` | 2026-04-19 |
| `toolbox_dns_recovery` | 2026-04-19 |
| `media_frontdoor_recovery` | 2026-04-19 |
| `recovery_dns_ssot_commit` | 2026-04-19 |

---

## Operator Notes

- `radio-node` ist aktuell kein DNS- oder Proxy-Thema mehr. Die Gegenprobe von `toolbox` schlaegt ebenfalls fehl. Das ist sehr wahrscheinlich ein Pi-/Power-/Boot-/LAN-Problem.
- Fuer entfernte Tailscale-Clients muss der restricted nameserver fuer `hs27.internal` auf `100.82.26.53` zeigen, nicht auf `10.1.0.20`.
- Der Repo-Stand ist sauber: `main` ist mit `origin/main` synchron.

## Definition Of Done

Eine Task gilt erst als erledigt, wenn:

- ein technischer Check oder sichtbarer Operator-Check gruen ist
- die relevante SSOT-Datei nachgezogen wurde
- keine Secrets ins Repo geschrieben wurden
- der naechste echte Restpunkt klar benannt ist
