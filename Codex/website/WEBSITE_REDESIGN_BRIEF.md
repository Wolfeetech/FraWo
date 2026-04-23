# FraWo Website — Redesign Brief v3
Stand: 2026-04-23 | Für den nächsten Agenten

---

## Auftrag

Kompletter Neuaufbau der FraWo-Website in Odoo 17.
Der aktuelle Stand (v2, frawo_homepage_blocks.html) ist deployed aber NICHT das was gewollt ist.

---

## Stilrichtung

**Referenz:** NTS Radio (nts.live) — nicht kopieren, aber Gefühl übernehmen:
- Starke, klare Typografie
- Redaktionell, seriös, kein Agentur-Sprech
- Dark Mode als Primär, Light Mode als Alternative (beide müssen funktionieren)
- Wenig Dekoration, Content trägt das Design
- Kein Spielkram, kein Gradient-Overload

**Nicht:** Sunshine Live (zu verspielt), kein Bootstrap-Einheitsbrei

---

## Sprache & Ton

- **Direkte Du-Ansprache** — "Du brauchst Ton für deinen Abend" nicht "Sie suchen..."
- Kein Marketingsprech, keine Superlative
- Kurze Sätze, konkret
- Texte sind Platzhalter — Wolf passt sie selbst an
- Zwei Zielgruppen klar trennen (siehe unten)

---

## Struktur: B2C / B2B Trennung

### B2C — Für Künstler, Bands, private Veranstalter
- Emotional, zugänglich
- "Du willst einen Abend der klingt wie er klingen soll"
- Fokus: Ton, Licht, unkomplizierter Ablauf
- CTA: direkt mailen / anrufen

### B2B — Für Locations, Veranstalter, Unternehmen
- Technisch, auf Augenhöhe
- "Ihr plant Events — wir liefern die Technik die nicht auffällt"
- Fokus: Zuverlässigkeit, Planungssicherheit, wiederholbare Abläufe
- CTA: Anfrage / Erstgespräch

**Trennung:** Eigene Sektionen auf der Homepage ODER zwei Einstiegspunkte in der Navigation — nach Best Practice für kleine Dienstleister die wachsen wollen. Entscheidung kann Wolf treffen, Seite soll erweiterbar sein.

---

## Radio Player (AzuraCast) — VORBEREITUNG, nicht live

**Status:** AzuraCast aktuell nicht funktional. Nächste Woche wieder verfügbar (Limit-Reset).

**Was trotzdem gebaut werden soll:**
- Sticky Footer Player — immer sichtbar, unten
- Skeleton: Play/Pause Button, Sendungsname, Lautstärke-Slider
- Happy / Unhappy Rating (Thumbs up / down)
- UI vorhanden, aber disabled / "Coming soon" bis AzuraCast läuft
- Stream-URL: `/radio/listen/frawo_funk/radio.mp3` (unverändert aus altem Code)
- Player ist **Zusatz-Feature**, nicht Kern der Seite

---

## Technischer Status (Stand 2026-04-23)

### Was deployed ist (aber ersetzt werden soll):
- `ir.ui.view` ID=503: Homepage (website.homepage) — v2 HTML
- `ir.ui.view` ID=496: Contact (website.contactus) — v2 HTML
- CSS: `user_custom_rules.scss` im Container (ID=3 in ir.asset, bundle: web.assets_frontend)
- Bilder: ID 858 (service-stage.jpg Platzhalter), ID 859 (hero-bodensee.jpg Platzhalter)

### Kritisches Problem: CSS rendert nicht
Die Seite sieht "wie Word" aus — komplett ungestylt. CSS ist im Bundle (720KB, 0 Fehler),
aber die fw-Klassen scheinen nicht zu greifen. Muss der nächste Agent debuggen BEVOR
er das neue Design deployed.

Mögliche Ursache:
- SCSS kompiliert aber klassen landen nicht im Output (nur :root vars sind nachweisbar)
- Odoo-Theme (theme_treehouse) könnte overriden
- ir.asset Reihenfolge prüfen: ID=3 ist last in bundle, sollte prio haben

### SSH / Zugang:
```
SSH Key:    c:\Users\Admin\Workspace\Repos\FraWo\Codex\openclaw_id_ed25519
Proxmox:    root@100.69.179.87 (Tailscale)
VM 220:     qm guest exec 220 bash -- -c "..."
Container:  docker exec odoo-web-1 bash -c "..."
Odoo Shell: odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=odoo_db_pass_final_v1 --no-http
DB:         FraWo_GbR
Admin PW:   frawo_temp_2026
```

### Bilder:
- Platzhalter laufen (IDs 858/859)
- Echte Fotos: wolfstudiopc (Tailscale 100.98.31.60) — SMB noch nicht freigegeben
  → Wolf muss Freigabe aktivieren oder Fotos rüberkopieren

---

## Design System (für v3)

CSS-Klassen-Prefix: `fw-` beibehalten  
Font: Inter (Google Fonts, bereits geladen)  
Dark Mode Primary: `prefers-color-scheme: dark` + manuelle Toggle-Option  

### Vorschlag Token-Struktur für Dark/Light:
```css
:root {
  /* Light */
  --fw-bg: #f5f5f3;
  --fw-surface: #ffffff;
  --fw-text: #0a0a0a;
  --fw-text-2: #3a3a3a;
  --fw-accent: #e05500;  /* kräftiger als bisheriges Amber */
}
[data-theme="dark"], .dark {
  --fw-bg: #0a0a0a;
  --fw-surface: #141414;
  --fw-text: #f0f0ee;
  --fw-text-2: #a0a09e;
  --fw-accent: #ff6b1a;
}
```

---

## Was der nächste Agent als erstes tun soll

1. **CSS-Problem diagnostizieren:** Warum rendert die Seite ungestylt?
   - Bundle prüfen: `curl http://10.1.0.22:8069/web/assets/1/.../web.assets_frontend.min.css | grep fw-hero`
   - Wenn leer: ir.asset ID=3 und user_custom_rules.scss im Container prüfen
   
2. **Neues Design-System umsetzen** (nach diesem Brief)

3. **Player-Skeleton bauen** (disabled, schön, vorbereitet)

4. **B2C/B2B Struktur** implementieren

5. **Bilder** von wolfstudiopc holen sobald Freigabe steht

---

## Referenzen

- nts.live — Stil, nicht Inhalt
- Keine weiteren Vorgaben — Eigene kreative Entscheidungen sind erwünscht
