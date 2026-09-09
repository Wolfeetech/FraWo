# -*- coding: utf-8 -*-
# Gespeicherte Arbeitsansichten fuer Odoo, 08.09.2026.
#
# WARUM
# Die abgeschaltete Automatik-Regel 16 hat versucht, "alle Anschaffungen an
# einem Ort" zu zeigen - indem sie Kopien anlegte. Das ist der falsche Weg:
# eine Kopie ist eine zweite Wahrheit, die sofort auseinanderlaeuft.
#
# Ein gespeicherter Filter leistet dasselbe und hat keinen dieser Nachteile.
# Er zeigt IMMER den aktuellen Stand, er kann nichts kaputt machen, und wenn
# er nicht mehr passt, loescht man ihn ohne Datenverlust.
#
# Diese Ansichten beantworten genau die fuenf Fragen aus Regel 7 der
# Sicherheitsstandards (DOCS/SICHERHEITSSTANDARDS.md) plus zwei Pruefblicke
# auf die Qualitaet des Bestands.
#
# Die Filter werden ohne Benutzer angelegt (user_id = False) und sind damit
# fuer alle sichtbar. Bereits vorhandene gleichen Namens werden aktualisiert,
# nicht verdoppelt.
#
# Laeuft in der Odoo-Shell auf CT140.

import datetime
import time
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval

# Dieselben Namen, die Odoo beim Auswerten eines Filter-Domains bereitstellt.
def context_today():
    return datetime.date.today()


ERLEDIGT = "(6, 35)"          # Erledigt, Abgebrochen
TAG_WOLF = 153                # 🙋 braucht Wolf
TAG_KAUF = 147                # 🛒 Anschaffung
TAG_FRIST = 133               # 💰 Forderung / Frist
STUFE_ARBEIT = 3              # 🚀 In Arbeit

ANSICHTEN = [
    # --- Die fuenf Fragen des Tagesberichts ---------------------------------
    {
        'name': "🙋 Braucht eine Entscheidung von Wolf",
        'domain': "[('tag_ids', 'in', [%d]), ('stage_id', 'not in', %s)]"
                  % (TAG_WOLF, ERLEDIGT),
        'context': "{'group_by': ['project_id']}",
    },
    {
        'name': "⏰ Überfällig",
        'domain': "[('date_deadline', '<', context_today().strftime('%Y-%m-%d')),"
                  " ('stage_id', 'not in', " + ERLEDIGT + ")]",
        'context': "{'group_by': ['project_id'], 'order': 'date_deadline asc'}",
    },
    {
        'name': "📅 Fällig in den nächsten 7 Tagen",
        'domain': "['&', '&',"
                  " ('date_deadline', '>=', context_today().strftime('%Y-%m-%d')),"
                  " ('date_deadline', '<=', (context_today() +"
                  " relativedelta(days=7)).strftime('%Y-%m-%d')),"
                  " ('stage_id', 'not in', " + ERLEDIGT + ")]",
        'context': "{'group_by': ['project_id']}",
    },
    {
        'name': "🚀 Läuft gerade (WIP)",
        'domain': "[('stage_id', '=', %d)]" % STUFE_ARBEIT,
        'context': "{'group_by': ['user_ids']}",
    },
    {
        'name': "🕸️ Liegengeblieben — seit 14 Tagen keine Bewegung",
        'domain': "[('stage_id', '=', %d),"
                  " ('write_date', '<', (datetime.datetime.now() -"
                  " datetime.timedelta(days=14)).strftime('%%Y-%%m-%%d %%H:%%M:%%S'))]"
                  % STUFE_ARBEIT,
        'context': "{'group_by': ['project_id']}",
    },

    # --- Ersetzt die abgeschaltete Duplizier-Regel --------------------------
    {
        'name': "🛒 Alle Anschaffungen (ersetzt Projekt 109)",
        'domain': "[('tag_ids', 'in', [%d]), ('stage_id', 'not in', %s)]"
                  % (TAG_KAUF, ERLEDIGT),
        'context': "{'group_by': ['project_id']}",
    },
    {
        'name': "💰 Forderungen & Fristen",
        'domain': "[('tag_ids', 'in', [%d]), ('stage_id', 'not in', %s)]"
                  % (TAG_FRIST, ERLEDIGT),
        'context': "{'group_by': ['project_id'], 'order': 'date_deadline asc'}",
    },

    # --- Qualitaet des Bestands --------------------------------------------
    {
        'name': "📭 Ohne Beschreibung — unbrauchbar für andere",
        'domain': "['&', ('stage_id', 'not in', " + ERLEDIGT + "),"
                  " '|', ('description', '=', False),"
                  " ('description', 'in', ['', '<p><br></p>'])]",
        'context': "{'group_by': ['project_id']}",
    },
    {
        'name': "🎯 Offen ohne Frist",
        'domain': "[('date_deadline', '=', False),"
                  " ('stage_id', 'not in', " + ERLEDIGT + ")]",
        'context': "{'group_by': ['project_id']}",
    },
]

Filter = env['ir.filters']
modell = 'project.task'

print("=" * 78)
print("ARBEITSANSICHTEN")
print("=" * 78)

for a in ANSICHTEN:
    werte = {
        'name': a['name'],
        'model_id': modell,
        'domain': a['domain'],
        'context': a['context'],
        # Odoo 19: aus user_id (many2one) wurde user_ids (many2many).
        # Leere Liste = fuer alle sichtbar. 'sort' ist Pflichtfeld.
        'user_ids': [(6, 0, [])],
        'sort': '[]',
        'action_id': False,     # in jeder Aufgaben-Ansicht verfuegbar
        'is_default': False,
    }
    vorhanden = Filter.search([
        ('name', '=', a['name']), ('model_id', '=', modell)], limit=1)
    if vorhanden:
        vorhanden.write(werte)
        zustand = "aktualisiert"
    else:
        Filter.create(werte)
        zustand = "angelegt"

    # Gegenpruefen - aber das Richtige.
    #
    # Die erste Fassung rief safe_eval mit dem Python-Modul datetime auf und
    # meldete fuer JEDEN Filter "NICHT AUSWERTBAR". Zwei Fehler in einem:
    # safe_eval nimmt keine rohen Module, UND Domains mit context_today()
    # wertet ohnehin die Weboberflaeche aus, nicht Python. Die Pruefung hat
    # also das Falsche getestet und dann auch noch falsch gemeldet - die
    # Filter selbst waren die ganze Zeit in Ordnung.
    #
    # Jetzt: Struktur pruefen (kann echt scheitern) und, wo kein Datum im
    # Spiel ist, die Treffer wirklich zaehlen.
    try:
        geparst = ast.literal_eval(a['domain'])
        if not isinstance(geparst, list):
            raise ValueError('kein Domain-Ausdruck')
        pruefung = "%d Treffer" % env[modell].search_count(geparst)
    except (ValueError, SyntaxError):
        # Enthaelt context_today()/datetime - von der Weboberflaeche
        # ausgewertet. Hier nur die Klammerstruktur pruefen.
        d = a['domain']
        if d.count('(') == d.count(')') and d.count('[') == d.count(']')                 and d.strip().startswith('[') and d.strip().endswith(']'):
            pruefung = "Datumsfilter, Struktur ok"
        else:
            pruefung = "!! KLAMMERN STIMMEN NICHT"
    except Exception as e:
        pruefung = "!! %s" % str(e)[:52]

    print("  %-12s %-50s %s" % (zustand, a['name'][:50], pruefung))

env.cr.commit()
print("")
print("Festgeschrieben. Sichtbar in Odoo unter Projekt → Aufgaben → Favoriten.")
