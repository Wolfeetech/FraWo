# Lotti VLAN Isolation & Security Protocol

Dokumentation der Netzwerktrennung gemäß **Task #692**.

---

## 🔒 1. VLAN-Isolation
- **VLAN 105 (Gast / Lotti Netz):** Auf UniFi Cloud Gateway Ultra isoliert.
- Kein Zugriff auf Server-Subnetz `10.1.0.0/24` (Odoo, Fileserver, Vaultwarden).
- Ausnahmen: Ausschließlich DNS (10.1.0.101) & FraWo Funk Live-Stream.
