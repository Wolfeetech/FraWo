#!/bin/bash
# FraWo · Prueft die Firewall-Regeln am Gateway gegen die Wirklichkeit
#
# Entstanden am 21.09.2026: Die Regel "Block IoT to Server" zeigte monatelang
# auf VLAN 101 - ein Netz, in dem kein Dienst mehr steckte. Die Netztrennung
# war damit wirkungslos, ohne dass irgendwer etwas gemerkt haette.
#
# Diese Pruefung findet genau solche Regeln. Sie braucht keine KI und kein
# Kontingent - sie misst. Aufgabe M5 aus Vorhaben "Netz professionell
# betreibbar machen" (Odoo #1523).
#
# Aufruf:  frawo-firewall-pruefen.sh            Klartext
#          frawo-firewall-pruefen.sh --kurz     nur Befunde, fuer Cron
#
# Rueckgabewert: 0 = alles in Ordnung, 1 = Befunde vorhanden

set -u
GW=10.1.0.1
KEY="${FRAWO_UNIFI_KEY:-}"
KURZ=0
[ "${1:-}" = "--kurz" ] && KURZ=1

if [ -z "$KEY" ]; then
    echo "FEHLER: Schluessel fehlt. Setzen mit:  export FRAWO_UNIFI_KEY=<schluessel aus Vaultwarden>"
    exit 2
fi

API="https://${GW}/proxy/network/api/s/default"
hole() { curl -s -k -m 25 -H "X-API-KEY: ${KEY}" "${API}/$1" 2>/dev/null; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
hole rest/firewallrule  > "$TMP/regeln.json"
hole rest/firewallgroup > "$TMP/gruppen.json"
hole rest/networkconf   > "$TMP/netze.json"
hole stat/sta           > "$TMP/geraete.json"

if [ ! -s "$TMP/regeln.json" ]; then
    echo "FEHLER: Gateway ${GW} antwortet nicht."
    exit 2
fi

FRAWO_KURZ="$KURZ" python3 - "$TMP" <<'PYEOF'
import json, os, sys, collections

d = sys.argv[1]
kurz = os.environ.get("FRAWO_KURZ") == "1"
lade = lambda n: json.load(open(f"{d}/{n}.json", encoding="utf-8")).get("data", [])

regeln, gruppen, netze, geraete = lade("regeln"), lade("gruppen"), lade("netze"), lade("geraete")

netz_name = {n["_id"]: n.get("name") for n in netze}
gruppe_by_id = {g["_id"]: g for g in gruppen}

# Wie viele Geraete stecken tatsaechlich in welchem Netz?
belegung = collections.Counter()
for g in geraete:
    if g.get("network_id"):
        belegung[g["network_id"]] += 1

# Ein leeres Netz ist nur dann ein Fehler, wenn dort auch etwas SEIN SOLL.
# "Anker-Guest" ohne Gaeste ist normal. "Anker-Server" ohne Server nicht.
# Merkmal: gibt es feste Zuteilungen, die auf dieses Netz zeigen?
erwartet = collections.Counter()
for g in geraete:
    if g.get("use_fixedip") and g.get("network_id"):
        erwartet[g["network_id"]] += 1
for g in gruppen:
    pass  # Gruppen tragen keine Netz-Zuordnung

def soll_belegt_sein(n):
    """Netz, fuer das Reservierungen bestehen, muss auch Geraete haben."""
    return erwartet.get(n, 0) > 0

befunde = []
def melde(schwere, text, beleg=""):
    befunde.append((schwere, text, beleg))

def nid(r, seite):
    return r.get(f"{seite}_networkconf_id")

# ── 1. Regeln, die auf ein leeres Netz zeigen ────────────────────────
# Das ist der Fehler vom 21.09.2026: die Regel existiert, wirkt aber nicht.
gemeldete_netze = set()
for r in regeln:
    if not r.get("enabled"):
        continue
    for seite in ("src", "dst"):
        n = nid(r, seite)
        if not n or belegung.get(n, 0) > 0:
            continue
        if not soll_belegt_sein(n):
            continue          # leeres Gaeste-/DMZ-Netz ist kein Fehler
        if n in gemeldete_netze:
            continue          # je Netz nur einmal melden, nicht je Regel
        gemeldete_netze.add(n)
        betroffen = [x.get("name") for x in regeln
                     if x.get("enabled") and n in (nid(x, "src"), nid(x, "dst"))]
        melde("KRITISCH",
              f'Das Netz "{netz_name.get(n, n)}" hat feste Zuteilungen, aber kein '
              f'einziges Geraet steckt darin. {len(betroffen)} Firewall-Regel(n) '
              f'zeigen darauf und wirken damit ins Leere.',
              "betroffen: " + ", ".join(str(b)[:28] for b in betroffen[:5]))

# ── 2. Reihenfolge: steht eine Ausnahme HINTER ihrer Sperre? ─────────
lan = sorted([r for r in regeln if r.get("ruleset") == "LAN_IN" and r.get("enabled")],
             key=lambda x: int(str(x.get("rule_index", 0)) or 0))
sperren = [r for r in lan if r.get("action") == "drop"]
for r in lan:
    if r.get("action") != "accept":
        continue
    ridx = int(str(r.get("rule_index", 0)) or 0)
    quelle = r.get("src_address") or ""
    if not quelle:
        continue
    # Ziele der Ausnahme sammeln
    ziele_a = set()
    if r.get("dst_address"):
        ziele_a.add(r["dst_address"])
    for gid in (r.get("dst_firewallgroup_ids") or []):
        gg = gruppe_by_id.get(gid)
        if gg:
            ziele_a.update(gg.get("group_members") or [])

    for s in sperren:
        sidx = int(str(s.get("rule_index", 0)) or 0)
        if sidx >= ridx:
            continue
        # Ziele der Sperre sammeln
        ziele_s = set()
        if s.get("dst_address"):
            ziele_s.add(s["dst_address"])
        for gid in (s.get("dst_firewallgroup_ids") or []):
            gg = gruppe_by_id.get(gid)
            if gg:
                ziele_s.update(gg.get("group_members") or [])
        # Nur melden, wenn die Sperre die Ausnahme ueberhaupt treffen KANN:
        # gleiche Quelle UND ueberlappendes Ziel.
        if not (ziele_a & ziele_s):
            continue
        melde("KRITISCH",
              f'Die Ausnahme "{r.get("name")}" (Index {ridx}) steht HINTER der '
              f'Sperre "{s.get("name")}" (Index {sidx}) und greift deshalb nie.',
              f'Quelle {quelle}, ueberlappendes Ziel: {", ".join(sorted(ziele_a & ziele_s))}')

# ── 3. Sperrt eine Regel etwas, das die Geraete zum Leben brauchen? ──
# Der klassische stille Ausfall: DNS oder Zeitserver mitgesperrt.
gesperrt = set()
for r in regeln:
    if r.get("action") != "drop" or not r.get("enabled"):
        continue
    for gid in (r.get("dst_firewallgroup_ids") or []):
        g = gruppe_by_id.get(gid)
        if g and g.get("group_type") == "address-group":
            gesperrt.update(g.get("group_members") or [])
    if r.get("dst_address"):
        gesperrt.add(r["dst_address"])

for n in netze:
    if n.get("purpose") == "wan":
        continue
    for i in (1, 2, 3, 4):
        srv = n.get(f"dhcpd_dns_{i}")
        if srv and srv in gesperrt:
            melde("KRITISCH",
                  f'Das Netz "{n.get("name")}" bekommt {srv} als Namensserver zugeteilt — '
                  f'diese Adresse ist aber gesperrt. Die Geraete dort verlieren lautlos '
                  f'die Namensaufloesung.',
                  f'dhcpd_dns_{i}')

# ── 4. Gesperrte Adressen, die es gar nicht mehr gibt ────────────────
# "Online" heisst hier: das Gateway kennt die Adresse, ODER es gibt eine
# Reservierung dafuer. Ein Container, der laenger nicht gefunkt hat, faellt
# sonst faelschlich als tot auf.
lebende = {g.get("ip") for g in geraete if g.get("ip")}
lebende |= {g.get("fixed_ip") for g in geraete if g.get("fixed_ip")}
for g in gruppen:
    if g.get("group_type") != "address-group":
        continue
    tot = [m for m in (g.get("group_members") or [])
           if "/" not in m and m not in lebende]
    if tot:
        melde("HINWEIS",
              f'Adressgruppe "{g.get("name")}" enthaelt {len(tot)} Adresse(n) '
              f'ohne bekanntes Geraet und ohne Reservierung.',
              ", ".join(tot[:6]))

# ── 5. Feste Zuteilungen, die ins falsche Netz zeigen ────────────────
# Genau daran sind am 21.09. alle Adressen gewandert.
for g in geraete:
    ip, fix = g.get("ip"), g.get("fixed_ip")
    if g.get("use_fixedip") and ip and fix and ip != fix:
        melde("KRITISCH",
              f'Geraet "{g.get("name") or g.get("hostname") or g.get("mac")}" hat '
              f'{ip}, reserviert ist aber {fix}. Die Reservierung greift nicht — '
              f'die Adresse wandert beim naechsten Neustart.',
              f'MAC {g.get("mac")}')

# ── Ausgabe ──────────────────────────────────────────────────────────
krit = [b for b in befunde if b[0] == "KRITISCH"]
hinw = [b for b in befunde if b[0] == "HINWEIS"]

if not kurz:
    print("=" * 74)
    print("FraWo · Firewall-Pruefung gegen die Wirklichkeit")
    print("=" * 74)
    print(f"  Regeln geprueft:      {len([r for r in regeln if r.get('enabled')])}")
    print(f"  Netze:                {len([n for n in netze if n.get('purpose') != 'wan'])}")
    print(f"  Geraete online:       {len(geraete)}")
    print()

if krit:
    print(f"🔴 {len(krit)} kritische(r) Befund(e):\n")
    for _, t, b in krit:
        print(f"  • {t}")
        if b:
            print(f"    ({b})")
        print()

if hinw and not kurz:
    print(f"⚠️  {len(hinw)} Hinweis(e):\n")
    for _, t, b in hinw:
        print(f"  • {t}")
        if b:
            print(f"    ({b})")
        print()

if not befunde:
    print("✅ Keine Befunde. Jede aktive Regel zeigt auf ein Netz, in dem auch "
          "Geraete stecken, und keine Reservierung widerspricht der Wirklichkeit.")

sys.exit(1 if krit else 0)
PYEOF
