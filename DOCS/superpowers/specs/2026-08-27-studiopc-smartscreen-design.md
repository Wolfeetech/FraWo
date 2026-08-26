# StudioPC "Smart Screen" auf Touchscreen + Surface Go

## Ziel

Der Touchscreen am stock-pve (Aufgabe #1039) und Wolfs Surface Go (1. Generation)
sollen zusätzlich zu ihrer normalen Rolle (Dashboard) einen zweiten,
unabhängigen virtuellen Bildschirm des StudioPC anzeigen und bedienen können —
ohne den Fernseher (der aktuell an Monitor 1 hängt) zu beeinflussen. Wolf sitzt
oft nicht direkt am StudioPC (Fernseher blockiert), will aber trotzdem
arbeiten können.

## Nicht-Ziele

- Keine Migration von Odoo/AzuraCast/etc. — reine Anzeige-/Fernsteuerungs-Frage.
- Kein Ersatz für den Fernseher-Anschluss (Monitor 1 bleibt unverändert).
- Keine Lösung für Zugriff von außerhalb des Tailnets — beide Clients sind
  ohnehin über Tailscale erreichbar, kein neuer öffentlicher Zugang.

## Architektur

```
StudioPC (Windows 11 Home, Tailscale 100.98.31.60)
├── Virtueller Bildschirmtreiber (open source, IDD-basiert)
│     → "Monitor 2": rein virtuell, keine physische Buchse, keine Auswirkung auf Monitor 1 (TV)
├── TigerVNC-Server
│     → teilt NUR Monitor 2
│     → lauscht NUR auf 100.98.31.60 (Tailscale-Interface), nicht auf 0.0.0.0
│     → Passwort-geschützt (VNC-Auth)
└── Tailscale (bereits vorhanden, kein neuer Port am Router)

        │  (beide Clients unabhängig, gleichzeitig möglich — VNC erlaubt
        │   mehrere Betrachter nativ)
        │
        ├── Touchscreen (stock-pve, bestehender Chromium-Kiosk, Aufgabe #1039)
        │     → neuer Kiosk-Reiter "StudioPC" lädt noVNC (HTML5-VNC-Client,
        │       läuft im selben Chromium, keine neue Software auf dem Host)
        │
        └── Surface Go 1. Gen (Windows)
              → TigerVNC-Viewer (portable, keine Installation nötig)
```

## Komponenten im Detail

1. **Virtueller Monitor (StudioPC).** Ein quelloffener Indirect-Display-Treiber
   (z. B. "Virtual Display Driver", basiert auf Microsofts IDD-Beispieltreiber)
   erzeugt einen zusätzlichen Windows-Bildschirm, der nie eine echte Grafikbuchse
   braucht. Windows behandelt ihn wie jeden zweiten Monitor — Fenster lassen
   sich dorthin verschieben, eine App kann dort im Vollbild laufen.

2. **VNC-Server (StudioPC).** TigerVNC-Server, konfiguriert auf genau diesen
   virtuellen Monitor (nicht "ganzer Desktop"). Bindet ausschließlich an die
   Tailscale-IP — von außerhalb des Tailnets nicht erreichbar, unabhängig von
   der VNC-Passwortsicherheit selbst. Startet als Windows-Dienst automatisch
   mit dem PC.

3. **Touchscreen-Client.** Der bestehende Chromium-Kiosk (autologin, tty2,
   Aufgabe #1039) bekommt einen zusätzlichen Reiter/Knopf, der noVNC lädt und
   sich mit der StudioPC-Tailscale-IP verbindet. Kein zusätzliches Programm
   auf stock-pve nötig, nur eine weitere Seite im selben Kiosk.

4. **Surface-Go-Client.** TigerVNC-Viewer (portable .exe, quelloffen), auf dem
   Desktop verknüpft, verbindet sich mit derselben Adresse.

## Ablauf (Nutzersicht)

1. Wolf tippt am Touchscreen (oder öffnet die App am Surface Go) auf
   "StudioPC".
2. Er sieht den virtuellen Monitor 2 des StudioPC — leer, bis er selbst ein
   Fenster dorthin zieht oder eine App dort öffnet.
3. Touch-Tipp = Mausklick, Wischen = Mausbewegung. Tastatur bei Bedarf über
   die Bildschirmtastatur des jeweiligen Geräts.
4. Der Fernseher (Monitor 1) zeigt währenddessen unverändert weiter, was
   gerade läuft.

## Fehlerfälle & Sicherheit

- **StudioPC ausgeschaltet/im Ruhezustand:** VNC-Verbindung schlägt fehl,
  Kiosk zeigt eine einfache Fehlermeldung statt eines hängenden grauen
  Bildschirms (noVNC macht das von Haus aus).
- **VNC-Passwort:** eigenes, nicht mit anderen Diensten geteiltes Passwort,
  landet in Vaultwarden (nicht im Repo, analog zur #815-Konvention).
- **Kein neuer offener Port am Router.** Erreichbarkeit ausschließlich über
  Tailscale — passt zur bestehenden FraWo-Sicherheitslinie ("keine einzige
  Portweiterleitung").
- **Mehrere Betrachter gleichzeitig:** TigerVNC erlaubt das nativ; beide
  Geräte teilen sich Maus/Tastatur der einen Sitzung (kein getrenntes
  Multi-User-Desktop — das wäre ein eigenes, viel größeres Projekt).

## Testen

- Virtueller Monitor erscheint in Windows-Anzeigeeinstellungen als Monitor 2,
  Monitor 1 (TV) bleibt unverändert bedienbar.
- VNC-Verbindung vom Touchscreen UND vom Surface Go gleichzeitig möglich,
  beide sehen denselben Inhalt in Echtzeit.
- Verbindungsversuch von einem Gerät AUSSERHALB des Tailnets (z. B. normales
  Heim-WLAN ohne Tailscale) schlägt fehl — bestätigt, dass nicht versehentlich
  auf 0.0.0.0 gelauscht wird.
- PC-Neustart: VNC-Server kommt automatisch wieder hoch, ohne manuellen
  Eingriff.
