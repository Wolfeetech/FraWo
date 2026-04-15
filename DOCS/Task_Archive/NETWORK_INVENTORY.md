# Network Inventory

## Metadata

- Observed at: `2026-03-17`
- Primary scan source: `nmap -sn 192.168.2.0/24` executed from `proxmox`
- Secondary sources:
  - `qm config` for `VM 200`, `VM 220`, `VM 230`
  - direct SSH checks on `toolbox`, `nextcloud`, `odoo`, `paperless`
  - Easy Box device list reviewed on `2026-03-18`
- Router baseline: Vodafone Easy Box on `192.168.2.1`
- UCG test segment observation (2026-04-05):
  - Proxmox `vmbr0` DHCPs as `10.1.0.92/24` with gateway `10.1.0.1`
  - `vmbr0` stays on DHCP in the UCG segment; Proxmox still carries legacy aliases `192.168.2.10/24` plus the emergency gateway alias `192.168.2.1/24`
  - Core service nodes (`toolbox`, `nextcloud`, `odoo`, `paperless`, `haos`, `vaultwarden`) are migrated onto `10.1.0.0/24`
  - UCG static route `Anker-Legacy-Bridge` remains configured for `192.168.2.0/24 -> 10.1.0.92`, but stays shadowed by the WAN overlap and is only a fallback path
- Lease validation status:
  - Router credential is now stored in Ansible Vault
  - `user_lang.json` can now be fetched headlessly through a real browser-context probe against `https://192.168.2.1`
  - raw CLI HTTP clients still receive `UNKNOWN 400 Bad Request` from the EasyBox 805
  - authenticated EasyBox login plus `overview.json` extraction are now reproduced headlessly through the browser-context path
  - latest browser probe showed `trying_times=0` and `delay_time=0`; do not brute-force further login attempts
- `CT 100 toolbox` is now joined to Tailscale and reports `BackendState=Running`
- the toolbox tailnet DNS name is `toolbox.tail150400.ts.net.`
- toolbox now advertises the subnet route `10.1.0.0/24` (Tailnet approval pending)
  - authenticated overview extraction on `2026-03-19` yielded exact live mappings:
    - `fireTV` -> `192.168.2.100` / `08:12:A5:EC:66:A8`
    - `Franz_iphone` -> `192.168.2.122` / `56:26:8F:F1:F7:94`
    - `udhcpc1.21.1` -> `192.168.2.101` / `90:F1:AA:F2:C5:E6`
    - `udhcp 1.24.1` -> `192.168.2.134` / `B0:4A:39:0E:38:84`
    - `Shelly_plug_repeater` -> current authenticated overview now shows `192.168.2.117` / `B0:81:84:A5:EA:08`
    - `shellyplugsg3-8cbfea968024` -> `192.168.2.107` / `8C:BF:EA:96:80:24`
- authenticated overview extraction on 2026-03-24 yielded:
    - .141 -> D0:C9:07:EF:8C:32 (Apple Mobile)
    - .142 -> D0:C9:07:DA:70:6C (Apple Mobile)
    - .143 -> D0:C9:07:DA:6E:F2 (Apple Mobile)
    - .144 -> D0:C9:07:EF:8A:F0 (Apple Mobile)
- Remaining router-only labels still to map 1:1 onto active IPs:
    - none

  - the authenticated overview also shows additional current router labels worth keeping as soft aliases:
    - `Surface_Laptop` had appeared separately on `192.168.2.118`; operator clarified on `2026-03-31` that this is Wolfs `Arbeitssurface` and must stay separate from `Franz Surface Laptop`
    - `yourparty-Surface-Go` is visible on `192.168.2.154`
    - `RE355` is visible on `192.168.2.126`
    - `iPhone-3-Pro` is visible on `192.168.2.129`
  - The Surface Go is now rebuilt and operational as a managed frontend:
    - SSH and Tailscale admin are live
    - local portal path and sleep hardening are live
    - remaining work is touch/browser UX polish, not baseline rebuild
- Planned edge replacement:
  - `UniFi Cloud Gateway Ultra (UCG-Ultra)` is now active in a test segment; Proxmox lives on `10.1.0.92/24` and the core services are migrated to `10.1.0.0/24`, while `192.168.2.0/24` remains only as an emergency fallback
  - `AdGuard Home` is active in opt-in mode on `CT 100` and currently serves `hs27.internal` plus external DNS for test clients
  - AdGuard admin on `CT 100` is now localhost-only on `127.0.0.1:3000`
  - Caddy is active on `CT 100` as the internal HTTP frontdoor for `portal.hs27.internal`, `cloud.hs27.internal`, `odoo.hs27.internal`, `paperless.hs27.internal`, `ha.hs27.internal` and `radio.hs27.internal`
  - Tailscale is live on `CT 100`; the node is joined and currently reports `Running`
  - public exposure is planned only as a later controlled edge phase, not as part of the current live network

## Classification Model

| Zone | Meaning |
| --- | --- |
| `core` | Router and core network control plane |
| `management` | Proxmox and direct admin endpoints |
| `business` | Business workloads for GbR operations |
| `infra-services` | Supporting infrastructure services |
| `smart-home-iot` | IoT and automation endpoints |
| `media-private` | Private media and entertainment devices |
| `trusted-clients` | User laptops and phones with expected access |
| `unknown-review` | Unclassified devices pending review |

## Core, Management, Business and Infra

| IP | Hostname | MAC / Vendor | Device Class | Zone | Owner | Mgmt | DHCP/Static | Criticality | Status | Source | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `192.168.2.1` | `easy.box` | `78:B3:9F:08:F5:60` / unknown | router | `core` | shared-network | web | dhcp-router | critical | active | nmap + browser audit | finish headless login path; `user_lang.json` works, full lease extraction still pending |
| `10.1.0.92` | `proxmox-anker` | not captured in scan | hypervisor | `management` | homeserver-gbr | ssh + tailscale | dhcp | critical | active | ssh + live ip route | UCG segment active and kept; Proxmox now bridges the migration with helper aliases `192.168.2.10/24` + `192.168.2.1/24` and a temporary transition router for the isolated legacy guests |
| `192.168.2.10` | `proxmox-anker.local` | not captured in scan | hypervisor | `management` | homeserver-gbr | ssh | static | critical | stale | ssh config + nmap | host is currently on `10.1.0.92/24`; restore legacy IP only if rolling back the UCG test |
| `10.1.0.20` | `toolbox` | `BC:24:11:AC:BD:44` / Proxmox | lxc admin toolbox | `infra-services` | homeserver-gbr | ssh + http + dns + vpn | static | high | active | pct + ansible + toolbox network check + tailscale + portal pilot preflight + 2026-04-07 firewall/runtime check | productive frontdoor currently runs as Docker container `toolbox-network_caddy_1`; IP updated to `10.1.0.20` (local) / `100.82.26.53` (tailnet), OpenClaw secure key installed |
| `10.1.0.21` | `nextcloud` | `BC:24:11:D2:A4:3C` / Proxmox | vm app host | `business` | homeserver-gbr | ssh + http | static | high | active | qm + ssh + http + local backup proof | move from local proof backups to scheduled PBS jobs and proxy naming; OpenClaw secure key installed |
| `10.1.0.22` | `odoo` | `BC:24:11:AA:BB:CC` / Proxmox | vm app host | `business` | homeserver-gbr | ssh + http | static | high | active | qm + qga + docker + http + 2026-04-07 remediation check | Compose/frontdoor/version drift was remediated on `2026-04-07`; runtime now matches the `Odoo 17` database again, direct `8069`, `odoo.hs27.internal` and `100.82.26.53:8444` return `HTTP 200`; OpenClaw secure key installed |
| `10.1.0.23` | `paperless` | `BC:24:11:E0:C3:01` / Proxmox | vm app host | `business` | homeserver-gbr | ssh + http | static | high | active | qm + ssh + http + local backup proof | move from local proof backups to scheduled PBS jobs and proxy naming |
| `10.1.0.26` | `vaultwarden` | not captured / Proxmox | lxc app host | `business` | homeserver-gbr | ssh + http | static | high | active | pct + http + caddy | keep SMTP health check and backup proof tracked for the MVP gate |
| `10.1.0.30` | `storage-node` | not captured / Proxmox | lxc storage node | `infra-services` | homeserver-gbr | ssh + smb | static | high | active | pct + smb + mount verification | keep SMB mounts aligned with media + docs paths and avoid drift from the IaC mounts |

## Smart Home, Media and Trusted Clients

| IP | Hostname | MAC / Vendor | Device Class | Zone | Owner | Mgmt | DHCP/Static | Criticality | Status | Source | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `192.168.2.100` | `fireTV` | `08:12:A5:EC:66:A8` / Amazon | fire tv streamer | `media-private` | private-household | app | dhcp | medium | active | nmap + authenticated router overview | router label now confirmed; map room and TV association in device register |
| `192.168.2.101` | `udhcpc1.21.1` | `90:F1:AA:F2:C5:E6` / Samsung | samsung tv or media endpoint candidate | `media-private` | private-household | app | dhcp | medium | active | nmap + authenticated router overview | router label now confirmed; verify whether this is the Samsung TV endpoint |
| `192.168.2.104` | `fritz.repeater.local` | `C0:25:06:0A:80:74` / AVM | wifi repeater | `infra-services` | private-household | web | dhcp | medium | active | nmap | verify downstream clients behind repeater |
| `192.168.2.106` | `shellyoutdoorsg3-e4b063d5661c.local` | `C0:25:06:0A:80:74` / AVM seen via repeater | shelly device | `smart-home-iot` | growbox | web | dhcp | medium | active | nmap + router page | confirmed growbox Shelly; still validate real MAC and reservation plan |
| `192.168.2.107` | `shellyplugsg3-8cbfea968024` | `8C:BF:EA:96:80:24` / unknown | shelly plug | `smart-home-iot` | growbox | web | dhcp | medium | active | authenticated router overview + prior nmap | exact router label now confirmed; keep as growbox Shelly plug |
| `192.168.2.109` | `shellyblugwg3-34cdb07897c8.local` | `34:CD:B0:78:97:C8` / unknown | shelly bluetooth gateway | `smart-home-iot` | growbox | web | dhcp | medium | active | nmap + router page | confirmed growbox Bluetooth gateway; HA candidate once HAOS is live |
| `192.168.2.110` | `Google-Home-Mini.local` | `48:D6:D5:DA:6A:32` / Google | smart speaker | `smart-home-iot` | private-household | app | dhcp | low | active | nmap | confirm use or retire from active inventory |
| `192.168.2.112` | `Wolf_Pixel` | `22:93:66:09:A7:48` / private | mobile phone | `trusted-clients` | wolf | local-device | dhcp | medium | active | nmap + router page | confirmed resident device; keep as admin-capable Tailscale client |
| `192.168.2.113` | `android-dhcp-14.local` | `44:F5:3E:E4:71:74` / unknown | mobile client | `trusted-clients` | resident-review | local-device | dhcp | low | active | nmap + router page + authenticated router overview | keep as separate resident mobile client; no longer a candidate for `Franz_iphone` |
| `192.168.2.114` | `shellyplugsg3-b08184a5ea08.local` | `C0:25:06:0A:80:74` / AVM seen via repeater | shelly plug via repeater | `smart-home-iot` | growbox | web | dhcp | medium | active | prior nmap + partial router decoding | earlier observation only; the newer authenticated overview instead shows `Shelly_plug_repeater` on `192.168.2.117`, so verify current live lease before reserving |
| `192.168.2.118` | `Surface_Laptop` | not yet captured | work laptop | `trusted-clients` | wolf | local-device + tailscale | dhcp | medium | active-operator-clarified | authenticated router overview + operator clarification | Wolfs `Arbeitssurface`; keep separate from `Franz Surface Laptop`, use split-access model: default local independent work on WLAN, internal apps/admin on-demand via Tailscale, no permanent full-tunnel and no blind `RouteAll` |
| `192.168.2.122` | `Franz_iphone` | `56:26:8F:F1:F7:94` / private | mobile phone | `trusted-clients` | franz | local-device | dhcp | medium | active | authenticated router overview | confirmed resident device; Tailscale candidate after phone validation |
| `192.168.2.126` | `SonRoku.local` | `EC:08:6B:31:19:56` / TP-Link | Roku TV addon | `media-private` | private-household | app | dhcp | low | active | nmap + router page + user note | confirmed as Roku TV addon |
| `192.168.2.132` | `wolf-ZenBook-UX325EA-UX325EA.local` | `00:42:38:B2:66:82` / Intel | laptop | `trusted-clients` | wolf | ssh/local-device + tailscale + anydesk | dhcp | medium | active | nmap + local verification | primary admin client; Tailscale joined and AnyDesk active |
| `100.79.103.59` | `DESKTOP-7LMP02S` | not captured / Microsoft | review control node | `trusted-clients` | wolf | local-device + repo-ssh + tailscale | tailscale-managed | medium | active-clean-control-node | local verification 2026-04-15 | `wolf_surface` is the clean FraWo control node; workspace bootstrap, repo checkout, Git, OpenSSH and Tailscale are present. Remaining clean fix is split DNS for `hs27.internal` through Tailscale admin, not a local hosts-file workaround |
| `192.168.2.134` | `udhcp 1.24.1` | `B0:4A:39:0E:38:84` / Roborock | robot vacuum candidate | `smart-home-iot` | private-household | app | dhcp | low | active | authenticated router overview + prior nmap | router label now confirmed; supersedes the older `192.168.2.135` Roborock observation |
| `192.168.2.154` | `yourparty-Surface-Go.local` | `D8:C4:97:C6:0E:B0` / Microsoft | shared touch frontend | `trusted-clients` | shared-household | ssh + local-device + tailscale | dhcp | medium | active-managed | ssh + tailscale + user confirmation | keep managed frontend path stable; remaining work is local browser/touch UX polish and later DHCP reservation |
| `192.168.2.162` | `WOLFSTUDIOPC.local` | `34:5A:60:44:22:F4` / unknown | studio workstation | `trusted-clients` | wolf | local-device + smb + tailscale | dhcp | medium | active-tailscale-joined-no-ssh | authenticated router overview + port probe + tailscale ping 2026-04-15 | joined in Tailscale as `100.98.31.60`; SMB is reachable, but `SSH` on `22/tcp` is still closed. Next step is to enable `OpenSSH Server`, place the repo locally, then run `scripts/bootstrap_windows_workspace.cmd` |
| `192.168.2.135` | `localhost` | `B0:4A:39:0E:38:84` / Roborock | robot vacuum | `smart-home-iot` | private-household | app | dhcp | low | stale-observation | older nmap only | superseded by the authenticated router overview on `192.168.2.134`; keep only as historical scan note |
| `192.168.2.141` | `d0:c9:07:ef:8c:32` | `D0:C9:07:EF:8C:32` / Apple | mobile phone | `trusted-clients` | family | local-device | dhcp | low | active | router overview | family Apple device; confirmed during 2026-03-24 lease review |
| `192.168.2.142` | `d0:c9:07:da:70:6c` | `D0:C9:07:DA:70:6C` / Apple | mobile phone | `trusted-clients` | family | local-device | dhcp | low | active | router overview | family Apple device; confirmed during 2026-03-24 lease review |
| `192.168.2.143` | `d0:c9:07:da:6e:f2` | `D0:C9:07:DA:6E:F2` / Apple | mobile phone | `trusted-clients` | family | local-device | dhcp | low | active | router overview | family Apple device; confirmed during 2026-03-24 lease review |
| `192.168.2.144` | `d0:c9:07:ef:8a:f0` | `D0:C9:07:EF:8A:F0` / Apple | mobile phone | `trusted-clients` | family | local-device | dhcp | low | active | router overview | family Apple device; confirmed during 2026-03-24 lease review |
| `10.1.0.24` | `homeassistant.local` | `BC:24:11:D5:BA:30` / Proxmox | Home Assistant OS VM | `smart-home-iot` | homeserver-gbr | web + qga | static-in-guest | high | active | qm guest exec + qga + http + caddy | keep `ha.hs27.internal` and local backup coverage green; add USB adapters when physically present |


## Unknown Review Bucket

| IP | Hostname | MAC / Vendor | Device Class | Zone | Owner | Mgmt | DHCP/Static | Criticality | Status | Source | Next Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |



## Planned Network Hardware

| Device | Planned Role | Current State | Integration Gate |
| --- | --- | --- | --- |
| `UniFi Cloud Gateway Ultra (UCG-Ultra)` | active gateway transition plane, DHCP reservation plane, firewall policy anchor, VLAN-ready network edge | active in transition mode; Proxmox currently lives on `10.1.0.92` in VLAN 101 while the legacy guest segment remains isolated behind the transition router | keep the published VLAN schema in `UCG_NETWORK_ARCHITECTURE.md` as the target model; next gates are firewall policy, Proxmox VLAN trunk adoption, and controlled service cutover |

## Planned Infrastructure Services

| Service | Planned Role | Current State | Activation Gate |
| --- | --- | --- | --- |
| `AdGuard Home` | internal DNS filtering, local upstream for `hs27.internal`, opt-in resolver for trusted clients | active in opt-in mode on `CT 100`; not LAN default DNS | keep on pilot clients first; promote to primary LAN DNS only after controlled DHCP ownership, lease cleanup and rollback proof |
| `Storage Node (CT 110)` | single source of truth SMB/NFS data node for documents + media | active on `10.1.0.30`, client integration still open | mount `\\10.1.0.30\Media\yourparty_Libary` and the shared documents path cleanly into Nextcloud, Paperless, Jellyfin, and radio-node |
| `AzuraCast radio node` | dedicated internal radio control plane on a Raspberry Pi 4 behind the internal frontdoor | active on `radio-node` (`192.168.1.16`, `100.64.23.77`) during the current UCG Ultra test segment; default gateway is `192.168.1.1`, `radio.hs27.internal` still proxies to the Pi, and SMB-backed media remains live | verify DNS and routing on the UCG test segment before broader rollout, then keep the Pi as the first controlled cutover client |
| `Proxmox Backup Server (VM 240)` | durable backup control plane for Proxmox jobs, retention and recurring restore drills | active as interim PBS-v1 on `192.168.2.25`; datastore `hs27-interim` is active on USB-backed storage, scheduled jobs are live, and first proof-backup plus restore drill are verified | keep the `64GB` USB attached, continue recurring restore drills, and later migrate to larger dedicated PBS storage |
| `Home Assistant OS (VM 210)` | smart-home control plane with Supervisor, Add-ons and later USB passthrough | active on stable in-guest address `10.1.0.24`; internal frontdoor `ha.hs27.internal` now live via `CT 100` | keep reverse-proxy trust and interim local backup coverage verified; add USB passthrough only once adapters are physically present |
| `Public Edge` | later public reverse-proxy layer for selected endpoints with TLS and monitoring | planned, not active | activate only after UCG-grade firewall control, final inventory/zones, proven backups, and documented domain/DNS/TLS/auth/monitoring/rollback |
| `Ollama` | local AI inference workload | wishlist only, not active | revisit only after RAM expansion, separate inference node or external AI host strategy |

## Current Best-Practice Actions

1. Freeze a canonical device register now and update it only from scan plus router-lease reconciliation.
2. Reserve or document fixed addresses for all infrastructure and business nodes on the Easy Box.
3. Keep unmanaged household and IoT devices explicitly separated in inventory even before VLAN-capable hardware exists.
4. Treat `unknown-review` devices as temporary exceptions and close them out before exposing any services over Tailscale.
5. Only promote devices into `trusted-clients` after owner and management posture are known.
6. Treat Wolfs `Arbeitssurface` as a split-access trusted client:
   - default mode is local independent work on WLAN
   - internal app and admin reachability is on-demand via Tailscale
   - no permanent full-tunnel and no blind `RouteAll`
7. Treat the UCG-Ultra as a dedicated later-phase network cutover, not as a side-task during current LXC/VM rollout work.
8. Keep router-only names that are not yet tied to a live IP explicit in the notes instead of guessing their mapping.
9. Introduce AdGuard Home first as an opt-in internal DNS service, not as immediate default DNS for the whole LAN.
10. Treat public exposure as its own hardening phase with edge separation, not as an extension of the current flat-LAN toolbox phase.
11. Treat shared frontend devices as kiosk-first endpoints, not as ad hoc desktop-server hybrids.

## 2026-04-05 Transition Note

- Core business services now live on UCG VLAN 101 (`10.1.0.0/24`).
- `wolfstudiopc` still sits on the EasyBox-connected `192.168.2.0/24`; the legacy subnet is kept only as an emergency alias on Proxmox.
- `wolf_surface` is now the dedicated review/control node; it should stay on the repo-based SSH path and not grow into a second ad hoc admin workstation.
- Direct StudioPC-to-legacy `192.168.2.x` access is no longer the working path during migration.
- The current working operator path is `Tailscale first` through `toolbox` on `100.82.26.53` and direct Proxmox management on `100.69.179.87`.
- OpenClaw (Hostinger) access is fully established via Tailscale IPs and secure rotation-proof SSH keys.
