import subprocess
import json
import sys

# Script to seed IT Equipment Inventory directly in Odoo database (CT140) via SSH on stockenweiler-pve

IT_ASSETS = [
    {
        "name": "stockenweiler-pve (HP ProDesk)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.128",
        "tailscale_ip": "100.91.20.116",
        "vlan_id": "101",
        "pve_host": "stockenweiler-pve",
        "vm_ct_id": "Host",
        "equipment_role": "Primary Proxmox Hypervisor (Rothkreuz)",
        "is_critical": True,
        "model": "HP ProDesk 600 G4 Mini (Intel i5, 16GB RAM)",
        "location": "Rothkreuz - Server Rack 1",
        "serial_no": "PRODESK-600G4-RK1",
        "note": "Primary Proxmox VE 8.x Hypervisor Node. Hosts CT140 (Odoo), CT120 (Fileserver), VM210 (AzuraCast), CT108 (Vaultwarden), CT150 (Monitoring Stack). Network: 10.1.0.128 / Tailscale 100.91.20.116."
    },
    {
        "name": "proxmox-anker (Lenovo ThinkCentre)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.92",
        "tailscale_ip": "100.69.179.87",
        "vlan_id": "101",
        "pve_host": "proxmox-anker",
        "vm_ct_id": "Host",
        "equipment_role": "Secondary Proxmox Hypervisor (Rothkreuz)",
        "is_critical": True,
        "model": "Lenovo ThinkCentre M720q Tiny (Intel i5, 16GB RAM)",
        "location": "Rothkreuz - Server Rack 2",
        "serial_no": "THINKCENTRE-M720Q-RK2",
        "note": "Secondary Proxmox VE 8.x Hypervisor Node. Hosts VM240 (PBS Backup Server), VM210 (HAOS Master), CT150 (OpenClaw @Frawo_bot), VM300 (Nextcloud). Network: 10.1.0.92 / Tailscale 100.69.179.87."
    },
    {
        "name": "wolfstudiopc (StudioPC Workstation)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.211",
        "tailscale_ip": "100.98.31.60",
        "vlan_id": "101",
        "pve_host": "wolfstudiopc",
        "vm_ct_id": "Workstation",
        "equipment_role": "AV/IT Master Operator Workstation",
        "is_critical": False,
        "model": "Custom Workstation (Windows 11 Pro, Intel i7, 32GB RAM)",
        "location": "Rothkreuz - Studio PC Desk",
        "serial_no": "STUDIOPC-WIN11-WOLF",
        "note": "AV/IT Master Operator Workstation. Persistent SMB Mounts: M: (\\\\10.1.0.94\\music), R: (\\\\10.1.0.94\\radio). Runs OpenClaw Node background service. Network: 10.1.0.211 / Tailscale 100.98.31.60."
    },
    {
        "name": "CT140 frawotech-web (Odoo 19)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.112",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "stockenweiler-pve",
        "vm_ct_id": "CT140",
        "equipment_role": "Odoo 19 ERP + Cloudflare Tunnel (frawo.tech)",
        "is_critical": True,
        "model": "Proxmox LXC Container (Debian 12, Docker)",
        "location": "stockenweiler-pve (Host)",
        "serial_no": "CT140-ODOO19-WEB",
        "note": "Odoo 19 ERP Master System (FraWo_GbR DB) + Cloudflare Tunnel 'FraWo-RK' (frawo.tech / frawotech.de). PostgreSQL 16 on frawotech-db-1 container. Network: 10.1.0.112."
    },
    {
        "name": "CT120 fileserver (Samba Master)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.94",
        "tailscale_ip": "100.64.130.24",
        "vlan_id": "101",
        "pve_host": "stockenweiler-pve",
        "vm_ct_id": "CT120",
        "equipment_role": "Samba Master Music & Radio Shares (M: / R:)",
        "is_critical": True,
        "model": "Proxmox LXC Container (Debian 12, Samba)",
        "location": "stockenweiler-pve (Host)",
        "serial_no": "CT120-SAMBA-FILESERVER",
        "note": "Samba Master Storage Server. Shared drives: //10.1.0.94/music (M:) and //10.1.0.94/radio (R:). Configured deadtime=15s for SMB resilience. Network: 10.1.0.94 / Tailscale 100.64.130.24."
    },
    {
        "name": "VM210 azuracast-vm (FraWo Funk Master)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.38",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "stockenweiler-pve",
        "vm_ct_id": "VM210",
        "equipment_role": "Master-AzuraCast Radiostation (Icecast/Liquidsoap)",
        "is_critical": True,
        "model": "Proxmox KVM VM (Ubuntu 22.04 LTS, Docker)",
        "location": "stockenweiler-pve (Host)",
        "serial_no": "VM210-AZURACAST-MASTER",
        "note": "Master AzuraCast Web Radio Station ('FraWo Funk'). Icecast 2 + Liquidsoap auto-dj. Streams live audio on https://10.1.0.38/listen/frawo_funk/radio.mp3. Network: 10.1.0.38."
    },
    {
        "name": "CT108 vaultwarden (Passwort-Manager)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.95",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "stockenweiler-pve",
        "vm_ct_id": "CT108",
        "equipment_role": "Vaultwarden Password Manager (Bitwarden API)",
        "is_critical": True,
        "model": "Proxmox LXC Container (Debian 12, Docker)",
        "location": "stockenweiler-pve (Host)",
        "serial_no": "CT108-VAULTWARDEN-PWD",
        "note": "Vaultwarden Enterprise Password Manager (Bitwarden API). Stores all internal credentials, API keys, SSH keys, and system secrets. Network: 10.1.0.95."
    },
    {
        "name": "CT150 openclaw (@Frawo_bot)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.31",
        "tailscale_ip": "100.72.154.15",
        "vlan_id": "101",
        "pve_host": "proxmox-anker",
        "vm_ct_id": "CT150",
        "equipment_role": "OpenClaw AI Gateway & Telegram Agent Bridge",
        "is_critical": True,
        "model": "Proxmox LXC Container (Debian 12, Node.js)",
        "location": "proxmox-anker (Host)",
        "serial_no": "CT150-OPENCLAW-BOT",
        "note": "OpenClaw AI Gateway & Telegram Agent Bridge (@Frawo_bot). Polls Odoo tasks every 5 minutes and executes autonomous DevOps instructions. Network: 10.1.0.31 / Tailscale 100.72.154.15."
    },
    {
        "name": "CT150 monitoring-stack (Grafana/Prometheus)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.115",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "stockenweiler-pve",
        "vm_ct_id": "CT150",
        "equipment_role": "Prometheus, Grafana, Alertmanager & Dead-Man's-Switch",
        "is_critical": True,
        "model": "Proxmox LXC Container (Debian 12, Prometheus/Grafana)",
        "location": "stockenweiler-pve (Host)",
        "serial_no": "CT150-MONITORING-STACK",
        "note": "Central Monitoring Stack. Runs Prometheus, Grafana, Alertmanager (Telegram Alerts), and External Dead-Man's-Switch (healthchecks.io). Network: 10.1.0.115."
    },
    {
        "name": "VM210 haos (Home Assistant Haupt)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.40",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "proxmox-anker",
        "vm_ct_id": "VM210",
        "equipment_role": "Home Assistant Master Smart Home Controller",
        "is_critical": True,
        "model": "Proxmox KVM VM (Home Assistant OS)",
        "location": "proxmox-anker (Host)",
        "serial_no": "VM210-HAOS-MASTER",
        "note": "Master Home Assistant Smart Home Controller. Manages Zigbee, Shelly, Matter/Thread, and IoT devices across Rothkreuz & Stockenweiler. Network: 10.1.0.40."
    },
    {
        "name": "VM240 PBS-FraWo (Backup Server)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.70",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "proxmox-anker",
        "vm_ct_id": "VM240",
        "equipment_role": "Proxmox Backup Server (Daily 04:00 Backups)",
        "is_critical": True,
        "model": "Proxmox KVM VM (Proxmox Backup Server 3.x)",
        "location": "proxmox-anker (Host)",
        "serial_no": "VM240-PBS-BACKUP",
        "note": "Proxmox Backup Server. Performs automated daily deduplicated & encrypted backups of all LXC/VM guests at 04:00. Network: 10.1.0.70."
    },
    {
        "name": "CT110 n8n (Workflows & Uptime)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.100",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "stockenweiler-pve",
        "vm_ct_id": "CT110",
        "equipment_role": "n8n Workflow Automation & Uptime Kuma",
        "is_critical": False,
        "model": "Proxmox LXC Container (Debian 12, Docker)",
        "location": "stockenweiler-pve (Host)",
        "serial_no": "CT110-N8N-WORKFLOWS",
        "note": "n8n Workflow Automation & Uptime Kuma monitoring service. Executes scheduled webhooks, notifications, and status pages. Network: 10.1.0.100."
    },
    {
        "name": "CT101 adguard (Primary DNS)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.52",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "stockenweiler-pve",
        "vm_ct_id": "CT101",
        "equipment_role": "Primary DNS & AdGuard Home Filter",
        "is_critical": True,
        "model": "Proxmox LXC Container (Debian 12, AdGuard Home)",
        "location": "stockenweiler-pve (Host)",
        "serial_no": "CT101-ADGUARD-DNS1",
        "note": "Primary Network DNS & AdGuard Home Filter. Serves internal domain resolutions (*.frawo.tech) and malware filtering. Network: 10.1.0.52."
    },
    {
        "name": "CT103 npm (Nginx Proxy Manager)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.149",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "stockenweiler-pve",
        "vm_ct_id": "CT103",
        "equipment_role": "Internal Nginx Reverse Proxy",
        "is_critical": True,
        "model": "Proxmox LXC Container (Debian 12, Docker)",
        "location": "stockenweiler-pve (Host)",
        "serial_no": "CT103-NPM-PROXY",
        "note": "Internal Nginx Reverse Proxy Manager. Manages SSL certificates (Let's Encrypt) and internal HTTPS routing. Network: 10.1.0.149."
    },
    {
        "name": "VM300 nextcloud (Cloud Storage)",
        "equipment_assign_to": "other",
        "ip_address": "10.1.0.111",
        "tailscale_ip": "",
        "vlan_id": "101",
        "pve_host": "proxmox-anker",
        "vm_ct_id": "VM300",
        "equipment_role": "Nextcloud Enterprise Cloud (cloud.frawo.tech)",
        "is_critical": False,
        "model": "Proxmox KVM VM (Ubuntu 22.04 LTS, Nextcloud Hub)",
        "location": "proxmox-anker (Host)",
        "serial_no": "VM300-NEXTCLOUD-HUB",
        "note": "FraWo Enterprise Nextcloud Cloud Storage (cloud.frawo.tech). Document management, team sync, and file sharing. Network: 10.1.0.111."
    },
]

def run_sql_script(sql: str):
    cmd = [
        "ssh", "-o", "BatchMode=yes", "root@10.1.0.128",
        "pct exec 140 -- docker exec -i frawotech-db-1 psql -U odoo -d FraWo_GbR"
    ]
    res = subprocess.run(cmd, input=sql, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"SQL Error: {res.stderr}")
        sys.exit(1)
    print(res.stdout)

def main():
    print("=== Step 1: Configuring German (de_DE) as Default Language in Odoo ===")
    sql_lang = """
-- Activate German language
UPDATE res_lang SET active = true WHERE code = 'de_DE';

-- Set German as default language for all partners & users
UPDATE res_partner SET lang = 'de_DE' WHERE lang IS NULL OR lang = 'en_US';
UPDATE res_users SET lang = 'de_DE' WHERE lang IS NULL OR lang = 'en_US';

-- Set system default for new partners/users in ir_default
DELETE FROM ir_default WHERE field_id IN (SELECT id FROM ir_model_fields WHERE name = 'lang');
INSERT INTO ir_default (field_id, value, json_value)
SELECT id, '"de_DE"', '"de_DE"' FROM ir_model_fields WHERE name = 'lang' AND model = 'res.partner';
"""
    run_sql_script(sql_lang)
    print("[OK] German (de_DE) set as default language in Odoo!")

    print("\n=== Step 2: Seeding & Enriching IT Equipment records in Odoo ===")
    sql_assets = []
    for a in IT_ASSETS:
        name_json = json.dumps({"de_DE": a["name"], "en_US": a["name"]})
        sql_assets.append(f"""
UPDATE maintenance_equipment
SET 
    model = '{a["model"].replace("'", "''")}',
    location = '{a["location"].replace("'", "''")}',
    serial_no = '{a["serial_no"].replace("'", "''")}',
    note = '{a["note"].replace("'", "''")}',
    ip_address = '{a["ip_address"]}',
    tailscale_ip = '{a["tailscale_ip"]}',
    vlan_id = '{a["vlan_id"]}',
    pve_host = '{a["pve_host"]}',
    vm_ct_id = '{a["vm_ct_id"]}',
    equipment_role = '{a["equipment_role"].replace("'", "''")}',
    is_critical = {str(a["is_critical"]).upper()},
    write_date = NOW()
WHERE name->>'de_DE' = '{a["name"].replace("'", "''")}';
""")
    
    run_sql_script("\n".join(sql_assets))
    print("[OK] All 15 IT Equipment assets enriched with detailed technical specifications in Odoo!")

if __name__ == "__main__":
    main()
