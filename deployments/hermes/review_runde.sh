#!/usr/bin/env bash
# Hermes prueft liegengebliebene Peer-Reviews (Jarvis faellt aus, #1964). Laeuft auf CT160 als Benutzer hermes.
# Aufruf: bash review_runde.sh 1915 1908 1541 ...   Ergebnis je Aufgabe als Kommentar "🤖 [Hermes]" in Odoo.
cd "$HOME/FraWo" && git pull -q
export HERMES_DISABLE_TELEMETRY=1
for id in "$@"; do
  echo "=== #$id $(date +%T)"
  timeout 1500 "$HOME/.local/bin/hermes" -z "Peer-Review nach AGENTS.md für Odoo-Aufgabe $id (project.task). Lies Beschreibung und Chatter, besonders die letzte Review-Bitte und die Nachweise. Prüfe Behauptungen, soweit möglich, gegen das Repo ($HOME/FraWo) und Odoo; Live-Aussagen prüfst du lesend per SSH (OptiPlex 10.1.0.227, Anker 10.1.0.92, ProDesk 10.1.0.128; Fundorte siehe AGENTS.md 'Wo liegt was'), ohne etwas zu ändern; was trotzdem nicht prüfbar ist, benennst du. Poste genau EINEN Kommentar an Aufgabe $id mit Signatur 🤖 [Hermes]: Urteil ✅ oder ❌, Begründung kurz (geprüft / nicht prüfbar / Befund). Ändere sonst nichts, keine Stage. Antworte mir nur mit: #$id ✅ oder ❌ und ein Halbsatz." 2>&1 | tail -1
done
