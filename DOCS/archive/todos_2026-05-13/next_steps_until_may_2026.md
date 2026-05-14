# Nächste Schritte bis Mai 2026

> **Kontext:** Der Operator ist fachfremd und hat bis auf Weiteres nur ein Mobiltelefon zur Verfügung.
> Die Vaultwarden-Recovery-Offline-Kopien können frühestens im Mai 2026 erstellt werden.
> Dieses Dokument trennt klar, was jetzt (handy-only), später (wenn Laptop verfügbar) und im Mai möglich ist.

Stand: `2026-04-10`

---

## 🟢 Jetzt – Phone-only (kein Terminal nötig)

Diese Aufgaben können vollständig über GitHub App oder Browser erledigt werden.

- [ ] `OPERATOR_TODO_QUEUE.md` lesen und verstehen, was blockiert ist und warum.
- [ ] `MEMORY.md` und `LIVE_CONTEXT.md` lesen – aktuellen Systemstand auffrischen.
- [ ] `SECURITY_BASELINE.md` lesen (nur lesen, nichts ausführen) – verstehen, was noch offen ist.
- [ ] Entscheiden: Ist `device_rollout_verified` (Franz Surface / iPhone) bis Mai blockiert?
  - Wenn **ja**: Eintrag in `OPERATOR_TODO_QUEUE.md` entsprechend anpassen (Datum eintragen).
  - Wenn **nein / unklar**: als Frage im PR kommentieren oder Eintrag mit Notiz versehen.
- [ ] `docs/plans/next_steps_until_may_2026.md` (diese Datei) lesen und Punkte mental vorbereiten.
- [ ] `OPS_HOME.md` lesen – Überblick über alle aktiven Lanes behalten.
- [ ] Offene Entscheidungen aus `CHECKLIST_NEXT_STEPS_WOLF_FRANZ.md` prüfen, ob handy-only klärbar.

---

## 🟡 Später – wenn Laptop / Terminal verfügbar

Diese Aufgaben erfordern einen Laptop mit Terminal-Zugang. **Maximal eine Task pro Session.**

- [ ] **PBS-Restore-Drill** wiederholen → `make pbs-restore-proof`
  - Nachweis: exitstatus OK + Snapshot sichtbar in PBS
- [ ] **Tailnet Route-Freigabe + Split-DNS schließen** → `SECURITY_BASELINE.md` → Punkt 2
  - Nachweis: `make security-baseline-check` grün
- [ ] **`NETWORK_INVENTORY.md` via Easy-Box-Abgleich finalisieren** → `make easybox-browser-probe`
  - Nachweis: Inventar stimmt mit tatsächlichen Leases überein
- [ ] **Security-Baseline prüfen** → `make security-baseline-check`
  - Nachweis: Keine offenen kritischen Findings
- [ ] **`device_rollout_verified` abschließen** (wenn nicht bis Mai blockiert) → `scripts/prove_device_rollout.ps1`
  - Nachweis: sichtbarer Gerätenachweis für Franz Surface + iPhone

---

## 🔴 Mai 2026 – physische Aktion erforderlich

Diese Aufgaben erfordern physischen Zugang (Drucker, USB-Sticks, sicherer Aufbewahrungsort).

**Frühestes Datum: 2026-05-01**

- [ ] Zwei physische Offline-Kopien der Vaultwarden-Recovery-Infos erstellen.
  - Option A: Papierausdruck + USB-Stick an zwei getrennten Orten.
  - Option B: 2× USB-Stick, einer davon außerhalb des Büros / Hauses.
- [ ] Sichtprüfung: Beide Kopien sind lesbar und vollständig.
- [ ] In `LIVE_CONTEXT.md` nur den Status setzen: `recovery_material: verified` (keine Secrets eintragen).
- [ ] In `MEMORY.md` unter `## Aktive Operator-Aktionen` den Blocker als erledigt markieren.
- [ ] `scripts/release_mvp_gate.py` ausführen → MVP-Gate final schließen.
- [ ] Eintrag `vaultwarden_recovery_material_verified` in `OPERATOR_TODO_QUEUE.md` in ✅ Done verschieben.

---

## Empfohlene Reihenfolge (Gesamtüberblick)

```
Jetzt (Handy)          Lesen, Entscheiden, Klären
       ↓
Nächstes Laptop-Fenster    1 Task: PBS-Restore-Drill
       ↓
Weiteres Laptop-Fenster    1 Task: Tailnet / Split-DNS
       ↓
Mai 2026 (physisch)        Vaultwarden Offline-Kopien
       ↓
Nach Mai                   MVP-Gate schließen, dann Lane B / Website-Entscheid
```

---

## Hinweise

- Keine Secrets in dieses Dokument eintragen.
- Jeder Haken in dieser Checkliste setzt voraus, dass das Ergebnis in einer kanonischen Datei (`LIVE_CONTEXT.md`, `VM_AUDIT.md` oder `MEMORY.md`) gespiegelt wurde.
- Bei Unsicherheit gilt: erst lesen, dann fragen, dann handeln.
- Referenzdateien: `OPERATOR_TODO_QUEUE.md`, `MEMORY.md`, `LIVE_CONTEXT.md`, `SECURITY_BASELINE.md`, `OPS_HOME.md`.
