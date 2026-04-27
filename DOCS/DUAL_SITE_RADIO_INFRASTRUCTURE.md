# Dual-Site Radio Infrastructure

> **Status**: Implementation Active (2026-04-26)
> **Domain Migration**: `radio.yourparty.tech` → `funk.frawo-tech.de`

## Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                    ANKER/ROTHKREUZ (Primary)                 │
│                                                               │
│  VLAN 103 (Anker-DMZ-Radio) - 10.3.0.0/24                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Radio Node Anker (Raspberry Pi 4)                     │  │
│  │ IP: 10.3.0.10                                         │  │
│  │ Tailscale: 100.64.23.77                              │  │
│  │ Hostname: radio-anker.hs27.internal                  │  │
│  │ Station: frawo-funk                                   │  │
│  │ Platform: AzuraCast (Docker)                         │  │
│  │ Public: funk.frawo-tech.de                           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Storage: SMB Mount from CT 110 (10.1.0.30)                 │
│  Media Library: //10.1.0.30/Media/yourparty_Libary          │
└───────────────────┬───────────────────────────────────────────┘
                    │
          WireGuard Site-to-Site VPN
         (VLAN 110/111 Routing)
                    │
┌───────────────────┴───────────────────────────────────────────┐
│                  STOCKENWEILER (Remote)                       │
│                                                               │
│  VLAN 111 (Stock-Server) - 10.11.0.0/24 (via VPN)           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ AzuraCast VM 210                                      │  │
│  │ Target IP: 10.11.0.10 (VPN-routed)                   │  │
│  │ Local IP: 192.168.178.210 (fallback)                 │  │
│  │ Hostname: radio-stock.hs27.internal                  │  │
│  │ Station: stock-funk                                   │  │
│  │ Platform: AzuraCast (VM)                             │  │
│  │ Legacy: radio.yourparty.tech                         │  │
│  │ Migration: → funk.frawo-tech.de                      │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Media Library: /mnt/music_hdd/yourparty_Libary (283GB)     │
│  Status: Storage 100% full, Memory pressure critical         │
└───────────────────────────────────────────────────────────────┘
```

## Stations

### Station 1: Anker-Funk (Primary)
- **Name**: FraWo - Funk
- **Shortcode**: `frawo-funk`
- **Internal URL**: `http://radio-anker.hs27.internal`
- **Public URL**: `https://funk.frawo-tech.de`
- **Platform**: AzuraCast on Raspberry Pi 4 (2GB RAM)
- **Network**: VLAN 103 (Anker-DMZ-Radio)
- **IP**: `10.3.0.10`
- **Tailscale**: `100.64.23.77`
- **Media Source**: SMB mount from Storage Node (CT 110)
- **Library Size**: ~70GB (curated)
- **Status**: ✅ **LIVE** with AutoDJ

### Station 2: Radio4yourparty (LIVE - Stockenweiler)
- **Name**: Radio4yourparty
- **Shortcode**: `radio.yourparty`
- **Internal URL**: `http://radio-stock.hs27.internal`
- **Public Player**: `http://radio-stock.hs27.internal/public/radio.yourparty`
- **Legacy Domain**: `radio.yourparty.tech` (active)
- **Migration Target**: `https://funk.frawo-tech.de`
- **Platform**: AzuraCast on VM 210
- **Backend**: Liquidsoap
- **Frontend**: Icecast
- **Network**: VLAN 111 (Stock-Server) via Tailscale VPN
- **Target IP**: `10.11.0.10` (VPN-routed)
- **Local IP**: `192.168.178.210` (direct access)
- **Streaming**: 320kbps MP3 (primary) + 192kbps MP3 (light)
- **HLS**: Enabled (`/hls/radio.yourparty/live.m3u8`)
- **Media Library**: `/mnt/music_hdd/yourparty_Libary` (283GB)
- **Active Playlists**: "Wolfarites", "Wolf Lounge"
- **Now Playing**: ✅ Live (Farley 'Jackmaster' Funk - Love Can't Turn Around)
- **Listeners**: 0 (available for streaming)
- **Status**: 🟢 **LIVE & STREAMING** (verified 2026-04-27)

## Network Configuration

### VLAN 103: Anker-DMZ-Radio (10.3.0.0/24)
**Purpose**: Isolated radio services network at Anker site

| Host | IP | Purpose |
|------|-----|---------|
| Gateway | `10.3.0.1` | UCG-Ultra routing |
| Radio Node Anker | `10.3.0.10` | Raspberry Pi 4 AzuraCast |

**Firewall Rules (Outbound)**:
- VLAN 103 → VLAN 101: Ports 445 (SMB), 80, 443 (Storage + Toolbox)
- VLAN 103 → Internet: Ports 80, 443, 123 (NTP), 53 (DNS)
- VLAN 103 → VLAN 111: Ports 8000, 8443 (Cross-Site Relay)

**Firewall Rules (Inbound)**:
- VLAN 101 (10.1.0.20 toolbox) → VLAN 103: Ports 80, 443 (Reverse Proxy)
- VLAN 100 → VLAN 103: Ports 80, 443 (Client Access)

### VLAN 111: Stock-Server (10.11.0.0/24)
**Purpose**: Stockenweiler server infrastructure (VPN-routed)

| Host | IP | Purpose |
|------|-----|---------|
| Gateway | `10.11.0.1` | UCG-Ultra VPN routing |
| AzuraCast VM 210 | `10.11.0.10` | Legacy radio VM |

**VPN Access**:
- WireGuard Site-to-Site: UCG-Ultra ↔ FritzBox 5690 Pro
- Routed Subnets: 10.11.0.0/24, 10.10.0.0/24
- Local Fallback: `192.168.178.210`

## DNS Configuration

### Internal DNS (hs27.internal)
**AdGuard Rewrites** (on CT 100 toolbox):
```yaml
- domain: radio-anker.hs27.internal
  answer: 10.3.0.10

- domain: radio-stock.hs27.internal
  answer: 10.11.0.10

# Legacy compatibility
- domain: radio.hs27.internal
  answer: 10.3.0.10  # Points to Anker by default
```

### Public DNS
**Target Domain**: `funk.frawo-tech.de`

**Migration Path**:
```
Legacy: radio.yourparty.tech
    ↓
Target: funk.frawo-tech.de (unified domain for both stations)
```

**Cloudflare Routing**:
- `funk.frawo-tech.de` → Cloudflare Tunnel
- Origin: VM 220 Odoo (website) or Radio Node (direct stream)
- Player Embed: `www.frawo-tech.de/radio`
- Standalone: `funk.frawo-tech.de`

## Control Surface Integration

### Actions (Control Surface V2)

**Anker Station**:
- **Player**: `radio_listen_anker` → `http://radio-anker.hs27.internal/public/frawo-funk`
- **Control**: `radio_control_anker` → `http://radio-anker.hs27.internal/login`
- **Status**: ✅ Ready
- **Code**: RA, RCA

**Stockenweiler Station**:
- **Player**: `radio_listen_stock` → `http://radio-stock.hs27.internal/public/stock-funk`
- **Control**: `radio_control_stock` → `http://radio-stock.hs27.internal/login`
- **Status**: ⏳ Backlog (pending integration)
- **Code**: RS, RCS

**Radio Group**:
- **Name**: Radio
- **Eyebrow**: "Audio - Dual Site"
- **Description**: "Player und Steuerung für beide Radio-Stationen (Anker + Stockenweiler)."
- **Priority**: 30

## Implementation Phases

### Phase 0: Pre-Flight ⏳ IN PROGRESS
- [x] Inventory updated (both stations)
- [x] UCG Network Architecture documented
- [x] Firewall rules defined
- [x] Control Surface V2 extended
- [ ] **Tailscale subnet route approval** (192.168.178.0/24) - **MANUAL ACTION REQUIRED**
- [ ] Stockenweiler VM 210 payload backup
- [ ] VLAN 103 gateway verified (✅ 10.3.0.1 responds)

### Phase 1: Anker Migration to VLAN 103
**Objective**: Move Raspberry Pi from current network → VLAN 103

1. **Network Preparation**:
   - UCG-Ultra VLAN 103 configuration ✅
   - DHCP reservation for `10.3.0.10` (MAC of Pi)
   - Firewall rules deployment

2. **DNS Configuration**:
   - Deploy toolbox DNS updates
   - Verify `radio-anker.hs27.internal` → `10.3.0.10`

3. **Network Migration**:
   - SSH via Tailscale: `ssh wolf@100.64.23.77`
   - Configure static IP `10.3.0.10/24`
   - Gateway: `10.3.0.1`
   - DNS: `10.1.0.20`
   - Restart networking

4. **Verification**:
   - Ping gateway, toolbox, storage-node
   - SMB mount check
   - AzuraCast web UI accessible
   - Stream functional
   - Tailscale frontdoor working

### Phase 2: Stockenweiler Integration
**Objective**: Integrate VM 210 into UCG network via VPN

**Blockers**:
- ⚠️ Tailscale route not approved (192.168.178.0/24)
- ⚠️ Storage 100% full (no backup space)
- ⚠️ Memory pressure critical (70.6% swap)

**Prerequisites**:
1. Approve Tailscale subnet route
2. Backup VM 210 payload to Rothkreuz
3. Free storage space OR provision additional capacity
4. WireGuard S2S VPN verification

**Steps**:
1. Tailscale access to `192.168.178.25` (Proxmox)
2. Payload capture (AzuraCast config, DB, WordPress)
3. VPN routing configuration
4. DNS deployment for `radio-stock.hs27.internal`
5. Verification via VPN

### Phase 3: Public Edge & Domain Migration
**Objective**: Migrate `radio.yourparty.tech` → `funk.frawo-tech.de`

1. **Domain Setup**:
   - DNS: `funk.frawo-tech.de` CNAME or A record
   - Cloudflare: SSL certificate (automatic)
   - Cloudflare Tunnel routing decision

2. **Stream Configuration**:
   - Define public mount point
   - Configure bitrate/quality (128kbps MP3 recommended)
   - Enable crossfading (3-5 seconds)
   - Test stream endpoint

3. **Website Integration**:
   - Option A: Embed on `www.frawo-tech.de/radio`
   - Option B: Standalone `funk.frawo-tech.de`
   - Player frontend deployment

4. **Migration Cutover**:
   - Parallel operation: `radio.yourparty.tech` + `funk.frawo-tech.de`
   - DNS TTL reduction (pre-migration)
   - Cutover to new domain
   - Redirect old domain (HTTP 301)

### Phase 4: Operational Readiness
**Objective**: Production-grade monitoring and automation

1. **Monitoring**:
   - Uptime Kuma integration (both stations)
   - Stream health checks
   - Dead-air alerting
   - Listener metrics

2. **Backup**:
   - AzuraCast config backup to PBS
   - Database backup automation
   - Media library (already on Storage Node)

3. **Documentation**:
   - Operations runbook
   - Emergency procedures
   - Media upload workflow
   - Restart procedures

## Current Status

### ✅ Completed
- Ansible inventory updated for dual-site
- UCG network architecture documented
- Firewall rules defined
- Control Surface V2 extended
- Git commit & push completed

### ⏳ In Progress
- Phase 0 pre-flight checks
- Tailscale route approval (waiting)

### ⚠️ Blockers
1. **Tailscale Route Approval** (Manual): `192.168.178.0/24` for `stockenweiler-pve`
2. **Radio Node Offline**: `100.64.23.77` not responding (Tailscale issue?)
3. **Stockenweiler Capacity**: Storage 100% full, swap pressure critical
4. **WireGuard VPN**: S2S configuration between UCG ↔ FritzBox pending

### 📋 Next Actions
1. **YOU**: Approve Tailscale route in admin console
2. **YOU**: Verify Radio Node Tailscale connectivity
3. **AUTOMATED**: Deploy DNS configuration for dual-station
4. **AUTOMATED**: Firewall rules deployment to UCG
5. **MANUAL**: Stockenweiler payload backup before integration

## Resources

### Documentation
- [UCG Network Architecture](../infrastructure/UCG_NETWORK_ARCHITECTURE.md)
- [Control Surface Actions V2](../manifests/control_surface/actions_v2.json)
- [Ansible Inventory](../ansible/inventory/hosts.yml)
- [Radio Operations Standard](Task_Archive/RADIO_OPERATIONS_STANDARD.md)

### Scripts
- `scripts/radio_operations_check.sh` - Health check
- `scripts/ensure_stockenweiler_toolbox_access.ps1` - VPN access

### Ansible Playbooks
- `ansible/playbooks/deploy_raspberry_pi_azuracast.yml`
- `ansible/playbooks/curate_raspberry_pi_radio.yml`
- `ansible/playbooks/integrate_raspberry_pi_radio_network_music.yml`

## Risk Assessment

### High Risk
- **VPN Failure**: Stock station isolated
  - Mitigation: Local fallback `192.168.178.210`, Tailscale secondary
- **VLAN Misconfiguration**: Media access broken
  - Mitigation: Snapshot before changes, Tailscale management, rollback tested

### Medium Risk
- **Resource Exhaustion**: Pi 4 overload
  - Mitigation: Low-resource profile, monitoring, single station
- **DNS Failure**: Resolution problems
  - Mitigation: Multiple DNS servers, direct IP access, Tailscale DNS

### Low Risk
- **Media Corruption**: Library issues
  - Mitigation: Source on Storage Node (PBS backup), rsync atomic sync

## Success Criteria

### Technical KPIs
- Station uptime: > 99.5%
- API latency: < 500ms
- VPN latency: < 50ms
- Stream quality: No dropouts

### Operational KPIs
- Deployment time: < 2 hours per station
- MTTR: < 1 hour
- Automation coverage: > 90%

### User Experience
- Control Surface shows both stations
- Station switching seamless
- Streaming works on all devices
- Admin access for both stations

---

**Generated**: 2026-04-26
**Last Updated**: 2026-04-26
**Status**: Implementation Active
**Next Review**: After Phase 1 completion
