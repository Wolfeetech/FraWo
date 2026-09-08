# -*- coding: utf-8 -*-
# Aufraeumen der von base.automation-Regel 16 erzeugten Kopien, 08.09.2026.
#
# BEFUND
# Die Regel "Anschaffungs-Tag -> Task in Proj 109" hat bei JEDEM Schreibvorgang
# auf einer Aufgabe mit Schlagwort 147 eine Kopie angelegt. Das ist dreimal
# gelaufen und hat drei Generationen erzeugt:
#
#   Generation 0  die echten Aufgaben, in ihren Fachprojekten, saubere Namen
#   Generation 1  Kopien davon (01.09. / 06.09. / 08.09.), Name mit "?" davor,
#                 Beschreibung "Automatisch erkannt aus Projekt ... Original
#                 Task: ..." - ausser bei zwoelf Stueck, die eine echte
#                 Bewertung als Beschreibung bekommen haben
#   Generation 2  Kopien der Kopien (08.09. 21:08:28), Name mit doppeltem
#                 Gluehbirnen-Zeichen - entstanden, weil das Verschieben der
#                 Generation 1 aus Projekt 109 heraus die Regel erneut ausloeste
#
# WICHTIG: Die 26 Aufgaben, die am 08.09. aus Projekt 109 nach 163 verschoben
# wurden, waren also KEINE Originale. Sie sind selbst Generation 1. Deshalb
# stehen sie alle auf "In Arbeit" und blaehen die Zahl der laufenden Aufgaben
# auf, ohne dass irgendjemand daran arbeitet.
#
# VORGEHEN
# Nicht loeschen, sondern archivieren (active = False). Umkehrbar mit einem
# Schreibvorgang, und die Historie bleibt lesbar. Vor dem Archivieren wird
# geprueft, ob das Original wirklich existiert - fehlt es, bleibt die Kopie
# unangetastet und wird gemeldet.
#
# Die zwoelf Bewertungen aus Generation 1 gehen nicht verloren: sie werden
# vorher als Notiz in den Chatter des Originals geschrieben.
#
# Laeuft in der Odoo-Shell auf CT140.

import re
from markupsafe import Markup

# Kopie -> echtes Original (Generation 0)
KOPIE_ZU_ORIGINAL = {
    # --- Generation 1, mit Bewertung in der Beschreibung ---
    1236: 1157, 1238: 374,  1240: 1182, 1241: 1103,
    1242: 1100, 1243: 1099, 1245: 430,  1247: 385,
    1248: 380,  1249: 377,  1250: 265,  1251: 521,
    # --- Generation 1, reine Kopie ohne Eigeninhalt ---
    1286: 1264, 1291: 381,  1293: 1183, 1294: 1159,
    1366: 1038, 1367: 1205, 1368: 1206, 1369: 1207,
    1370: 1170,
    # --- Generation 2, Kopien der Kopien ---
    1372: 380,  1373: 1103, 1374: 1244, 1375: 1100,
    1376: 1159, 1377: 1183, 1378: 381,  1379: 1264,
    1380: 377,  1381: 1099, 1382: 374,  1383: 521,
    1384: 265,  1385: 385,  1386: 430,  1387: 1182,
    1388: 1157,
}

# Nur diese tragen eine echte Bewertung, die erhalten bleiben muss.
MIT_BEWERTUNG = [1236, 1238, 1240, 1241, 1242, 1243,
                 1245, 1247, 1248, 1249, 1250, 1251]

Task = env['project.task']


def nur_text(html):
    if not html:
        return ""
    txt = re.sub(r'<[^>]+>', ' ', html)
    txt = txt.replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
    txt = txt.replace('&nbsp;', ' ')
    return re.sub(r'\s+', ' ', txt).strip()


print("=" * 78)
print("VORHER")
print("=" * 78)
offen_vorher = Task.search_count([('stage_id', 'not in', (6, 35))])
arbeit_vorher = Task.search_count([('stage_id', '=', 3)])
print("  offene Aufgaben gesamt: %d" % offen_vorher)
print("  davon 'In Arbeit':      %d" % arbeit_vorher)
print("")

# --- 1. Bewertungen sichern -----------------------------------------------
print("=" * 78)
print("BEWERTUNGEN AUF DIE ORIGINALE UEBERTRAGEN")
print("=" * 78)

uebertragen = 0
for kopie_id in MIT_BEWERTUNG:
    kopie = Task.browse(kopie_id).exists()
    orig = Task.browse(KOPIE_ZU_ORIGINAL[kopie_id]).exists()
    if not kopie or not orig:
        print("  %-5s uebersprungen (Kopie oder Original fehlt)" % kopie_id)
        continue
    text = nur_text(kopie.description)
    if not text:
        continue
    orig.message_post(
        body=Markup("🤖 [Claude] Bewertung aus der automatisch "
                    "erzeugten Kopie #%d uebernommen, bevor diese "
                    "archiviert wurde:<br/><b>%s</b>")
        % (kopie_id, text),
        message_type='comment', subtype_xmlid='mail.mt_note')
    print("  #%-5s -> #%-5s  %s" % (kopie_id, orig.id, text[:52]))
    uebertragen += 1

print("")
print("  %d Bewertungen gesichert." % uebertragen)
print("")

# --- 2. Kopien archivieren -------------------------------------------------
print("=" * 78)
print("KOPIEN ARCHIVIEREN (nicht loeschen)")
print("=" * 78)

archiviert = []
verweigert = []

for kopie_id, orig_id in sorted(KOPIE_ZU_ORIGINAL.items()):
    kopie = Task.browse(kopie_id).exists()
    if not kopie:
        continue
    # Sicherheitsnetz: ohne lebendes Original wird nichts weggeraeumt.
    orig = Task.browse(orig_id).exists()
    if not orig:
        verweigert.append((kopie_id, kopie.name[:50], "Original %s fehlt" % orig_id))
        continue
    if not orig.active:
        verweigert.append((kopie_id, kopie.name[:50], "Original %s archiviert" % orig_id))
        continue
    kopie.write({'active': False})
    archiviert.append((kopie_id, orig_id, kopie.name[:52]))

print("  archiviert: %d" % len(archiviert))
for kid, oid, name in archiviert:
    print("    #%-5s (Original #%-5s) %s" % (kid, oid, name))

if verweigert:
    print("")
    print("  NICHT angefasst: %d" % len(verweigert))
    for kid, name, grund in verweigert:
        print("    #%-5s %-50s %s" % (kid, name, grund))

# --- 3. Die beiden echten Aufgaben richtigstellen --------------------------
print("")
print("=" * 78)
print("ECHTE AUFGABEN, DIE NUR FALSCH AUSSAHEN")
print("=" * 78)

# 1292 hat eine von Hand gebaute Brainstorming-Tabelle - kein Automat.
# Nur der doppelte Emoji im Namen stammt von der Regel.
t = Task.browse(1292).exists()
if t:
    neu = t.name.replace("\U0001F4A1 \U0001F4A1", "\U0001F4A1", 1)
    if neu != t.name:
        t.write({'name': neu})
        print("  #1292 umbenannt: %s" % neu)
    print("        bleibt - enthaelt eine von Hand angelegte Brainstorming-Tabelle")

# 1244 ist ein echtes Original (kein Zwilling im Bestand), steht aber auf
# "In Arbeit", obwohl die Beschreibung sagt: wartet auf Kontofreigabe.
t = Task.browse(1244).exists()
if t and t.stage_id.id == 3:
    t.write({'stage_id': 5})
    print("  #1244 auf 'Blockiert' gesetzt (wartet laut Beschreibung auf Kontofreigabe)")

# --- 4. Projekt 109 archivieren -------------------------------------------
print("")
print("=" * 78)
print("PROJEKT 109")
print("=" * 78)
p = env['project.project'].with_context(active_test=False).browse(109).exists()
if p:
    rest = Task.search_count([('project_id', '=', 109)])
    print("  '%s' - verbleibende aktive Aufgaben: %d" % (p.name, rest))
    if p.active and rest == 0:
        p.write({'active': False})
        print("  archiviert.")
    elif not p.active:
        print("  war bereits archiviert.")
    else:
        print("  NICHT archiviert - es liegen noch %d aktive Aufgaben darin." % rest)

# --- 5. Kontrollzahlen -----------------------------------------------------
print("")
print("=" * 78)
print("NACHHER")
print("=" * 78)
offen_nachher = Task.search_count([('stage_id', 'not in', (6, 35))])
arbeit_nachher = Task.search_count([('stage_id', '=', 3)])
print("  offene Aufgaben gesamt: %d   (vorher %d, Differenz %d)"
      % (offen_nachher, offen_vorher, offen_vorher - offen_nachher))
print("  davon 'In Arbeit':      %d   (vorher %d, Differenz %d)"
      % (arbeit_nachher, arbeit_vorher, arbeit_vorher - arbeit_nachher))
print("  erwartete Differenz:    %d archivierte Kopien" % len(archiviert))

# --- 6. Automatik-Regeln durchsehen ---------------------------------------
print("")
print("=" * 78)
print("AKTIVE AUTOMATIK-REGELN (Regel 3: jaehrlich durchsehen)")
print("=" * 78)
for r in env['base.automation'].search([], order='id'):
    print("  [%s] #%-4s %-46s %s"
          % ("aktiv" if r.active else "  aus", r.id, r.name[:46], r.trigger))

env.cr.commit()
print("")
print("Festgeschrieben.")
