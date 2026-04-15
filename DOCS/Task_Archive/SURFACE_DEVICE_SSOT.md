# Surface Device Single Source of Truth (SSOT)

Um Verwechslungen zwischen den verschiedenen Surface-Modellen zu vermeiden, definieren wir hier die kanonische Nomenklatur für das gesamte Projekt. Jede KI und jeder Operator muss diese Aliase verwenden.

## Die drei Surface-Klassen

| Eindeutiger Alias | Hardware-Details | Rolle | Primärer Nutzer | Netzwerk / Zugriff |
| :--- | :--- | :--- | :--- | :--- |
| **`surface-wolfi`** | Microsoft Surface Laptop | Operator-Arbeitsgerät | Wolf | `192.168.2.118` (DHCP LAN) <br> Split-Access (lokales WLAN + Tailscale on-demand) |
| **`surface-franz`** | Microsoft Surface Laptop | Business-Gerät (MVP) | Franz | `100.x.x.x` (Tailscale) <br> Business-Pfad Rollout |
| **`kiosk-frontend`** | Microsoft Surface Go | Haus-Dashboard | Shared | `192.168.2.154` (DHCP LAN) <br> Kiosk Browser, Touch-UI |

## Vorgaben für Dokumentation & Rollout

- Wenn es um das Gerät von Franz geht, heißt es ab sofort immer **`surface-franz`**. Niemals "Surface Laptop" pur verwenden.
- Wolfs Arbeitslaptop heißt **`surface-wolfi`**. Er ist kein reiner Kiosk und kein reines Testgerät, sondern hat ein Split-Access Profil.
- Das Smart-Home- und Radio-Tablet im Hausnetz heißt **`kiosk-frontend`**.

## Identifikation

- `surface-wolfi`: Bisher im Router als `Surface_Laptop` auf `.118` geführt.
- `kiosk-frontend`: Bisher im Router als `yourparty-Surface-Go` auf `.154` geführt.
- `surface-franz`: Wird primär über das Tailnet als aktiver Client eingeführt.
