# --- 5. Proxmox Backup Server (VM241 OptiPlex, seit 24.09.2026, Odoo #1462) --
# Nicht nur "Speicher aktiv": jeder laufende Gast im Verbund (ausser 240 alter PBS,
# 241 PBS selbst, 990 Test-VM) braucht eine PBS-Sicherung juenger als 26 h.
# Fehlende Gaeste werden mit Namen gemeldet. Jeder Fehler (PBS weg, pvesm haengt) = durchgefallen.
PBS_FEHLT=$(timeout "$TIMEOUT_REMOTE" python3 - <<'PYEOF' 2>&1 | tail -1
import json, socket, subprocess, time
AUS = {240, 241, 990}
def j(cmd):
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
res = j(["pvesh", "get", "/cluster/resources", "--type", "vm", "--output-format", "json"])
laufend = {r["vmid"]: r.get("name", "") for r in res if r.get("status") == "running" and r["vmid"] not in AUS}
jung = {}
for b in j(["pvesh", "get", "/nodes/" + socket.gethostname() + "/storage/pbs/content", "--output-format", "json"]):
    v = int(b.get("vmid") or 0)
    jung[v] = max(jung.get(v, 0), int(b.get("ctime") or 0))
grenze = time.time() - 26 * 3600
fehlt = ["%d %s" % (v, n) for v, n in sorted(laufend.items()) if jung.get(v, 0) < grenze]
print(("FEHLT " + ", ".join(fehlt)) if fehlt else ("OK %d" % len(laufend)))
PYEOF
)
case "$PBS_FEHLT" in
    "OK "*) pruefe "pbs_datastore" 1 "PBS 10.1.0.8: alle ${PBS_FEHLT#OK } laufenden Gaeste juenger als 26 h gesichert" ;;
    *)      pruefe "pbs_datastore" 0 "PBS 10.1.0.8: ${PBS_FEHLT:0:300}" ;;
esac
