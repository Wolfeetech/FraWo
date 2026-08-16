# Gemini/Antigravity — Start hier, jede Sitzung

**Lies zuerst [`AGENTS.md`](AGENTS.md) in diesem Repo komplett durch. Jede Regel dort ist
für dich genauso bindend wie für jeden anderen Agenten.** Diese Datei dupliziert AGENTS.md
nicht, sondern verstärkt die Punkte, die am 2026-08-04 konkret missachtet wurden — lies sie
zusammen mit AGENTS.md, nicht statt.

## Was am 2026-08-04 schiefging (damit es nicht nochmal passiert)

1. **CI v3.0 ignoriert** (AGENTS.md §5 existierte schon): Kiosk/Anker-Tracker wurde mit
   Glassmorphism, Cyan/Purple/Emerald-Paletten und einem zweiten Google-Font gebaut — obwohl
   [`SSOT/FRAWO_CI_GUIDELINES.md`](SSOT/FRAWO_CI_GUIDELINES.md) flach, 0px-Radius, nur
   Forest/Violet/Void, nur Inter vorschreibt. **Vor jeder sichtbaren/kundenseitigen Änderung:
   diese Datei öffnen und jeden Farbwert/Radius/Schatten dagegen prüfen — nicht das eigene
   Geschmacksurteil verwenden.**
2. **Direkt an Produktion vorbei deployt** (SSH + `pct push`, direkte Odoo-XML-RPC-Writes),
   am Git-Repo komplett vorbei. Ergebnis: niemand konnte nachvollziehen, was geändert wurde,
   Repo und Live-Server sind jetzt inkonsistent. **Code-Änderungen (Controller, Views) gehören
   ins Repo und werden über einen nachvollziehbaren Weg deployt — kein Base64-über-SSH-Hack.**
3. **"Fertig"/"verifiziert" behauptet, ohne es zu prüfen**: die Radio-"Engine" war erfunden
   (Standardeinstellungen, teils sogar falsch), der Alois-Prinz-Auftrag ist eine leere Hülle,
   Songzahlen waren falsch. **Bevor du in einem Walkthrough "✅ verifiziert" schreibst: den
   echten Endpunkt aufrufen, den echten Datensatz auslesen. Eine Behauptung ohne diesen Beleg
   gilt als nicht verifiziert.**
4. **Passwörter im Klartext** in ~10 Wegwerf-Skripten. AGENTS.md §3 verbietet das bereits
   ausdrücklich. **Auch in `scratch/`-Dateien nicht tun**, selbst wenn sie gitignored sind —
   sie liegen trotzdem offen auf der Platte.
5. **Neue Planungsdokumente erstellt** (`DOCS/STOCKENWEILER_AIRBEAM_VPN_SETUP_GUIDE.md`), obwohl
   AGENTS.md §3 das explizit untersagt ("No Stale Documents") — und eine davon behandelte sogar
   das falsche Thema (aus einer anderen Session reinkopiert).

## Zusätzlich, bevor du irgendwas Kundenseitiges baust

Der User hat kein IT-Hintergrundwissen und sagt bewusst nur das Ziel ("bau mir eine
professionelle Website"), nicht den Weg. Das heißt für dich: **das Nachdenken über den Weg ist
dein Job, nicht seiner.**

- Recherchiere zuerst 2–3 echte, konkrete Referenzen aus der relevanten Branche (z.B.
  Veranstaltungstechnik-/Radio-Anbieter), bevor du irgendwas baust — nicht das generische
  "KI-Demo-Design" (Glow, Glasoptik, Regenbogenfarben) als Standard nehmen.
- Gleiche dein Konzept gegen `SSOT/FRAWO_CI_GUIDELINES.md` und `DOCS/FRAWO_SERVICES_REAL.md` ab,
  bevor du es umsetzt.
- Erfinde keine Fakten (Preise, Namen, Zahlen) — wenn etwas unklar ist, als offene Frage markieren,
  nicht raten.
