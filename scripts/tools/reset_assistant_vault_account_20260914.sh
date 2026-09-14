#!/bin/bash
# Einmal-Skript (14.09.2026): erzeugt ein zufaelliges Passwort fuer das
# Vaultwarden-Konto assistant@frawo.tech, legt es GLEICHZEITIG in die
# Zwischenablage (zum Einfuegen im Browser) UND in eine geschuetzte Datei
# auf dem Anker (fuer kuenftige Automation per Claude), OHNE es je auf dem
# Bildschirm anzuzeigen.
set -euo pipefail

PW=$(openssl rand -base64 24)

# In die Zwischenablage (Windows clip.exe via Git Bash)
printf '%s' "$PW" | clip.exe

# Gleichzeitig geschuetzt auf dem Anker ablegen (chmod 600, nur root lesbar)
printf '%s' "$PW" | ssh anker-pve "pct exec 108 -- sh -c 'cat > /root/.vw_assistant_pw && chmod 600 /root/.vw_assistant_pw'"

unset PW

echo "Fertig. Das neue Passwort liegt in deiner Zwischenablage (Strg+V) und geschuetzt auf dem Server."
echo "Naechster Schritt: In Vaultwarden bei assistant@frawo.tech auf 'Einladung erneut senden',"
echo "den Link oeffnen, beim neuen Passwort einfach einfuegen (Strg+V)."
