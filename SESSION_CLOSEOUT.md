# Session Closeout - 2026-03-18

## Day Status

- Workspace is structurally ready:
  - named alias created
  - desktop shortcut created
  - shared Codex/Gemini context files in place
  - automatic `LIVE_CONTEXT.md` refresh active via user systemd path
- Inventory baseline is in place for the full observed LAN.
- Legacy session directories were removed after secret migration.
- `VM 200 nextcloud` is healthy and QGA-verified.
- `VM 220 odoo` was stabilized and QGA-verified.
- `VM 230 paperless` is healthy and QGA-verified.
- All three business stacks now run from `/opt/homeserver2027/stacks` under systemd-managed local IaC.
- Proxmox thin-pool guardrails were hardened and re-verified.
- `CT 100 toolbox` now has a live internal network foundation:
  - Docker installed and managed under local IaC
  - Caddy frontdoor active on port `80`
  - AdGuard Home active in opt-in mode on port `53`
  - AdGuard admin reduced to localhost-only on `127.0.0.1:3000`
  - `hs27.internal` rewrites verified to `192.168.2.20`
  - `/dev/net/tun` is present and `tailscaled` is installed, enabled and active

## What Was Finished Today

1. Built the shared operations workspace and canonical documentation set.
2. Created human-readable and machine-readable network inventory.
3. Migrated active secrets into encrypted Ansible Vault storage.
4. Cleaned up obsolete session directories.
5. Repaired Odoo runtime stability:
   - duplicate disk mapping removed
   - boot order corrected
   - restart policies improved
   - QEMU Guest Agent installed and verified
6. Verified Nextcloud runtime and installed QEMU Guest Agent.
7. Added workspace presets, alias, desktop shortcut and auto-refresh handoff flow.
8. Moved Nextcloud, Odoo and Paperless under local IaC with:
   - `ansible/playbooks/deploy_business_stacks.yml`
   - templated stack definitions
   - enabled systemd compose services on each business VM
9. Verified post-cutover application health:
   - Nextcloud returned `200`
   - Odoo `/web/login` returned `200`
   - Paperless returned `302`
10. Removed obsolete in-guest stack directories under `/home/wolf/<stack>` after the cutover proved healthy.
11. Installed and verified QEMU Guest Agent on `VM 230 paperless`, including a successful reboot.
12. Cleaned up temporary business-VM snapshots, enabled LVM thin-pool autoextend on Proxmox and extended `local-lvm` from `140.87 GiB` to `156.88 GiB`.
13. Verified the new thin-pool settings with a successful create/delete test snapshot on `VM 200`.
14. Proved the interim backup and restore path end to end:
   - local `vzdump` backups for `VM 200`, `VM 220` and `VM 230` succeeded
   - Odoo restore to temporary `VM 920` succeeded with `qga_ok`
   - `http://192.168.2.240:8069/web/login` returned `200`
   - test VM `920` was removed again after verification
15. Added and verified `make business-drift-check` for the IaC-managed business stacks:
   - Nextcloud, Odoo and Paperless systemd units are enabled and active
   - compose files are present under `/opt/homeserver2027/stacks`
   - application login endpoints returned healthy HTTP responses
16. Added local backup-retention operations for the interim Proxmox `local` backup path:
   - `make backup-list`
   - `make backup-prune-dry-run`
   - `make backup-prune`
   - standard retention until PBS goes live is latest `2` local qemu archives per business VM
17. Folded the next planning wave into the canonical roadmap:
   - `AdGuard Home` is now staged as a later internal DNS/filter service on `CT 100`
   - public exposure is explicitly separated into a future hardened edge phase
   - `Ollama` is captured as deferred wishlist because the current host only has `15 GB` RAM
18. Built the first live `CT 100` network-foundation stack under local IaC:
   - `ansible/playbooks/deploy_toolbox_foundation.yml`
   - Caddy on `192.168.2.20:80`
   - AdGuard Home on `192.168.2.20:53` and `192.168.2.20:3000`
19. Verified internal frontdoor routing and split-DNS:
   - `cloud.hs27.internal` returned `200`
   - `odoo.hs27.internal/web/login` returned `200`
   - `paperless.hs27.internal/accounts/login/` returned `200`
   - `ha.hs27.internal` and `radio.hs27.internal` returned `503` placeholders by design
20. Added reusable toolbox operations checks:
   - `make ansible-syntax-check-toolbox`
   - `make toolbox-deploy`
   - `make toolbox-network-check`
21. Prepared `CT 100` for Tailscale subnet routing:
   - Proxmox `dev0: /dev/net/tun` passthrough added to `CT 100`
   - safety snapshot `codex-pre-toolbox-ts-20260318` created before the change
   - `tailscale` package installed from the official Tailscale Debian repository
   - `tailscaled` enabled and active
   - forwarding sysctls set for subnet-router use
22. Added reusable Tailscale prep tooling:
   - `ansible/playbooks/prepare_toolbox_tailscale.yml`
   - `make toolbox-tun-prep`
   - `make toolbox-tailscale-prep`
   - `make toolbox-tailscale-check`
   - `make toolbox-tailscale-login-url`
23. Added and ran a real HAOS preflight:
   - `make haos-preflight`
   - `VM 210` does not yet exist
   - host RAM and `local-lvm` are sufficient for a baseline `4096 MB` / `32 GB` HAOS VM
   - current USB audit shows only root hubs and no serial adapters, so passthrough is not yet physically actionable
24. Deployed the interim Proxmox night backup standard:
   - `ansible/playbooks/deploy_proxmox_local_backup_ops.yml`
   - host timer `homeserver2027-local-business-backup.timer`
   - daily schedule `02:40`
25. Verified the timer-backed local backup run end to end:
   - fresh archives created for `VM 200`, `VM 220` and `VM 230`
   - service exited with `status=0/SUCCESS`
   - resulting retention is `2` local archives per business VM
   - new operator checks:
     - `make ansible-syntax-check-proxmox-backups`
     - `make proxmox-local-backup-deploy`
     - `make proxmox-local-backup-check`
26. Prepared the HAOS deployment path without creating `VM 210` early:
   - `ansible/playbooks/deploy_haos_vm_runner.yml`
   - Proxmox runner target `/usr/local/sbin/homeserver2027-deploy-haos-vm.sh`
   - new operator checks:
     - `make ansible-syntax-check-haos`
     - `make haos-runner-deploy`
     - `make haos-stage-gate`
     - `make haos-vm-check`
   - the actual VM build remains intentionally stage-gated behind Toolbox Tailscale readiness
27. Added a canonical morning start path:
   - `MORNING_ROUTINE.md`
   - `scripts/start_day.sh`
   - `make start-day`
28. Added a repeatable security baseline:
   - `SECURITY_BASELINE.md`
   - `scripts/security_baseline_check.sh`
   - `make security-baseline-check`
29. Hardened the business VMs against unnecessary local name-resolution exposure:
   - `ansible/playbooks/harden_business_network_baseline.yml`
   - `LLMNR=no`
   - `MulticastDNS=no`
   - verified that `5355` disappeared while application health stayed green
30. Removed the last unnecessary LAN admin surface from `toolbox`:
   - AdGuard admin is now bound only to `127.0.0.1:3000`
   - `make toolbox-network-check` remained green
   - `make security-baseline-check` now reports `adguard_admin_lan_surface=no`
31. Prepared the durable PBS rollout path without building a fake same-disk datastore:
   - `ansible/playbooks/deploy_pbs_vm_runner.yml`
   - Proxmox runner target `/usr/local/sbin/homeserver2027-deploy-pbs-vm.sh`
   - new operator checks:
     - `make ansible-syntax-check-pbs`
     - `make pbs-preflight`
     - `make pbs-stage-gate`
     - `make pbs-vm-check`
   - current blocker is no separate backup storage at `/srv/pbs-datastore`
32. Staged the official PBS installer media on Proxmox and re-verified the gate:
   - `scripts/proxmox_stage_pbs_iso.sh`
   - `make pbs-iso-stage`
   - source ISO stored at `/var/lib/vz/template/iso/proxmox-backup-server_4.1-1.iso`
   - active alias refreshed at `/var/lib/vz/template/iso/proxmox-backup-server-current.iso`
   - verified SHA256: `670f0a71ee25e00cc7839bebb3f399594f5257e49a224a91ce517460e7ab171e`
   - `make pbs-stage-gate` now reports `pbs_iso_present=yes`
   - remaining blocker is only missing separate backup storage at `/srv/pbs-datastore`
33. Added a safe read-only EasyBox browser probe:
   - `scripts/easybox_browser_probe.sh`
   - `make easybox-browser-probe`
   - headless Firefox can now fetch `user_lang.json` reliably from the real browser context via `https://192.168.2.1`
   - raw CLI HTTP clients still fail against the EasyBox 805 with `UNKNOWN 400 Bad Request`
   - latest probe result showed `trying_times=3` with `delay_time=0`
   - authenticated login and lease extraction remain unresolved and should not be brute-forced
34. Added an operator-friendly Tailscale join assistant for `toolbox`:
   - `scripts/toolbox_tailscale_join_assist.sh`
   - `make toolbox-tailscale-join-assist`
   - refreshes the login URL, can open it locally, and polls until `BackendState=Running`
   - keeps the join flow reproducible instead of depending on ad hoc shell steps
35. Completed the actual Tailscale join for `CT 100 toolbox`:
   - backend state is now `Running`
   - tailnet DNS name is `toolbox.tail150400.ts.net.`
   - local prefs advertise `192.168.2.0/24`
   - remaining external follow-up is route approval in the Tailscale admin
36. Built and booted `VM 210` as the baseline HAOS VM:
   - created through `/usr/local/sbin/homeserver2027-deploy-haos-vm.sh`
   - first boot succeeded and Home Assistant answered with `HTTP 200`
   - current first-boot DHCP address is `192.168.2.153`
   - planned steady-state address remains `192.168.2.24`
   - `ha.hs27.internal` is intentionally still not switched to the live HA backend
37. Stabilized `VM 210` onto the planned in-guest address `192.168.2.24`:
   - Home Assistant now answers directly on `http://192.168.2.24:8123`
   - the former first-boot DHCP address `192.168.2.153` is no longer serving HA
   - QGA still reports the guest healthy after the network change
38. Brought Home Assistant onto the internal frontdoor and backup standard:
   - `ha.hs27.internal` now returns `200` through Caddy on `CT 100`
   - Home Assistant reverse-proxy trust is configured for toolbox source IP `192.168.2.20`
   - local backup coverage now includes a successful `vzdump` archive for `VM 210`
39. Re-ran the timer-backed local backup workflow after adding `VM 210`:
   - the real systemd service completed successfully for `VM 200`, `VM 210`, `VM 220` and `VM 230`
   - retention is now enforced at `2` local archives per secured VM
   - the temporary HAOS networking snapshot was removed again after verification
40. Added the first internal shared portal on `CT 100`:
   - `portal.hs27.internal` now resolves through AdGuard to `192.168.2.20`
   - Caddy serves a static internal frontdoor page for Home Assistant, Nextcloud, Radio, Paperless and Odoo
   - the portal path is intended as the future server-side frontdoor for the Surface Go kiosk
   - the temporary toolbox snapshot taken before deployment was removed again after verification
41. Extended the mobile Tailscale frontdoor to cover the new portal:
   - `http://100.99.206.128:8447` now serves the shared internal portal
   - the toolbox mobile firewall was expanded so `8447` stays Tailscale-only like the existing app ports

## Review Findings

1. Medium: Router lease table has not yet been reconciled with the inventory.
   - Manual router review already resolved `Wolf_Pixel`, `SonRoku` and that the Shelly devices belong to the growbox.
   - `Surface_Laptop` is now effectively resolved to `yourparty-Surface-Go.local` on `192.168.2.154`, but the device still needs a clean rebuild into the managed frontend standard.
   - Unknown devices `.141-.144`, the exact `.107`/`.114` Shelly alias split, and labels such as `fireTV` and `Franz_iphone` still need authoritative identification from the Easy Box.
   - Router credentials are now stored and `user_lang.json` is reachable through the new browser-context probe, but authenticated login and lease extraction are still not reproduced.
   - The Surface Go currently exposes `HTTP/80` with the Ubuntu `nginx` default page and no `SSH`, so it is identified but not yet remotely manageable.
2. Medium: Backup and restore are now locally proven, but the durable PBS operating model is still not live.
   - The current stopgap is now stronger than before: successful restore proof plus a live daily local timer on Proxmox `local`.
   - The PBS runner and stage-gate path are now prepared, and the official installer ISO is staged on Proxmox.
   - We still need separate backup storage, scheduled PBS jobs and recurring restore drills before calling the platform fully hardened.
   - Local retention remains latest `2` archives per business VM until PBS takes over.
3. Low: One older snapshot still exists on `VM 100`.
   - This was left untouched intentionally because it is outside the business-VM change scope and may still be part of the Toolbox/Tailscale workstream.
4. Low: `CT 100` network foundation is now live and Tailscale is joined.
   - Internal Caddy and AdGuard opt-in DNS are running and verified.
   - `portal.hs27.internal` is now live as the shared internal frontdoor.
   - The next network step is subnet-route approval plus a controlled pilot-client rollout for AdGuard.
5. Low: `HAOS` ist jetzt intern integriert, nicht nur deployed.
   - `VM 210` ist stabil auf `192.168.2.24`.
   - `ha.hs27.internal` liefert `200` ueber den Toolbox-Frontdoor.
   - USB passthrough haengt weiterhin nur von physisch vorhandenen Adaptern ab.
## Safe To Stop?

Yes.

For tonight the environment is in a controlled state:

- business VMs respond
- Ansible inventory works
- QGA works for `VM 200`, `VM 210`, `VM 220` and `VM 230`
- local backup and restore proof exists for all three business VMs
- workspace handoff is complete

Remaining items are follow-up work, not emergency break-fix work.

## First Tasks Tomorrow

1. Log into the Vodafone Easy Box and reconcile DHCP leases with `NETWORK_INVENTORY.md`.
2. Resolve and classify:
   - unknown devices `.141-.144`
   - duplicated/repeater-shadowed Shelly entries `.107`, `.114`
   - remaining router-only labels `fireTV`, `Franz_iphone`, `Surface_Laptop`, `udhcpc1.21.1`, `udhcp 1.24.1`
3. Prepare `CT 100` as the next network-foundation block:
   - confirm subnet route approval for `192.168.2.0/24`
   - pilot-client rollout for AdGuard Home
   - keep `hs27.internal` and internal Caddy on the verified baseline
   - regenerate the login URL with `make toolbox-tailscale-login-url` if needed
4. Turn the PBS path green:
   - mount separate backup storage at `/srv/pbs-datastore`
   - rerun `make pbs-stage-gate`
5. Keep `VM 210 HAOS` on the new steady-state baseline.
   - preserve `192.168.2.24`, `ha.hs27.internal` and local backup coverage
   - add USB passthrough only once the actual adapters are attached
6. Use `make start-day` as the required operator check before new changes.

## Resume Commands

```bash
cd ~/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace
sed -n '1,220p' LIVE_CONTEXT.md
sed -n '1,220p' SESSION_CLOSEOUT.md
make inventory-check
make ansible-ping
make qga-check
make business-drift-check
make backup-list
make pbs-stage-gate
```

## Notes For Gemini And Codex

- Start from `LIVE_CONTEXT.md`, not from stale chat context.
- Treat `SESSION_CLOSEOUT.md` as the session handoff and `MEMORY.md` as the durable project memory.
- Do not recreate deleted legacy notes or ad hoc side files.
