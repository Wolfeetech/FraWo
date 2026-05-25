import csv

csv_file = r"C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\vaultwarden_import.csv"

# Bitwarden CSV Header
# folder,favorite,type,name,notes,fields,reprompt,login_uri,login_username,login_password,login_totp
header = ["folder", "favorite", "type", "name", "notes", "fields", "reprompt", "login_uri", "login_username", "login_password", "login_totp"]

rows = [
    # Infrastruktur
    ["Infrastruktur", 1, "login", "Proxmox (pve-anker)", "Haupt-Server Webinterface", "", 0, "https://10.1.0.92:8006", "root", "", ""],
    ["Infrastruktur", 1, "login", "Cloudflare", "DNS, Tunnels & Proxy", "", 0, "https://dash.cloudflare.com", "office@frawo-tech.de", "", ""],
    
    # Odoo
    ["Odoo", 1, "login", "Odoo (Wolf)", "Hauptaccount", "", 0, "https://www.frawo-tech.de", "wolf@frawo-tech.de", "", ""],
    ["Odoo", 0, "login", "Odoo (Franz)", "Hauptaccount Franz", "", 0, "https://www.frawo-tech.de", "franz@frawo-tech.de", "[BITTE_EINTRAGEN]", ""],
    ["Odoo", 0, "login", "Odoo (Database Admin)", "Für Datenbank-Backups", "", 0, "https://www.frawo-tech.de/web/database/manager", "admin", "", ""],
    
    # Web-Dienste
    ["Web-Dienste", 0, "login", "Vaultwarden Admin", "Konfiguration des Tresors", "", 0, "https://vault.frawo-tech.de/admin", "", "", ""],
    ["Web-Dienste", 0, "login", "Nextcloud", "Cloud Speicher", "", 0, "https://cloud.frawo-tech.de", "admin", "", ""],
    ["Web-Dienste", 0, "login", "Home Assistant", "Smart Home", "", 0, "https://home.frawo-tech.de", "admin", "", ""],
    ["Web-Dienste", 0, "login", "AzuraCast (Radio)", "Webradio Backend", "", 0, "https://funk.frawo-tech.de", "radio@frawo-tech.de", "", ""],
]

proxmox_vms = [
    ("100", "toolbox", "LXC"),
    ("101", "adguard-slave", "LXC"),
    ("110", "storage-node", "LXC"),
    ("120", "vaultwarden", "LXC"),
    ("130", "radio-node", "LXC"),
    ("200", "nextcloud (VM 200)", "VM"),
    ("210", "haos", "VM"),
    ("220", "odoo", "VM"),
    ("230", "paperless (VM 230)", "VM"),
    ("240", "PBS-FraWo", "VM"),
    ("300", "nextcloud (VM 300)", "VM"),
    ("330", "paperless (VM 330)", "VM"),
]

for vmid, name, vm_type in proxmox_vms:
    rows.append([
        "Proxmox VMs & Container",
        0,
        "login",
        f"[{vmid}] {name}",
        f"{vm_type} auf pve-anker",
        "",
        0,
        "",
        "root",
        "",
        ""
    ])

with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print(f"CSV generated at {csv_file}")
