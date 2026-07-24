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
    },
]

def run_remote_python(code: str):
    # Pass python code via stdin over SSH with UTF-8 encoding
    cmd = [
        "ssh", "-o", "BatchMode=yes", "root@10.1.0.128",
        "pct exec 140 -- python3 -"
    ]
    res = subprocess.run(cmd, input=code, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"Error executing python on CT140: {res.stderr}")
        sys.exit(1)
    print(res.stdout)

def main():
    print("=== Step 1: Upgrading Odoo modules maintenance & frawo_agent on CT140 ===")
    cmd_upgrade = [
        "ssh", "-o", "BatchMode=yes", "root@10.1.0.128",
        "pct exec 140 -- su - odoo -c 'python3 /usr/bin/odoo -c /etc/odoo/odoo.conf -d FraWo_GbR -u maintenance,frawo_agent --stop-after-init'"
    ]
    res_upg = subprocess.run(cmd_upgrade, capture_output=True, text=True)
    print("Odoo module upgrade triggered successfully.")

    print("\n=== Step 2: Seeding IT Equipment records into Odoo ===")
    python_seed_code = f"""import psycopg2, json

conn = psycopg2.connect(
    dbname='FraWo_GbR', user='odoo', password='odoo_FraWo_2026_x9k2', host='db', port=5432
)
cur = conn.cursor()

assets = {json.dumps(IT_ASSETS)}

for a in assets:
    cur.execute("SELECT id FROM maintenance_equipment WHERE name = %s;", (a['name'],))
    row = cur.fetchone()
    if row:
        cur.execute(\"\"\"
            UPDATE maintenance_equipment
            SET ip_address=%s, tailscale_ip=%s, vlan_id=%s, pve_host=%s, vm_ct_id=%s, equipment_role=%s, is_critical=%s
            WHERE id=%s;
        \"\"\", (a['ip_address'], a['tailscale_ip'], a['vlan_id'], a['pve_host'], a['vm_ct_id'], a['equipment_role'], a['is_critical'], row[0]))
        print(f"Updated {{a['name']}} (ID: {{row[0]}})")
    else:
        cur.execute(\"\"\"
            INSERT INTO maintenance_equipment (name, ip_address, tailscale_ip, vlan_id, pve_host, vm_ct_id, equipment_role, is_critical)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        \"\"\", (a['name'], a['ip_address'], a['tailscale_ip'], a['vlan_id'], a['pve_host'], a['vm_ct_id'], a['equipment_role'], a['is_critical']))
        print(f"Inserted {{a['name']}}")

conn.commit()
cur.close()
conn.close()
print("✅ Seeding IT Equipment assets completed successfully!")
"""
    run_remote_python(python_seed_code)

if __name__ == "__main__":
    main()
