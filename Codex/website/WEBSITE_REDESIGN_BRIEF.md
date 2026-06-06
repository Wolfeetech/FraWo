# FraWo Website â€” Redesign Brief v3
Stand: 2026-04-23 | FÃ¼r den nÃ¤chsten Agenten

---

## Auftrag

Kompletter Neuaufbau der FraWo-Website in Odoo 17.
Der aktuelle Stand (v2, frawo_homepage_blocks.html) ist deployed aber NICHT das was gewollt ist.

---

## Stilrichtung

**Referenz:** NTS Radio (nts.live) â€” nicht kopieren, aber GefÃ¼hl Ã¼bernehmen:
- Starke, klare Typografie
- Redaktionell, seriÃ¶s, kein Agentur-Sprech
- Dark Mode als PrimÃ¤r, Light Mode als Alternative (beide mÃ¼ssen funktionieren)
- Wenig Dekoration, Content trÃ¤gt das Design
- Kein Spielkram, kein Gradient-Overload

**Nicht:** Sunshine Live (zu verspielt), kein Bootstrap-Einheitsbrei

---

## Sprache & Ton

- **Direkte Du-Ansprache** â€” "Du brauchst Ton fÃ¼r deinen Abend" nicht "Sie suchen..."
- Kein Marketingsprech, keine Superlative
- Kurze SÃ¤tze, konkret
- Texte sind Platzhalter â€” Wolf passt sie selbst an
- Zwei Zielgruppen klar trennen (siehe unten)

---

## Struktur: B2C / B2B Trennung

### B2C â€” FÃ¼r KÃ¼nstler, Bands, private Veranstalter
- Emotional, zugÃ¤nglich
- "Du willst einen Abend der klingt wie er klingen soll"
- Fokus: Ton, Licht, unkomplizierter Ablauf
- CTA: direkt mailen / anrufen

### B2B â€” FÃ¼r Locations, Veranstalter, Unternehmen
- Technisch, auf AugenhÃ¶he
- "Ihr plant Events â€” wir liefern die Technik die nicht auffÃ¤llt"
- Fokus: ZuverlÃ¤ssigkeit, Planungssicherheit, wiederholbare AblÃ¤ufe
- CTA: Anfrage / ErstgesprÃ¤ch

**Trennung:** Eigene Sektionen auf der Homepage ODER zwei Einstiegspunkte in der Navigation â€” nach Best Practice fÃ¼r kleine Dienstleister die wachsen wollen. Entscheidung kann Wolf treffen, Seite soll erweiterbar sein.

---

## Radio Player (AzuraCast) â€” VORBEREITUNG, nicht live

**Status:** AzuraCast aktuell nicht funktional. NÃ¤chste Woche wieder verfÃ¼gbar (Limit-Reset).

**Was trotzdem gebaut werden soll:**
- Sticky Footer Player â€” immer sichtbar, unten
- Skeleton: Play/Pause Button, Sendungsname, LautstÃ¤rke-Slider
- Happy / Unhappy Rating (Thumbs up / down)
- UI vorhanden, aber disabled / "Coming soon" bis AzuraCast lÃ¤uft
- Stream-URL: `/radio/listen/frawo_funk/radio.mp3` (unverÃ¤ndert aus altem Code)
- Player ist **Zusatz-Feature**, nicht Kern der Seite

---

## Technischer Status (Stand 2026-04-23)

### Was deployed ist (aber ersetzt werden soll):
- `ir.ui.view` ID=503: Homepage (website.homepage) â€” v2 HTML
- `ir.ui.view` ID=496: Contact (website.contactus) â€” v2 HTML
- CSS: `user_custom_rules.scss` im Container (ID=3 in ir.asset, bundle: web.assets_frontend)
- Bilder: ID 858 (service-stage.jpg Platzhalter), ID 859 (hero-bodensee.jpg Platzhalter)

### Kritisches Problem: CSS rendert nicht
Die Seite sieht "wie Word" aus â€” komplett ungestylt. CSS ist im Bundle (720KB, 0 Fehler),
aber die fw-Klassen scheinen nicht zu greifen. Muss der nÃ¤chste Agent debuggen BEVOR
er das neue Design deployed.

MÃ¶gliche Ursache:
- SCSS kompiliert aber klassen landen nicht im Output (nur :root vars sind nachweisbar)
- Odoo-Theme (theme_treehouse) kÃ¶nnte overriden
- ir.asset Reihenfolge prÃ¼fen: ID=3 ist last in bundle, sollte prio haben

### SSH / Zugang:
```
Proxmox:    root@100.69.179.87 (Tailscale)
VM 220:     qm guest exec 220 bash -- -c "..."
Container:  docker exec odoo-web-1 bash -c "..."
Odoo Shell: odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=odoo_db_pass_final_v1 --no-http
DB:         FraWo_GbR
Admin PW:   frawo_temp_2026
```

### Bilder:
- Platzhalter laufen (IDs 858/859)
- Echte Fotos: wolfstudiopc (Tailscale 100.98.31.60) â€” SMB noch nicht freigegeben
  â†’ Wolf muss Freigabe aktivieren oder Fotos rÃ¼berkopieren

---

## Design System (fÃ¼r v3)

CSS-Klassen-Prefix: `fw-` beibehalten  
Font: Inter (Google Fonts, bereits geladen)  
Dark Mode Primary: `prefers-color-scheme: dark` + manuelle Toggle-Option  

### Vorschlag Token-Struktur fÃ¼r Dark/Light:
```css
:root {
  /* Light */
  --fw-bg: #f5f5f3;
  --fw-surface: #ffffff;
  --fw-text: #0a0a0a;
  --fw-text-2: #3a3a3a;
  --fw-accent: #e05500;  /* krÃ¤ftiger als bisheriges Amber */
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

## Was der nÃ¤chste Agent als erstes tun soll

1. **CSS-Problem diagnostizieren:** Warum rendert die Seite ungestylt?
   - Bundle prÃ¼fen: `curl http://10.1.0.22:8069/web/assets/1/.../web.assets_frontend.min.css | grep fw-hero`
   - Wenn leer: ir.asset ID=3 und user_custom_rules.scss im Container prÃ¼fen
   
2. **Neues Design-System umsetzen** (nach diesem Brief)

3. **Player-Skeleton bauen** (disabled, schÃ¶n, vorbereitet)

4. **B2C/B2B Struktur** implementieren

5. **Bilder** von wolfstudiopc holen sobald Freigabe steht

---

## Referenzen

- nts.live â€” Stil, nicht Inhalt
- Keine weiteren Vorgaben â€” Eigene kreative Entscheidungen sind erwÃ¼nscht
