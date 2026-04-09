# Legacy Network Knowledge Transfer (Radio Project -> Homeserver 2027)

## 🎯 Network Signatures & Conflict History
These devices were identified as causing massive IP conflicts in the 192.168.178.x subnet during the 2025 troubleshooting sessions.

| MAC Address | Vendor | Known Conflict IPs | Role |
| :--- | :--- | :--- | :--- |
| `34-CD-B0-7F-72-D0` | Espressif (IoT) | `.50`, `.202` | Rogue Client / IoT |
| `34-98-7A-A7-36-B8` | Espressif (IoT) | `.203` | Rogue Client / IoT |

## 📐 Recommended IP Architecture (The "Professional" Setup)
Maintain this segmentation to prevent interference between the Proxmox environment and unpredictable IoT hardware.

| Zone | IP Range | Assignment |
| :--- | :--- | :--- |
| **Infrastructure** | `.1` - `.19` | Router, Switches, Mesh Masters |
| **Server/Core** | `.20` - `.49` | Proxmox Host, Critical VMs (Odoo, DB), NAS |
| **Clients** | `.50` - `.199` | DHCP Range (Laptops, Mobile, Desktop) |
| **IoT/VLAN** | `.200` - `.254` | Smart Home Devices (Ideally move to Guest WLAN) |

## ⚠️ Legacy Issues
- **Fritz!Box Mesh Stability**: Connectivity between the Mesh Master and Repeater FritzBox was unstable, resolved primarily through TR-064 reboots.
- **Service Mapping**: AzuraCast was formerly on `.210`, but moved IPs due to DHCP conflicts.
