# Surface Control Dashboard

Dieses Dokument ist die kanonische Schnellansicht fuer `wolf_surface`.

## Rolle

- `wolf_surface` ist der saubere FraWo-Kontrollknoten fuer Sichtpruefung, Log-Review, SSH-Administration und Backup-Checks.
- Estate-Zugriff erfolgt ueber die Repo-Konfiguration `Codex/ssh_config`, nicht ueber lokale SSH-Sonderwege.
- `wolf_surface` bleibt bewusst schlank: Workspace, Browser, Git, OpenSSH, Tailscale und die noetigen Launcher reichen aus.

## Status 2026-04-15

- Lokal bestaetigt: Hostname `DESKTOP-7LMP02S`, Tailscale `100.79.103.59`
- Repo-SSH verifiziert:
  - `ssh -F Codex/ssh_config toolbox`
  - `ssh -F Codex/ssh_config pve`
  - `ssh -F Codex/ssh_config stock`
- `wolfstudiopc` ist im Tailnet online als `100.98.31.60`, aber `SSH` ist dort noch nicht offen.
- `hs27.internal` loest auf `wolf_surface` derzeit noch nicht sauber auf. Der richtige Fix ist Split DNS in Tailscale, nicht ein lokaler Hosts-Workaround.

## Management-Pfade

| Ziel | Pfad |
| --- | --- |
| Proxmox Anker | `https://100.69.179.87:8006` |
| Toolbox SSH | `ssh -F Codex/ssh_config toolbox` |
| Proxmox SSH | `ssh -F Codex/ssh_config pve` |
| Stockenweiler SSH | `ssh -F Codex/ssh_config stock` |
| WolfStudioPC GUI-Fallback | `Studio-RDP.cmd` nach Freigabe von RDP/OpenSSH |

## Review Guardrails

1. Keine lokale Schattenkonfiguration fuer SSH, DNS oder Inventar aufbauen.
2. Aenderungen zuerst im Repo pflegen, danach den Kontrollknoten nur als sauberen Sicht- und Steuerpfad verwenden.
3. Wenn `hs27.internal` auf `wolf_surface` gebraucht wird, den Split-DNS-Pfad aus `TAILSCALE_SPLIT_DNS_PLAN.md` verwenden.
4. Wenn `wolfstudiopc` administrierbar werden soll, zuerst `OpenSSH Server` dort aktivieren und dann den Repo-Bootstrap ausrollen.
