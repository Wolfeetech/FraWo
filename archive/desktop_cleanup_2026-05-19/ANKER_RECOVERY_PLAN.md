# 🔴 ANKER PVE RECOVERY PLAN - Echtes Odoo retten

## Aktuelle Situation:

**Anker PVE ist OFFLINE** (physisch ausgeschaltet oder Netzwerkproblem)
- Letzter Kontakt: Vor ~1 Tag
- Tailscale Status: "offline, last seen 1d ago"
- Alle Verbindungsmethoden fehlgeschlagen

**Betroffene Services auf Anker:**
- ❌ Toolbox Container (kritisch!)
- ❌ Odoo ERP (Deine echten Daten!)
- ❌ Nextcloud
- ❌ Paperless
- ❌ Vault
- ❌ Portal

---

## 🎯 WAS DU JETZT TUN MUSST:

### OPTION 1: Vor-Ort-Zugang (EMPFOHLEN)

**Du MUSST nach Rothkreuz:**

1. **Zum Server gehen**
   - Standort: Rothkreuz
   - Server: Anker PVE (Proxmox Anker)

2. **Physische Checks:**
   ```
   ☐ Ist der Server eingeschaltet? (LEDs leuchten?)
   ☐ Sind Netzwerkkabel verbunden?
   ☐ Ist der Monitor an? (Fehlermeldungen?)
   ☐ Zeigt die LED am Netzwerkport Aktivität?
   ```

3. **Wenn Server AUS ist:**
   - Power-Button drücken
   - 2-3 Minuten warten
   - Von deinem PC testen: `python Desktop/WAKE_ANKER_PVE.py`

4. **Wenn Server AN ist aber kein Netzwerk:**
   - Netzwerkkabel neu einstecken
   - Switch/Router prüfen
   - Andere Geräte am Switch testen

5. **Wenn Server bootet:**
   - Warte bis Proxmox Login erscheint
   - Teste: `ping 10.1.0.92` (lokal) oder `ping 100.69.179.87` (Tailscale)
   - SSH: `ssh anker-pve`

6. **Services prüfen:**
   ```bash
   ssh anker-pve
   pct list                    # Container auflisten
   pct status <toolbox-id>     # Toolbox Status
   pct start <toolbox-id>      # Falls gestoppt
   ```

---

### OPTION 2: Jemand vor Ort schicken

Falls du nicht selbst hin kannst:

**Person vor Ort braucht:**
1. Zugang zum Server-Raum
2. Diese Anleitung
3. Telefon-Kontakt zu dir
4. Optional: Laptop mit diesem Tool

**Schritte für Person vor Ort:**
```
1. Server-LED-Status fotografieren und schicken
2. Wenn aus: Power-Button drücken
3. Warten bis LEDs blinken
4. Dir Bescheid geben
5. Du testest von deinem PC
```

---

### OPTION 3: Remote Management (Falls vorhanden)

**Check für IPMI/iLO/iDRAC:**
- Mögliche IP: `10.1.0.93` (häufige Konvention)
- Probiere: `https://10.1.0.93/`
- Falls Login erscheint: Remote Power On möglich!

**Test:**
```bash
curl -k https://10.1.0.93/
# oder
ping 10.1.0.93
```

---

## 🔧 NACH DEM ANKER PVE ONLINE IST:

### Automatische Wiederherstellung:

1. **Services prüfen:**
   ```bash
   python Desktop/frawo_ops_dashboard.py
   ```

2. **Falls Toolbox nicht startet:**
   ```bash
   ssh anker-pve
   pct list                    # Finde Toolbox VMID
   pct start <vmid>           # Starte Toolbox
   systemctl status pveproxy  # Proxmox selbst OK?
   ```

3. **Odoo Zugriff testen:**
   ```bash
   curl http://odoo.hs27.internal/
   # oder Browser: http://odoo.hs27.internal/
   ```

---

## 💾 BACKUP-STRATEGIE (Für nächstes Mal):

### Sofort nach Wiederherstellung:

1. **Backup von Odoo erstellen:**
   ```bash
   ssh anker-pve
   # Finde Odoo Container/VM
   vzdump <odoo-vmid> --storage hdd-backup
   ```

2. **Odoo Datenbank exportieren:**
   ```bash
   # In Odoo Web-Interface:
   # Settings → Database Manager → Backup
   # Oder via CLI im Odoo Container
   ```

3. **Backup an sicheren Ort kopieren:**
   ```bash
   scp anker-pve:/pfad/zum/backup/* ~/frawo-backups/
   ```

---

## 🚨 WENN ANKER NICHT WIEDER KOMMT:

### Plan B: Backup wiederherstellen

Falls Anker Hardware-Schaden hat:

1. **Backup-Dateien finden:**
   - PBS (Container 109 auf Stock PVE)
   - hdd-backup Storage
   - Externe Backups

2. **Toolbox/Odoo auf Stock PVE wiederherstellen:**
   ```bash
   ssh stock-pve
   pzrestore hdd-backup:vzdump-xxx.vma.zst <new-vmid>
   ```

3. **Netzwerk neu konfigurieren:**
   - IP-Adressen anpassen
   - hosts-Datei updaten

---

## 📞 KONTAKT-INFO FÜR ROTHKREUZ:

```
Standort: [HIER EINTRAGEN]
Ansprechpartner: [HIER EINTRAGEN]
Telefon: [HIER EINTRAGEN]
Server-Raum: [HIER EINTRAGEN]
```

---

## ⏱️ ZEITPLAN:

### Sofort (Jetzt):
- [ ] Kontakt mit Rothkreuz aufnehmen
- [ ] Termin für Vor-Ort-Check vereinbaren
- [ ] Oder Remote-Person organisieren

### Innerhalb 24h:
- [ ] Anker PVE physisch prüfen
- [ ] Server einschalten
- [ ] Konnektivität wiederherstellen

### Nach Wiederherstellung:
- [ ] Alle Services testen
- [ ] Backup erstellen
- [ ] Monitoring einrichten
- [ ] Dokumentation aktualisieren

---

## 🎯 ZUSAMMENFASSUNG:

**Das Problem:**
- Anker PVE ist physisch offline
- Kein Remote-Zugriff möglich
- Dein echtes Odoo läuft dort

**Die Lösung:**
- Jemand MUSS vor Ort zum Server
- Server einschalten / Netzwerk prüfen
- Danach läuft alles automatisch wieder

**Keine andere Option:**
- Remote Wake-up nicht möglich (kein WOL)
- Backups unsicher (nicht gefunden)
- Physischer Zugang ERFORDERLICH

---

## 📝 NEXT STEPS:

1. **JETZT:** Kontakt zu Rothkreuz aufnehmen
2. **HEUTE:** Termin für Server-Check
3. **MORGEN:** Server prüfen und einschalten
4. **DANN:** Odoo läuft wieder!

---

**Du kannst NICHTS remote tun. Der Server ist AUS.**
**Lösung: Jemand muss den Power-Button drücken.**

---

Soll ich dir helfen:
- [ ] Checkliste für Person vor Ort erstellen?
- [ ] Backup-Recovery-Plan erstellen (falls Hardware kaputt)?
- [ ] Monitoring einrichten (damit das nicht wieder passiert)?

---

*Stand: 2026-05-07 07:45*
*Anker PVE offline seit: ~24 Stunden*
