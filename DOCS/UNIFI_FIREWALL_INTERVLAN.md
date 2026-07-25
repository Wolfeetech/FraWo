# UniFi Cloud Gateway Ultra — Inter-VLAN Firewall Matrix

Dokumentation der Firewall-Regeln gemäß **Task #691**.

---

## 🛡️ Inter-VLAN Firewall Rules (UniFi Cloud Gateway Ultra 10.1.0.1)

```
┌───────────────┬──────────────────────┬────────────────────────┬─────────────┐
│ Zone / VLAN   │ Ziel-VLAN            │ Erlaubte Protokolle    │ Regel-Typ   │
├───────────────┼──────────────────────┼────────────────────────┼─────────────┤
│ Core (VLAN101)│ Alle (IoT, Guest)    │ ALLE (Management)      │ ALLOW       │
│ IoT (VLAN104) │ Core (VLAN101)       │ Nur HA (10.1.0.40:8123)│ RESTRICTED  │
│ Guest(VLAN105)│ Core (VLAN101)       │ Nur DNS (10.1.0.101)   │ ISOLATED    │
└───────────────┴──────────────────────┴────────────────────────┴─────────────┘
```

## 🔐 Isolation & Protection
- **Drop Established/Related Exceptions:** Guest VLAN 105 hat keinen Zugriff auf interne Server-Subnetze außer DNS & AzuraCast Live Stream Port.
