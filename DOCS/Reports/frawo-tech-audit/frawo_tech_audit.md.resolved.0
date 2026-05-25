# Audit-Bericht & ToDo-Liste: FraWo-Tech.de

Dieser Bericht enthält die gefundenen Fehler und Abweichungen von Best Practices auf der Webseite [www.frawo-tech.de](https://www.frawo-tech.de/). Er ist so strukturiert, dass ein Claude Agent oder Entwickler die Punkte direkt abarbeiten kann.

## 1. Inhaltliche & Strukturelle Fehler (Inhaltsebene)

*   **[ ] Odoo Standard-Blindtext entfernen:**
    *   **Fundstelle:** Sektion "Über uns" (Zeile 121-122 im Content-Dump).
    *   **Text:** *"Wir sind ein Team von leidenschaftlichen Menschen, deren Ziel es ist, das Leben aller durch bahnbrechende Produkte zu verbessern..."*
    *   **Problem:** Das ist der Standard-Text von Odoo. Er wirkt extrem unprofessionell.
    *   **Lösung:** Durch echten Text über FraWo GbR ersetzen oder die Sektion vorerst entfernen.
*   **[ ] Fake-Telefonnummer ersetzen:**
    *   **Fundstelle:** Kontaktbereich (Zeile 127).
    *   **Text:** `+1 555-555-5556`
    *   **Problem:** Amerikanische Fake-Nummer.
    *   **Lösung:** Durch die echte Telefonnummer von FraWo ersetzen.
*   **[ ] Navigation korrigieren (Tote Links):**
    *   **Fundstelle:** Nützliche Links im Footer (Zeile 105-108).
    *   **Problem:** Die Links `Über uns`, `Produkte`, `Dienstleistungen`, `Rechtliches` zeigen alle auf die Startseite `https://www.frawo-tech.de/` anstatt auf die entsprechenden Sektionen oder Unterseiten.
    *   **Lösung:** Anker-Links setzen (z.B. `/#services` für Dienstleistungen) oder korrekte Seiten verlinken.
*   **[ ] Odoo-Branding entfernen:**
    *   **Fundstelle:** Ganz unten im Footer (Zeile 139).
    *   **Text:** `[kostenlose Website](http://www.odoo.com/...)`
    *   **Problem:** Zeigt, dass es eine Standard-Odoo-Seite ist.
    *   **Lösung:** Den "Powered by Odoo" bzw. "Kostenlose Website" Link im Footer entfernen (meist in den Odoo-Website-Einstellungen oder im Footer-Template).
*   **[ ] Falsche Kategorie im Footer:**
    *   **Fundstelle:** Footer (Zeile 132).
    *   **Text:** Überschrift "Folgen Sie uns" enthält die Links zu Impressum und Datenschutz.
    *   **Problem:** Unter "Folgen Sie uns" erwartet man Social Media Links, keine Rechtstexte.
    *   **Lösung:** Die Links in eine passende Kategorie verschieben oder die Überschrift anpassen.

## 2. Visuelle & Optische Fehler (Aus der Voranalyse)

*   **[ ] Odoo-Logo im Header ersetzen:**
    *   Das Standard-Odoo-Logo muss durch das FraWo-Logo ersetzt werden.
*   **[ ] Kontrast der Checkliste im Hero-Bereich erhöhen:**
    *   Die graue Schrift auf dunklem Grund ist schwer lesbar.
*   **[ ] Mobile Layouts fixen:**
    *   **Expertise-Sektion:** Text wird mobil zu stark gequetscht.
    *   **Kunden-Grid:** Texte ragen über die Karten hinaus.
*   **[ ] Funk-Statusleiste fixen:**
    *   Die Subdomain `funk.frawo-tech.de` löst nicht auf. Entweder DNS fixen oder die Komponente entfernen, damit sie nicht in der Dauerschleife hängt.

---
*Erstellt am 16.05.2026 für die Weiterverarbeitung durch den Claude Agent.*
