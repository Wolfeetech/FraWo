# 🦞 OPENCLAW: HOSTINGER DEPLOYMENT PACKAGE

Dieses Dokument ist das finale Paket für den OpenClaw-Agenten auf Hostinger. Es enthält alle Informationen, um den Agenten autonom auf dem FraWo-Estate arbeiten zu lassen.

---

## 🏗️ SETUP-STATUS

1. **SSH-Keys**: Ein dedizierter Key (`openclaw@frawo-hostinger`) wurde erstellt und auf allen Ziel-Nodes (Proxmox, Toolbox, Nextcloud, Odoo, Paperless) installiert.
2. **IP-Routing**: Alle Ziel-IPs wurden verifiziert (siehe unten).
3. **System Prompt**: Eine dedizierte Instruktions-Datei für den Agenten wurde erstellt.

---

## 📦 DAS PAKET FÜR OPENCLAW

Gib dem Agenten Zugriff auf das Repository und setze die folgenden Informationen als seinen **System-Prompt** oder **Context**:

### 1. System-Instruktionen & SSH-Key
Alle Details befinden sich in dieser Datei im Repo:
👉 [`OPENCLAW_SYSTEM_PROMPT.md`](file:///c:/Users/Admin/Documents/Private_Networking/OPENCLAW_SYSTEM_PROMPT.md)

### 2. SSH Private Key (Kopie für Hostinger)
Lasse den Agenten diesen Key als `~/.ssh/openclaw_ed25519` speichern:
```text
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDrydtMrMXeeDITVKZeFLp5pMmIuWnBI2yj8B4edYht4wAAAKAIhtaeCIbW
ngAAAAtzc2gtZWQyNTUxOQAAACDrydtMrMXeeDITVKZeFLp5pMmIuWnBI2yj8B4edYht4w
AAAEA+6LiUiPK7t2FdJ7KjdYBpNVwSw4Qe30S5T3PF9u2YsevJ20ysxd54MhNUpl4Uunmk
yYi5acEjbKPwHh51iG3jAAAAGG9wZW5jbGF3QGZyYXdvLWhvc3RpbmdlcgECAwQF
-----END OPENSSH PRIVATE KEY-----
```

---

## 🎯 ZIEL: AUTONOMES ARBEITEN

Sobald OpenClaw diesen Prompt und den Key hat, ist er instruiert:
- **Autonom zu handeln**: Repository pflegen, Status prüfen, Odoo/NC Aufgaben erledigen.
- **Wenig zu fragen**: Nur bei kritischen Infrastruktur-Eingriffen oder wenn Fakten fehlen.
- **SSOT zu wahren**: Alles wird im Repo dokumentiert.

---

## 🔗 RELEVANTE LINKS FÜR DICH

- **Repository**: `https://github.com/Wolfeetech/FraWo`
- **Tailscale Admin**: `https://login.tailscale.com/admin/machines` (zum Aufräumen der Namen)
- **Handoff Log**: [`CLAUDE_HANDOFF_BRAIN_AGENT.md`](file:///c:/Users/Admin/Documents/Private_Networking/OPENCLAW_HANDOFF_BRAIN_AGENT.md) (Archiv)

**Du kannst den Handoff jetzt abschließen. Der Agent ist bereit.**
