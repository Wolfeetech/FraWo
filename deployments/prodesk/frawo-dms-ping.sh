#!/bin/bash
# FraWo Totmannschalter: Herzschlag an healthchecks.io (Odoo #1525, M2 "zweiter Alarmweg").
# Laeuft auf dem ProDesk alle 5 min (frawo-dms.timer). Bleibt der Ping aus, weil ProDesk, Strom,
# Router oder Internet weg sind, alarmiert healthchecks.io Wolf von aussen.
# Eingerichtet 20.07.2026; ins Repo uebernommen und um Prometheus erweitert am 05.10.2026 (Claude).
# Die Ping-Adresse steht nur in /etc/frawo-dms.url (0600), nie im Repo.
URLFILE=/etc/frawo-dms.url
[ -s "$URLFILE" ] || exit 0
URL=$(tr -d ' \t\r\n' < "$URLFILE")
case "$URL" in ""|*PLACEHOLDER*) exit 0;; esac
# Health-Gate: Alertmanager UND Prometheus (CT155) muessen gesund sein, sonst /fail.
# Ohne Prometheus entstehen keine Alarme mehr; das soll auch von aussen auffallen.
if curl -fsS --max-time 8 http://10.1.0.35:9093/-/healthy >/dev/null 2>&1 \
   && curl -fsS --max-time 8 http://10.1.0.35:9090/-/ready >/dev/null 2>&1; then
  curl -fsS --max-time 10 --retry 2 "$URL" >/dev/null 2>&1
else
  curl -fsS --max-time 10 --retry 2 "${URL%/}/fail" >/dev/null 2>&1
fi
