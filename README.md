# FraWo Operations Workspace

Dieses Repository ist der technische Arbeitsraum für **Homeserver 2027**.

## 🚀 Startpunkt für Entwickler & Agenten

Wenn du ein neuer Entwickler oder ein KI-Agent bist, lies bitte zuerst:
1. **[`AGENT_ONBOARDING.md`](AGENT_ONBOARDING.md)** - Die Schritt-für-Schritt-Anleitung für das Onboarding und die Arbeitsweise im Projekt.
2. **[`NOW.md`](NOW.md)** - Der aktuelle Live-Zustand der Infrastruktur (IPs, VLANs, VMs).

---

## 🎯 Single Source of Truth (SSOT)

Wir arbeiten mit einem strikten SSOT-Modell, um Missverständnisse und veraltete Stände zu vermeiden:

- **Aufgaben & Roadmaps (Odoo):** 
  Alle aktiven Projekte, Aufgaben (Tasks), Meilensteine und Roadmaps werden ausschließlich in Odoo unter `http://10.1.0.112:8069` (Projekt: *🚀 Homeserver 2027: Masterplan*) gepflegt. Lokale Roadmaps oder `todo.md`-Dateien existieren nicht mehr.
  
- **Infrastruktur-Zustand (`NOW.md`):**
  Die Datei `NOW.md` ist der einzige Ort im Repository, an dem der physische Zustand des Netzwerks und der Server gepflegt wird.

- **Passwörter & API-Keys (Vaultwarden):**
  Alle Passwörter und sensitive Daten liegen sicher in Vaultwarden. Im Code oder in Aufgabenbeschreibungen werden nur Bezeichnungen oder UUIDs referenziert.

---

## 📂 Repository-Struktur

- **`apps/`** - Quellcode der Anwendungen (z. B. `radio-backend`, `radio-player-frontend`).
- **`scripts/`** - Automatisierungs- und Wartungs-Skripte.
- **`manifests/`** - Kubernetes-, Docker-Compose- oder System-Manifeste.
- **`ansible/`** - Ansible-Playbooks zur Konfiguration der Server.
- **`scratch/`** - Temporäre Skripte zum Testen und Debuggen (werden nicht versioniert oder dienen nur als Entwurf).
