# FraWo Sicherheitsstandards

**Fassung 1.0, 08.09.2026.** Entstanden aus den Vorfällen vom 07./08.09.2026 —
jede Regel hat einen konkreten Anlass, keine stammt aus einem Lehrbuch.

---

## Der Grundgedanke

**Wir bauen keine Disziplin, wir bauen Fangnetze.**

Wolf arbeitet sprunghaft: Themen wechseln mitten im Satz, Aufgaben werden
angefangen und liegengelassen, Belege landen mal hier und mal dort. Das ist kein
Fehler, den man wegtrainiert — das ist die Arbeitsweise, und sie hat Vorteile
(schnell, breit, findet Zusammenhänge). Der Preis ist, dass nichts durch
Gewissenhaftigkeit gesichert ist.

Also muss das **System** die Gewissenhaftigkeit übernehmen. Konkret heißt das:

> **Chaos ist erlaubt. Stille ist es nicht.**

Alles darf durcheinandergehen — solange jedes Problem sich von selbst meldet,
bevor es teuer wird.

---

## Regel 1 — Nichts scheitert leise

**Anlass:** An einem einzigen Tag: Die Nachtsicherung meldete „erfolgreich",
während 36 GB unhochgeladen auf der lokalen Platte lagen. Der Backup-TÜV lief seit
dem Hardwareausfall gar nicht mehr. Die Paperless-Zufuhr war zwei Tage tot. 62
Aufgaben verloren ihre Spalte und verschwanden dadurch aus **jeder** Auswertung.
Keines dieser Probleme hat sich gemeldet.

**Standard:**
- Jeder automatische Vorgang schreibt eine **Kennzahl**, nicht nur ein Logfile.
  Eine Kennzahl, die fehlt, ist selbst ein Alarm (`absent()`-Regel).
- Geprüft wird das **Ergebnis am Ziel**, nie der Ablauf. „Exit-Code 0" beweist nichts.
- Ein Vorgang, der etwas erzeugt, prüft anschließend, ob es **dort angekommen** ist,
  wo es hin soll — und zwar durch Zurücklesen, nicht durch Vertrauen.

**Umsetzung:** Backup-TÜV (neu aufzubauen), Prometheus-Kennzahlen mit
`absent()`-Alarmen, Nachlesen über die verschlüsselte Cloud-Verbindung.

---

## Regel 2 — Der Wächter steht nie im Haus, das er bewacht

**Anlass:** Die Überwachung lief auf dem ProDesk und starb mit ihm — der Ausfall
blieb vier Stunden unbemerkt. Danach überwachte der Anker sich selbst. Und der
`node_exporter` des lebenden Knotens wurde über einen Relay auf dem **toten**
abgefragt.

**Standard:**
- Mindestens **eine** Prüfung muss von außerhalb der Anlage kommen.
- Kein Überwachungsziel darf über einen dritten Rechner laufen.
- Der Ausfall des Überwachungssystems selbst muss auffallen (Dead-Man-Schalter).

**Umsetzung:** Cloudflare-Tunnelbenachrichtigung per Mail (kostenlos, außerhalb
der Anlage, kein neuer Dienst). Perspektivisch: Überwachung auf den dritten Knoten.

---

## Regel 3 — Keine Automatik ohne Bremse und Protokoll

**Anlass, gleich zweifach:**
- `net-resilience.sh` startete bei jedem Ping-Fehler das Netzwerk neu und kappte
  damit **alle** Gäste. Ein 3-Sekunden-Wackler kostete 12 Stunden Totalausfall.
  Eine zweite Stufe hätte den Server hart abgeschaltet — sie zündete nur wegen
  eines Tippfehlers im Pfad nicht.
- Eine Odoo-Regel legte bei jedem Schreibvorgang auf getaggten Aufgaben Kopien in
  einem Sammelprojekt an. Ergebnis: Das Projekt ließ sich nicht leeren, es füllte
  sich selbst nach.

**Standard:**
- Jede Automatik beantwortet vor dem Bau drei Fragen: **Was ist der größtmögliche
  Schaden? Wie merkt man, dass sie lief? Wie schaltet man sie ab?**
- Automatiken, die **Daten vervielfältigen**, sind verboten. Ein Filter zeigt
  dasselbe, ohne zweite Wahrheit.
- Kein automatischer Eingriff in Netz, Strom oder Neustarts. Diagnose ja,
  Selbstheilung nein.
- Bestehende Automatiken werden **jährlich durchgesehen**.

**Durchsicht vom 08.09.2026 (13 aktive Odoo-Regeln):**

| | Regel | Befund |
|---|---|---|
| 🔴 | #16 Anschaffungs-Tag → Projekt 109 | vervielfältigte Aufgaben, Duplikat-Schutz prüfte den selbst veränderten Namen → **abgeschaltet** |
| 🔴 | #11 „FraWo TEMP: MCP-Freigabe" | vergab dem Agenten bei jedem Schreibvorgang auf **einem** Auftrag die Gruppe *Sales/Administrator*. Gerüst aus einem Umweg, seit Wochen scharf → **abgeschaltet** (die Gruppe selbst bleibt, ändert betrieblich nichts) |
| 🟡 | #1 Klausi-Bot → Webhook | Webhook-Geheimnis steht **im Klartext im Code** in der Datenbank; keine Sperre gegen die eigene Antwort → gehört nach Vaultwarden bzw. `ir.config_parameter` |
| 🟢 | #10 Aufgabe → Kalendertermin | **richtig gebaut** — sucht vorhandene Termine über `res_model_id` + `res_id`, also über die ID des Ursprungsdatensatzes. Genau das hat #16 gefehlt. (Nebenkosten: synchrone Google-Synchronisation je Schreibvorgang) |
| 🟢 | #18 Auftrag → Liefertermin | dasselbe korrekte Muster |
| 🟢 | #14 erledigte Aufgabe → Termin aufräumen | setzt `active = False`, löscht nicht → entspricht Regel 4 |
| 🟢 | #2 #4 #5 #6 #7 #9 #13 #15 | unauffällig, keine Vervielfältigung |

Die Lehre daraus steht in einem Satz: **Ein Duplikat-Schutz muss auf ein Merkmal
prüfen, das die Automatik selbst nicht verändert.** Der Anzeigename ist nie so
ein Merkmal.

---

## Regel 4 — Alles ist umkehrbar

**Anlass:** Vor jeder Konfigurationsänderung dieser zwei Tage wurde gesichert —
`rclone-gdrive.service.bak-20260907`, `jobs.cfg.bak-20260907`,
`net-resilience.cron.deaktiviert-20260908`. Das hat mehrfach gerettet. Beim
Projektumbau in Odoo dagegen gingen 62 Spaltenzuordnungen verloren; nur weil Odoo
Änderungen protokolliert, ließen sich 60 davon zurückholen.

**Standard:**
- **Sicherung vor Änderung**, mit Datum im Namen: `datei.bak-JJJJMMTT`.
- **Abschalten statt löschen.** Deaktivierte Regeln, archivierte Projekte,
  umbenannte Cron-Dateien — alles bleibt, nichts verschwindet.
- **Entwurf vor Buchung.** Rechnungen entstehen als Entwurf; gebucht wird bewusst.
- Bei Massenänderungen: vorher zählen, nachher zählen, Differenz erklären.

---

## Regel 5 — Eine Sache, ein Ort

**Anlass:** Belege liegen teils in Paperless, teils in Odoo, teils nur im
Kontoauszug — mit Überschneidungen und Lücken in beide Richtungen. Dieselbe
Wärmepumpen-Kette hatte Meilensteine in einem archivierten Projekt, während die
Aufgaben in einem anderen lagen.

**Standard:**

| Was | Wo | Sonst nirgends |
|---|---|---|
| Aufgaben, Fristen, Geld | **Odoo** | — |
| Dokumente und Belege | **Paperless** | Drive nur als Eingang |
| Zustand der Anlage | **NOW.md** im Repo | — |
| Zugangsdaten | **Vaultwarden** | niemals in Dateien oder Chats |

- Ein Beleg, der nicht in Odoo als Rechnung steht, existiert für die Buchhaltung
  nicht. Deshalb muss die Strecke Paperless → Odoo automatisch laufen.
- Kopien sind verboten, Verweise erwünscht.

---

## Regel 6 — Was Geld oder Freiheit kostet, hat ein Datum im System

**Anlass:** Ein Bußgeldbescheid mit Zwei-Wochen-Frist und einem Antrag auf
Erzwingungshaft lag zwei Wochen unbemerkt in Paperless. Der Go-Live-Termin für den
Verleih verstrich, ohne dass die Aufgabe den Status wechselte. Fünf Meilensteine
waren seit Wochen überfällig und unsichtbar.

**Standard:**
- Jede Frist aus einem Dokument wird zu einer Odoo-Aufgabe **mit `date_deadline`**.
  Nicht in den Kalender, nicht in den Kopf.
- Behördenpost wird **am Eingangstag** ausgewertet, nicht bei Gelegenheit.
- Überfällige Fristen erscheinen im Tagesbericht — jeden Tag, bis sie erledigt sind.
- Wiederkehrende Zahlungen laufen als **Dauerauftrag**, nicht als Erinnerung.
  Bei jedem Kontowechsel gehören sie auf die Checkliste. (Der ganze
  Finanzamtsvorgang entstand aus einem beim Kontowechsel unterbrochenen
  Dauerauftrag.)

---

## Regel 7 — Ein Bericht, der zu Wolf kommt

> **Seit 09.09.2026 in Betrieb.** Kein neuer Kanal und kein neuer Dienst:
> Odoo-Cron 44 lief bereits täglich — er schrieb seinen Bericht nur in den
> Chatter einer Aufgabe, die niemand öffnet, und zählte abgebrochene Aufgaben
> als offen. Jetzt geht er per E-Mail über denselben Brevo-Postausgang, den die
> Überwachung schon benutzt. Quelle: `scripts/odoo_tagesbericht.py`.

**Anlass:** Alle Informationen dieses Tages *waren* im System. Sie mussten nur
jemand suchen. Bei einer sprunghaften Arbeitsweise ist „man müsste mal nachsehen"
keine Sicherung.

**Standard:** Ein **täglicher Lagebericht** über den bestehenden Telegram-Weg
(Jarvis), der genau fünf Fragen beantwortet:

1. Ist gestern Nacht die Sicherung gelaufen — und ist sie **angekommen**?
2. Welche Fristen sind überfällig oder laufen in den nächsten 7 Tagen ab?
3. Was steht in „In Arbeit" und hat sich seit 14 Tagen nicht bewegt?
4. Welche Rechnungen stehen noch auf Entwurf?
5. Was wartet auf eine Entscheidung von Wolf (Schlagwort „🙋 braucht Wolf")?

**Kein neuer Kanal.** Der Weg existiert, es fehlt nur der Inhalt.
Und: **Wenn nichts brennt, kommt eine kurze Meldung** — Stille darf nie „alles gut"
bedeuten, denn Stille ist auch das Bild eines toten Systems.

---

## Regel 8 — Vier Augen bei allem, was produktiv läuft

Steht bereits im Agenten-Protokoll und hat sich bewährt. Ergänzung aus der Praxis
dieser zwei Tage:

- **Wer etwas gebaut hat, setzt es nicht selbst auf „Erledigt".**
- Bei Massenänderungen an Daten: **nachzählen und die Differenz erklären**, bevor
  man Vollzug meldet. Fünf der heutigen Funde kamen erst beim Nachzählen ans Licht.
- Eine Erfolgsmeldung ohne Messwert ist keine.

---

## Was das mit dem Geschäftsziel zu tun hat

Diese Anlage ist der Prototyp für eine Dienstleistung. Ein Kunde kauft keine
Technik, er kauft **Verlässlichkeit** — und die entsteht nicht durch bessere
Hardware, sondern durch genau diese Regeln.

Der Maßstab bleibt: **reproduzierbar, dokumentiert, von jemand anderem betreubar.**
Ein Kunde mit derselben sprunghaften Arbeitsweise bekommt dasselbe Fangnetz —
und das ist dann das eigentliche Produkt.

---

## Umsetzungsstand

| Regel | Stand |
|---|---|
| 1 · Nichts scheitert leise | 🟡 `absent()`-Regel für die Wache ergänzt (bereitgestellt), **Backup-TÜV fehlt** |
| 2 · Wächter außerhalb | 🟡 Wache zieht auf den Anker (bereitgestellt, braucht Telegram-Schlüssel aus Vaultwarden). Cloudflare-Mail weiter offen |
| 3 · Automatik mit Bremse | ✅ alle 13 durchgesehen, zwei abgeschaltet, ein Punkt zum Nachziehen (#1) |
| 4 · Umkehrbar | ✅ gelebt, hier erstmals aufgeschrieben |
| 5 · Eine Sache, ein Ort | 🟡 Struktur steht, Strecke Paperless → Odoo defekt |
| 6 · Fristen im System | ✅ überfällige Fristen und Meilensteine stehen im Tagesbericht |
| 7 · Täglicher Lagebericht | ✅ **läuft** — Odoo-Cron 44 sendet täglich per Mail an wolf@frawo.tech |
| 8 · Vier Augen | ✅ im Protokoll, wird gelebt |

*Geschrieben von Claude Code am 08.09.2026. Änderungen nur mit Wolfs Zustimmung —
diese Datei ist Teil des Agenten-Protokolls.*
