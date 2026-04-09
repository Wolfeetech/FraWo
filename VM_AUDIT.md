# VM Audit

## Audit Timestamp

- Primary audit date: `2026-03-17`
- Follow-up audit date: `2026-03-24`
- Audit scope: `CT 100 toolbox`, `VM 200 nextcloud`, `VM 220 odoo`, `VM 230 paperless`, `VM 320 restore-test`

## Network State Change - 2026-04-03 (UCG Test Segment)

- Proxmox host `proxmox-anker` now reports `vmbr0` on `10.1.0.92/24` via DHCP with gateway `10.1.0.1`.
- `192.168.2.0/24` services are currently unreachable from `wolfstudiopc` (HTTP probes return `000`).
- From Proxmox, pings to `192.168.2.20-24` fail, so the business VMs are effectively isolated from the old LAN.
- VMs still run (`200/210/220/230` running), so the issue is network reachability, not VM power state.
- Required decision: either move the Proxmox port back to the legacy LAN/VLAN or migrate the full stack (VMs + DNS + routes) into `10.1.0.0/24`.
- `/etc/network/interfaces` is now staged for static `192.168.2.10/24` on `vmbr0` but not applied yet; it will only take effect after the Proxmox port is moved back to the legacy LAN and the network is reloaded.

## CT 100 - Toolbox

- Proxmox metadata:
  - CT ID `100`
  - Name `toolbox`
  - IP config `192.168.2.20/24`, gateway `192.168.2.1`
  - Debian 12, unprivileged LXC, `nesting=1`
- Runtime before remediation:
  - `/opt` was empty
  - Docker was not installed
  - no internal proxy or DNS service was active
- Remediation performed:
  - Proxmox snapshot `codex-pre-toolbox-foundation-20260318` created before changes
  - Docker and Compose installed
  - local IaC deployment added via `ansible/playbooks/deploy_toolbox_foundation.yml`
  - stack deployed to `/opt/homeserver2027/stacks/toolbox-network`
  - systemd unit `homeserver-compose-toolbox-network.service` enabled and active
  - Caddy verified on `192.168.2.20:80`
  - AdGuard Home verified on `192.168.2.20:53`
  - AdGuard admin verified as localhost-only on `127.0.0.1:3000` inside the guest
  - `hs27.internal` rewrites verified to `192.168.2.20`
  - `cloud.hs27.internal`, `odoo.hs27.internal` and `paperless.hs27.internal` returned healthy HTTP
  - `ha.hs27.internal` and `radio.hs27.internal` returned intentional `503` placeholders
  - Proxmox snapshot `codex-pre-toolbox-ts-20260318` created before Tailscale prep
  - `dev0: /dev/net/tun,uid=0,gid=0,mode=0666` added to CT config and verified inside the guest
  - `tailscale` installed from the official Debian repository
  - `tailscaled` enabled and active
  - `net.ipv4.ip_forward = 1` and `net.ipv6.conf.all.forwarding = 1` verified
  - backend state currently `Running`
- Remaining follow-up:
  - approve advertised route `192.168.2.0/24` in the Tailnet admin
  - keep AdGuard Home in opt-in mode until DHCP ownership and rollback are documented
- DNS-/n8n-Drift-Check `2026-04-08`:
  - `CT 100 toolbox` war auf `nameserver 127.0.0.1` gedriftet, obwohl der Hostpfad `127.0.0.1:53` lokal nicht antwortete
  - Verifikation: `nslookup google.com 127.0.0.1` und `nslookup registry-1.docker.io 127.0.0.1` liefen in Timeouts, waehrend dieselben Queries gegen `10.1.0.20:53` sofort erfolgreich waren
  - Remediation: `/etc/resolv.conf` auf `nameserver 10.1.0.20` plus `search hs27.internal` zurueckgezogen
  - Folgeprobe: ein vorbereiteter interner `toolbox-n8n`-Stack konnte danach DNS-seitig aufloesen, scheiterte beim Image-Pull aber reproduzierbar an `archive/tar: invalid tar header`
  - Betriebsentscheidung: `homeserver-compose-toolbox-n8n.service` wieder `disabled`; Stackpfad bleibt nur vorbereitet, kein halbaktiver Live-Dienst

## Toolbox Tailscale Join - 2026-03-18

- Result:
  - `CT 100 toolbox` is now joined to the tailnet
  - backend state is `Running`
  - tailnet DNS name is `toolbox.tail150400.ts.net.`
  - assigned Tailscale IPs:
    - `100.99.206.128`
    - `fd7a:115c:a1e0::af01:cea1`
- Local prefs:
  - `AdvertiseRoutes` includes `192.168.2.0/24`
  - `CorpDNS=false`
  - `Hostname=toolbox`
- Remaining follow-up:
  - verify route approval for `192.168.2.0/24` in the Tailscale admin
  - keep AdGuard pilot mode unchanged until DNS ownership is explicit

## Toolbox Admin Surface Hardening - 2026-03-18

- Change:
  - `ansible/templates/stacks/toolbox-network/docker-compose.yml.j2` now binds AdGuard admin as `127.0.0.1:3000:3000`
- Verification:
  - `make toolbox-network-check` remained green after redeploy
  - `make security-baseline-check` now reports:
    - `toolbox_tcp_ports=22,53,80`
    - `adguard_admin_lan_surface=no`
    - `adguard_admin_local_surface=yes`
    - `security_status=ok`

## PBS Runner Preparation - 2026-03-18

- Deployment path prepared:
  - `ansible/playbooks/deploy_pbs_vm_runner.yml`
  - runner target on Proxmox: `/usr/local/sbin/homeserver2027-deploy-pbs-vm.sh`
- Intended defaults captured from host vars:
  - `VM 240`
  - name `pbs`
  - `4096 MB` RAM
  - `32 GB` system disk on `local-lvm`
  - expected datastore mount on Proxmox: `/srv/pbs-datastore`
  - expected installer ISO path: `/var/lib/vz/template/iso/proxmox-backup-server-current.iso`
- Stage-gate checks exposed for operators:
  - `make pbs-preflight`
  - `make pbs-stage-gate`
  - `make pbs-vm-check`
- Current expected outcome:
  - PBS runner is installed and syntactically valid on Proxmox
  - `VM 240` does not yet exist
  - stage gate remains red for the right reasons:
    - `pbs_iso_present=yes`
    - `pbs_datastore_mount_state=missing`
    - `separate_backup_storage_ready=no`

## PBS ISO Staging - 2026-03-18

- Deployment path:
  - `scripts/proxmox_stage_pbs_iso.sh`
  - `make pbs-iso-stage`
- Result:
  - source ISO staged at `/var/lib/vz/template/iso/proxmox-backup-server_4.1-1.iso`
  - active alias refreshed at `/var/lib/vz/template/iso/proxmox-backup-server-current.iso`
  - verified SHA256:
    - `670f0a71ee25e00cc7839bebb3f399594f5257e49a224a91ce517460e7ab171e`
- Gate impact:
  - `make pbs-stage-gate` now reports `pbs_iso_present=yes`
  - the remaining PBS blocker is separate backup storage at `/srv/pbs-datastore`

## VM 200 - Nextcloud

- Proxmox metadata:
  - VM ID `200`
  - Name `nextcloud`
  - IP config `192.168.2.21/24`, gateway `192.168.2.1`
  - `scsi0` on `local-lvm`, `32G`
  - `onboot=1`
- Guest OS:
  - Debian 12
  - cloud-init status `done`
- Application runtime:
  - Docker stack now managed from `/opt/homeserver2027/stacks/nextcloud/docker-compose.yml`
  - systemd unit `homeserver-compose-nextcloud.service` is enabled and active
  - Containers `nextcloud_app_1`, `nextcloud_db_1`, `nextcloud_redis_1` running
  - HTTP on `http://127.0.0.1/` returned `200 OK`
  - Compose uses persistent Docker volumes
  - Restart policy already set to `always`
- Gaps found before remediation:
  - no QEMU Guest Agent installed
  - Compose is not yet under local IaC control
- Remediation performed:
  - Proxmox agent flag enabled
  - `qemu-guest-agent` installed in guest
  - controlled reboot completed successfully
  - `qm agent 200 ping` verified successfully
  - Docker stack came back automatically and HTTP still returned `200 OK`
  - stack was moved under local IaC control with `ansible/playbooks/deploy_business_stacks.yml`
  - Compose project labels now point to `/opt/homeserver2027/stacks/nextcloud`
  - Drift-Remediation `2026-04-07`:
    - Compose war auf `db=mariadb:10.6` und einen verwaisten `nextcloud:latest`-Altcontainer gedriftet; dadurch brach MariaDB an `10.11`-Redo-Logs und der App-Pfad fiel aus
    - Compose wurde auf dem vorgesehenen Pfad `/opt/homeserver2027/stacks/nextcloud/docker-compose.yml` mit `stack.env`, `db=mariadb:10.11`, `redis=redis:alpine` und `app=nextcloud:latest` neu ausgerichtet
    - `docker-compose up -d --force-recreate --remove-orphans` entfernte den Altcontainer und brachte `db`, `redis` und `app` wieder in den erwarteten Stack
    - der App-native Repair-Pfad lief ueber `php occ upgrade`, `php occ maintenance:repair --include-expensive` und anschliessend `php occ maintenance:mode --off`; direkte DB-Schreibfixes wurden bewusst nicht verwendet
    - anschliessend wurde `homeserver-compose-nextcloud.service` erfolgreich neu gestartet und meldet wieder `active`
    - Laufzeitverifikation `2026-04-07`: `cloud.hs27.internal/` -> `200`, `cloud.hs27.internal/status.php` -> `200`, `maintenance=false`, `needsDbUpgrade=false`, Container `nextcloud_app_1`, `nextcloud_db_1` und `nextcloud_redis_1` laufen
  - Mail-/DNS-Remediation `2026-04-07`:
    - Ursache fuer ausbleibenden Mail-Abruf in der Nextcloud-Mail-App war DNS-Drift auf der VM selbst, nicht die App-Logik
    - `VM 200` nutzte per Cloud-Init noch Tailscale-DNS `100.100.100.100` und Suchdomaint `tail150400.ts.net`, obwohl `tailscaled` dort `inactive` war
    - Persistenz wurde auf Proxmox-Ebene korrigiert: `qm set 200 --nameserver 10.1.0.20 --searchdomain hs27.internal`
    - nach kontrolliertem Reboot zeigte `/etc/resolv.conf` wieder `nameserver 10.1.0.20` und `search hs27.internal`
    - Verifikation: `getent hosts imap.strato.de` in der VM wieder gruen, Docker-Container loest ebenfalls auf, `openssl s_client -connect imap.strato.de:993 -servername imap.strato.de -brief` liefert wieder erfolgreichen TLS-Handshake
  - Alias-Routing `2026-04-08`:
    - `Nextcloud Mail` laeuft auf `Nextcloud 33.0.2` mit Mail-App `5.7.5`
    - der Shared-Posteingang `webmaster@frawo-tech.de` wurde read-only und dann live gegen die Alias-Adressen `wolf@`, `info@` und `agent@` ausgewertet
    - IMAP-Delimiter auf STRATO ist `.`; neue Ordner wurden daher als `Aliases.Agent` und `Aliases.Info` angelegt, waehrend `wolf@` bewusst in `INBOX` bleibt
    - lokal auf `VM 200` wurden `/opt/homeserver2027/tools/nextcloud_imap_alias_router.py`, `/usr/local/sbin/nextcloud_alias_router_runner.sh`, `hs27-nextcloud-alias-router.service` und `hs27-nextcloud-alias-router.timer` eingerichtet
    - Timer-Frequenz: `OnBootSec=2min`, `OnUnitActiveSec=5min`
    - erste Live-Trennung verschob `9` bestehende Alias-Mails aus `INBOX` in die zugehoerigen Alias-Ordner
    - End-to-End-Probe: neue Testmail an `info@frawo-tech.de` wurde nach Service-Lauf von `INBOX` nach `Aliases.Info` verschoben
    - Rueckzug `2026-04-08` spaet: `wolf@`-Mails wurden wieder aus `Aliases.Wolf` in `INBOX` geholt; neue `wolf@`-Probe blieb danach in `INBOX`
    - Laufzeitverifikation danach: `INBOX=6`, `Aliases.Agent=1`, `Aliases.Info=5`, `Aliases.Wolf=0`

## VM 220 - Odoo

- Proxmox metadata:
  - VM ID `220`
  - Name `odoo`
  - IP config `192.168.2.22/24`, gateway `192.168.2.1`
  - `scsi0` on `local-lvm`, `32G`
  - `onboot=1`
- Guest OS:
  - Debian 12
  - cloud-init status `done`
- Application runtime before remediation:
  - Docker Compose file found at `/home/wolf/odoo/docker-compose.yml`
  - `odoo_web_1` and `odoo_db_1` were both exited with status `255`
  - No restart policy configured
  - `http://127.0.0.1:8069/` did not answer
- Proxmox issue found:
  - same disk was attached twice as `scsi0` and `virtio0`
  - boot order targeted `virtio0`
  - first snapshot attempt failed because the duplicate disk attachment caused snapshot conflicts
- Remediation performed:
  - Odoo containers started successfully and served HTTP again
  - Restart policy set to `unless-stopped` for both containers
  - Duplicate `virtio0` disk attachment removed from Proxmox config
  - Boot order corrected to `scsi0`
  - Proxmox agent flag enabled on the VM
  - `qemu-guest-agent` installed in guest and verified with `qm agent 220 ping`
  - reboot path validated by stopping and starting the VM after the cleanup
  - Snapshot `codex-post-config-cleanup-20260317` created successfully after cleanup
  - stack was moved under local IaC control at `/opt/homeserver2027/stacks/odoo/docker-compose.yml`
  - systemd unit `homeserver-compose-odoo.service` is enabled and active
  - Compose project labels now point to `/opt/homeserver2027/stacks/odoo`
  - `http://127.0.0.1:8069/web/login` returned `200 OK` after the cutover
- Remaining follow-up:
  - document backup and restore proof end to end

## VM 230 - Paperless

- Proxmox metadata:
  - VM ID `230`
  - Name `paperless`
  - IP config `192.168.2.23/24`, gateway `192.168.2.1`
  - `scsi0` on `local-lvm`, `32G`
  - `onboot=1`
- Application runtime:
  - Docker stack now managed from `/opt/homeserver2027/stacks/paperless/docker-compose.yml`
  - systemd unit `homeserver-compose-paperless.service` is enabled and active
  - Paperless stack is running and healthy
  - HTTP listens on port `8000`
  - Postgres, Redis, Tika and Gotenberg containers are up
  - `http://127.0.0.1:8000/` returned `302`
- Remediation performed:
  - Proxmox agent flag enabled on the VM
  - `qemu-guest-agent` installed in guest
  - controlled reboot completed successfully
  - `qm agent 230 ping` verified successfully

## Backup and Restore Proof - 2026-03-18

- Proxmox storage target for interim proof: `local`
- Successful local `vzdump` archives:
  - `VM 200` -> `vzdump-qemu-200-2026_03_18-00_18_22.vma.zst` (`1.8G`)
  - `VM 220` -> `vzdump-qemu-220-2026_03_18-00_18_59.vma.zst` (`1.7G`)
  - `VM 230` -> `vzdump-qemu-230-2026_03_18-00_19_33.vma.zst` (`2.8G`)
- Restore validation:
  - source `VM 220`
  - restored to temporary `VM 920`
  - temporary IP `192.168.2.240`
  - `qm agent 920 ping` returned successfully
  - `http://192.168.2.240:8069/web/login` returned `200 OK`
  - `VM 920` was removed after verification
- Remaining backup follow-up:
  - promote the proven local path into scheduled PBS jobs with retention and regular restore drills
  - **PBS-v1 Drill 2026-03-24**: Successful manual restore of VM 220 to VM 320 (`odoo-restore-test`) on `local-lvm`

## Service Drift Check - 2026-03-18

- Check path: `./scripts/business_service_drift_check.sh`
- Result:
  - Nextcloud: systemd service enabled and active, compose file present, app endpoint returned `200`
  - Odoo: systemd service enabled and active, compose file present, `/web/login` returned `200`
  - Paperless: systemd service enabled and active, compose file present, `/accounts/login/` returned `200`
- Operational use:
  - the same check is exposed as `make business-drift-check`
  - run it after stack updates, host reboots or IaC rollouts

## Local Backup Retention - 2026-03-18

- Interim retention path until PBS is live:
  - keep latest `2` local qemu archives per business VM
  - inspect with `make backup-list`
  - prune preview with `make backup-prune-dry-run`
  - destructive cleanup only with `make backup-prune`

## Interim Scheduled Local Backup Ops - 2026-03-18

- Proxmox host service:
  - `homeserver2027-local-business-backup.service`
- Proxmox host timer:
  - `homeserver2027-local-business-backup.timer`
  - scheduled daily at `02:40`
- Deployment path:
  - `ansible/playbooks/deploy_proxmox_local_backup_ops.yml`
- Verified manual timer-backed run:
  - service exited with `status=0/SUCCESS`
  - created fresh archives for `VM 200`, `VM 220` and `VM 230`
  - resulting local archive count after pruning:
    - `VM 200` -> `2`
    - `VM 220` -> `2`
    - `VM 230` -> `2`
  - after HAOS integration the timer-backed service was rerun successfully for `VM 200`, `VM 210`, `VM 220` and `VM 230`
  - resulting retention now keeps `2` local archives per secured VM, including `VM 210`

## HAOS Runner Preparation - 2026-03-18

- Deployment path prepared:
  - `ansible/playbooks/deploy_haos_vm_runner.yml`
  - runner target on Proxmox: `/usr/local/sbin/homeserver2027-deploy-haos-vm.sh`
- Intended defaults captured from host vars:
  - `VM 210`
  - name `haos`
  - `4096 MB` RAM
  - `32 GB` disk on `local-lvm`
  - `q35`, `OVMF`, `virtio-scsi-single`, `vmbr0`
- Stage-gate checks exposed for operators:
  - `make haos-preflight`
  - `make haos-stage-gate`
  - `make haos-vm-check`
- Current expected outcome after Tailscale join:
  - HAOS stage gate is green
  - baseline HAOS can now be built without blocking on USB dongles

## VM 210 - Home Assistant OS - 2026-03-18

- Proxmox metadata:
  - VM ID `210`
  - Name `haos`
  - `q35`, `OVMF`, `virtio-scsi-single`
  - `2 vCPU`
  - `4096 MB` RAM
  - `scsi0` on `local-lvm`, `32G`
  - `onboot=1`
- Deployment path used:
  - `/usr/local/sbin/homeserver2027-deploy-haos-vm.sh`
- Runtime result:
  - `VM 210` was created successfully and started cleanly
  - stabilized network identity:
    - MAC `BC:24:11:D5:BA:30`
    - hostname `homeassistant.local`
    - static in-guest address `192.168.2.24`
  - Home Assistant answered on `http://192.168.2.24:8123/` with `HTTP 200`
- Important follow-up:
  - internal proxy hostname `ha.hs27.internal` now returns `HTTP 200` through `CT 100`
  - Home Assistant reverse-proxy trust was enabled for toolbox source IP `192.168.2.20`
  - a local `vzdump` archive for `VM 210` now exists on Proxmox `local`
  - USB passthrough is still not actionable because no target adapter is visible on the Proxmox host

## VM 320 - Restore Test (2026-03-24)

- Proxmox metadata:
  - VM ID `320`
  - Name `odoo-restore-test`
  - Restored from `pbs-interim` (Source: VM 220 odoo, March 21 backup)
  - Target storage `local-lvm`
- Verification:
  - Task initiated 2026-03-24 12:01 (local)
  - Log confirmed successful extraction to `local-lvm:vm-320-disk-0`

## Business VM Resolution Hardening - 2026-03-18

- Deployment path:
  - `ansible/playbooks/harden_business_network_baseline.yml`
  - `ansible/templates/network/90-homeserver2027-resolved-hardening.conf.j2`
- Change:
  - installed `/etc/systemd/resolved.conf.d/90-homeserver2027-hardening.conf`
  - set `LLMNR=no`
  - set `MulticastDNS=no`
  - restarted `systemd-resolved` on `VM 200`, `VM 220` and `VM 230`
- Verification:
  - `make business-drift-check` remained green after the change
  - `make security-baseline-check` now reports:
    - `nextcloud_tcp_ports=22,80`
    - `odoo_tcp_ports=22,8069`
    - `paperless_tcp_ports=22,8000`
    - `llmnr_open=no`
    - `security_status=ok`
- Snapshot hygiene:
  - temporary snapshots `codex-pre-llmnr-0318` were created before the change
  - temporary snapshots were removed again after verification

## Snapshot Notes

- `VM 200`: snapshot `codex-pre-qga-20260317` created successfully
- `VM 220`: first snapshot failed before cleanup due duplicate disk mapping; post-cleanup snapshot succeeded
- `VM 200`, `VM 220`, `VM 230`: snapshot `codex-pre-iac-cutover-20260317` created successfully before the local IaC cutover
- `VM 230`: snapshot `codex-pre-paperless-qga-20260317` created successfully before installing the guest agent
- Temporary validation snapshots for `VM 200`, `VM 220` and `VM 230` were removed again after successful verification to avoid thin-pool clutter

## Storage Status

- Proxmox initially reported thin-pool warnings during snapshot creation.
- Remediation performed on `2026-03-17`:
  - temporary `codex-*` snapshots on `VM 200`, `VM 220` and `VM 230` removed after validation
  - `/etc/lvm/lvm.conf` backed up to `/etc/lvm/lvm.conf.pre-codex-thinpool-20260317`
  - LVM thin-pool autoextend enabled with `thin_pool_autoextend_threshold = 70` and `thin_pool_autoextend_percent = 20`
  - `pve/data` extended from `140.87 GiB` to `156.88 GiB`
  - verification snapshot `tp-verify-20260317` on `VM 200` created and removed without the previous thin-pool protection warning
- Current live state:
  - `local-lvm` is active and healthy
  - thin-pool data usage is about `13%`
  - one older non-Codex snapshot remains on `VM 100` as legacy state outside this audit scope
  - `local` directory storage is after the proof and PBS ISO staging at about `31.85%` usage

## Network Transition Recovery - 2026-04-03

- Root cause for `Odoo`/`Nextcloud`/`Paperless`/`Portal` loss from `wolfstudiopc` was not an app outage.
- `proxmox-anker` had already moved to the new UCG segment as `10.1.0.92/24`, while the business guests stayed on an isolated internal `192.168.2.0/24`.
- Because `wolfstudiopc` itself is still on the old EasyBox-connected `192.168.2.0/24`, the same subnet existed on two different L2 domains and direct client access to the guests stopped working.
- Remediation applied:
  - kept `vmbr0` on DHCP in `10.1.0.0/24`
  - kept helper alias `192.168.2.10/24` on Proxmox
  - restored temporary internal legacy gateway `192.168.2.1/24` on Proxmox
  - enabled a persistent transition router/NAT on Proxmox for the isolated guest segment
  - started `CT 110 storage-node`, which restored the media bind-mount required by `CT 100 toolbox`
  - started `CT 100 toolbox` and recovered its Tailscale/mobile frontdoors
- Verified from `wolfstudiopc` over Tailscale:
  - `http://100.99.206.128:8444/web/login` -> `200` Odoo
  - `http://100.99.206.128:8445/` -> `302` Nextcloud
  - `http://100.99.206.128:8446/accounts/login/` -> `200` Paperless
  - `http://100.99.206.128:8447/` -> `200` Portal
  - `http://100.99.206.128:8442/alive` -> `200` Vaultwarden
  - `http://100.99.206.128:8448/` -> `302` Radio
  - `http://100.99.206.128:8449/` -> `302` Media
- Remaining follow-up:
  - `Home Assistant` frontdoor is now green again on `http://100.99.206.128:8443/` after extending HA trusted proxies to include the Proxmox transition-router path.
  - If classic `hs27.internal` hostnames should work directly on `wolfstudiopc` before the full migration, that needs a separate Windows hosts/DNS decision because local admin access is gated.

### Canonical Next Sequence

- Freeze the current working transition state: Proxmox stays on `10.1.0.92/24`, the guests stay isolated on the internal `192.168.2.0/24`, and operators use `Tailscale` plus toolbox frontdoors.
- Use the already published UCG VLAN/subnet target from `UCG_NETWORK_ARCHITECTURE.md` before any VM/CT renumbering; do not reopen subnet design unless the SSOT itself changes.
- Keep service entrypoints stable through toolbox frontdoors and `hs27.internal` names rather than re-teaching users direct guest IPs.
- First low-risk runtime success is now live on `CT 100 toolbox`: additive alias `10.1.0.20/24` is active and persistent, the `portal` vhost answers on the target IP, and the toolbox frontdoors remain `8/8` green.
- Use one low-risk pilot move first, then migrate the core business services in this order:
  - `Odoo`
  - `Nextcloud`
  - `Paperless`
- Move `Home Assistant` only after the business trio is stable on the new network model.
- Revisit `Vaultwarden` only with explicit rollback discipline because it is security-critical.
- Handle `PBS` and any storage redesign last.

## Platform Health Baseline - 2026-04-04

- Repeatable audit path now lives in `scripts/platform_health_audit.py` and writes to `artifacts/platform_health/latest_report.md`.
- Current hard facts:
  - `proxmox-anker` is operational and not the hottest capacity problem.
  - `stock-pve` is the current runtime pressure point: host swap `6.3 / 8.0 GiB`, storage `hdd-backup` at `84%`.
  - `Odoo` is runtime-green: direct `192.168.2.22:8069/web/login` returns `200` from Anker and the Tailscale frontdoor `100.99.206.128:8444/web/login` also returns `200`.
  - `VM 240 PBS` remains stopped and the PBS storages on Anker are still not the green consolidated backup target.
- Optimization hints from the same audit:
  - later rightsizing candidates on Anker are `CT 100 toolbox`, `CT 110 storage-node`, and `CT 120 vaultwarden`.
  - immediate pressure guests in Stockenweiler are `VM 360 homeassistant-eltern` and `VM 210 azuracast-vm`.
- Strategic consequence:
  - do not call `Odoo` production-ready only because the runtime is healthy; first freeze the intended module/profile rollout and customer portal scope.
  - do not thin Stockenweiler blindly; first secure the legacy `yourparty` payload across `VM 210`, `CT 207`, `CT 208`, and `CT 211`.

## VM 200 nextcloud - Odoo Agent Intake Deployment 2026-04-09

- Neue Runtime-Dateien ausgerollt:
  - `/opt/homeserver2027/tools/odoo_rpc_client.py`
  - `/opt/homeserver2027/tools/odoo_agent_intake_bridge.py`
  - `/usr/local/sbin/odoo_agent_intake_runner.sh`
  - `/root/.config/homeserver2027/odoo_agent_rpc.env` (root-only)
- Neue systemd-Units:
  - `hs27-odoo-agent-intake.service`
  - `hs27-odoo-agent-intake.timer`
- Verifiziert:
  - Timer `enabled` und `active`
  - letzter erfolgreicher Lauf: `checked=0`, `created=0`, `moved=0` nach dem initialen Proof-Lauf
  - initialer Proof-Lauf davor: `created=1`, `moved=1`
- Zweck:
  - Odoo liest fuer `agent@` nicht die gesamte Shared-INBOX, sondern nur den bereits getrennten Ordner `Aliases.Agent`

## Media / Wolf.EE Snapshot 2026-04-09

- `Jellyfin` auf `CT 100 toolbox` ist live und liest read-only von `/srv/media-library`.
- Der eigentliche Netzwerk-Musikpfad ist dort verifiziert als:
  - `/srv/media-library/music-network`
  - Source: `//10.1.0.30/Media`
  - FSTYPE: `cifs`
- Sichtbar fuer den Mediaserver:
  - `/srv/media-library/music-network/yourparty_Libary`
  - Groessenordnung des Netzwerkbestands: ca. `70G`
- Der zentrale Medienbestand liegt damit aktuell produktiv auf `CT 110 storage-node` unter:
  - `/mnt/data/media/yourparty_Libary`
- `Wolf.EE` ist als USB-NTFS-Platte auf `proxmox-anker` sichtbar:
  - Device: `/dev/sda2`
  - Label: `Wolf.EE`
  - Filesystem: `ntfs`
- `Wolf.EE` wurde fuer Sichtpruefung bewusst nur read-only gemountet:
  - Mountpoint: `/mnt/wolf-ee`
  - Mount-Optionen: `ro`
- Sichtbare grobe Sortierkandidaten auf `Wolf.EE`:
  - `MUSIK` ca. `6.5G`
  - `Sets` ca. `3.7G`
  - `Job Jobse` ca. `437M`
  - `von HDD` ca. `157G`
  - `Plugins` ca. `177G`
  - `StudioOne` ca. `32G`
  - `Nicotine` ca. `18G`
- Wichtige Einordnung:
  - Der Mediaserver sieht die zentrale Musik bereits.
  - `Wolf.EE` ist derzeit **keine** produktive Medienquelle, sondern eine separate read-only Sichtungs-/Sortierquelle.
  - Ein direkter `Stockenweiler`-Quellpfad wurde in dieser Session nicht live eingebunden.

## Media Import - Wolf.EE nach storage-node 2026-04-09

- Erster kontrollierter Medienimport von `Wolf.EE` wurde in den zentralen Review-/Importpfad ausgefuehrt:
  - Ziel: `/mnt/data/media/yourparty_Libary/incoming/Wolf_EE_20260409`
- Importierte Ordner:
  - `Job Jobse`
  - `The_TraXx`
  - `Sets`
  - `MUSIK`
- Verifizierte Zielgroessen:
  - `Job Jobse` `438M`
  - `The_TraXx` `2.7G`
  - `Sets` `3.7G`
  - `MUSIK` `6.5G`
  - gesamt ca. `14G`
- Wichtige Betriebsfolge:
  - `storage-node` steht danach bei `84G used / 9.1G free / 91%`
  - fuer diesen Block keine weiteren grossen Medienimporte mehr auf denselben Pfad ziehen
- `Stockenweiler` bleibt fuer Live-Medienimport weiter blockiert:
  - von `CT 100 toolbox` aktuell keine Route / kein Ping nach `192.168.178.25`

## Media Transport / Capacity Clarification 2026-04-09

- `Stockenweiler` ist ueber Tailscale als Peer sichtbar und antwortet auf Peer-Ebene:
  - Peer: `stockenweiler-pve`
  - Tailscale-IP: `100.91.20.116`
  - `tailscale ping stockenweiler-pve` von `CT 100 toolbox` liefert `pong`
- Der produktiv relevante Medienpfad nach `Stockenweiler` ist trotzdem nicht vorhanden:
  - auf `CT 100 toolbox` existiert aktuell keine Route fuer `192.168.178.0/24`
  - `tailscale status` meldet weiter `Some peers are advertising routes but --accept-routes is false`
  - daraus folgt: Peer erreichbar, Stockenweiler-LAN fuer Import aber nicht angebunden
- Die geplante Entlastungs-SSD auf `proxmox-anker` ist aktuell nicht schreibbar:
  - Mount: `/mnt/music_ssd`
  - Device: `/dev/sdb1`
  - Filesystem: `exfat`
  - Mount-Optionen: `ro,...,errors=remount-ro`
  - `touch /mnt/music_ssd/.hs27_write_probe` scheitert mit `Read-only file system`
  - `dmesg` meldet `exFAT-fs (sdb1) ... Filesystem has been set read-only`
- Einordnung:
  - `proxmox-anker` selbst ist nicht das akute Kapazitaetsproblem (`/` ca. `84%`)
  - der aktuelle Druckpunkt ist `CT 110 storage-node` mit ca. `91%` nach dem `Wolf.EE`-Reviewimport
  - weitere grosse Medienimporte bleiben bis zu einer sicheren Entlastung bewusst gestoppt
