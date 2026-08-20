# Ansible-Grundlinie — Betriebsanleitung

Verwaltet die Host-Betriebssystem-Grundlinie (SSH-Härtung, Firewall,
Autostart der Gäste, automatische Sicherheits-Updates, fail2ban, und —
nur `anker-pve` — Kernel-Panic-Auto-Reboot) für beide Proxmox-Server
`stock-pve` und `anker-pve`. Keine Anwendungs-Deployments (Odoo,
AzuraCast, Docker-Compose-Stacks) — das ist bewusst außerhalb des
Umfangs, siehe `DOCS/superpowers/specs/2026-08-19-ansible-baseline-design.md`.

## Voraussetzungen

1. **`ansible/.vault_pass`** muss lokal existieren (gitignored, liegt
   NICHT im Repo). Das ist das Ansible-Vault-Master-Passwort — von Wolf
   erfragen bzw. aus Vaultwarden holen. Vorlage: `.vault_pass.example`
   im Repo-Root (nach `ansible/.vault_pass` kopieren, echtes Passwort
   eintragen, `chmod 600`).
2. **Beide Hosts müssen bereits in `known_hosts` des Control-Nodes
   stehen** — `ansible.cfg` hat `host_key_checking = True`, ein Lauf
   gegen einen unbekannten Host-Key bricht sonst ab (das ist Absicht,
   kein Bug).
3. **`ansible.posix`-Collection installieren** (wird von
   `autoheal_anker`s `sysctl`-Task gebraucht):
   ```
   ansible-galaxy collection install -r ansible/requirements.yml
   ```

## Windows-Control-Node-Falle: WSL/DrvFs

Wird dieses Repo auf einem Windows-Rechner unter einem
Windows-gemounteten Pfad ausgecheckt (z. B. `/mnt/c/Users/...`), ignoriert
Ansible `ansible.cfg` stillschweigend — DrvFs meldet solche Verzeichnisse
als "world writable", und Ansible verweigert dort das Einlesen der
Config-Datei ohne Fehlermeldung, die auf die wahre Ursache hinweist
(Symptome: falsche Inventory, `roles_path` nicht gefunden, Vault-Passwort
nicht gefunden — obwohl `ansible.cfg` alles korrekt konfiguriert).

**Workaround:** vor jedem echten `ansible-playbook`/`ansible-inventory`-Lauf
`ansible/`, `ansible.cfg` und `ansible/.vault_pass` in einen nativen
WSL-Pfad kopieren (z. B. `/root/frawo-ansible-run/`) und von dort aus
laufen lassen:

```bash
mkdir -p /root/frawo-ansible-run
cp -r /mnt/c/.../FraWo/ansible /root/frawo-ansible-run/
cp /mnt/c/.../FraWo/ansible.cfg /root/frawo-ansible-run/
cd /root/frawo-ansible-run
ansible-playbook ansible/playbooks/baseline.yml --syntax-check
# ... danach die temporäre Kopie wieder aufräumen
```

## Ablauf (Pflichtreihenfolge, nie überspringen)

1. `--syntax-check`
2. `--check --diff --limit <host>` (Probe-Modus, ändert nichts am
   Server, zeigt nur was sich ändern würde)
3. Diff von einem Menschen durchsehen lassen (nicht blind weiterlaufen)
4. Echter Lauf (ohne `--check`)
5. Sofort danach denselben Lauf nochmal ausführen, um Idempotenz zu
   bestätigen — erwartet: `changed=0` bei allen Tasks, **außer** der
   `autostart_guests`-Start-Reihenfolge-Task (`-startup order=...`),
   die auf Hosts mit `order:` in `host_vars` per Design immer
   `changed_when: true` meldet (dokumentierte, akzeptierte Ausnahme,
   kein echter Idempotenz-Verstoß — der zugrundeliegende `pct`/`qm
   set`-Befehl selbst ist idempotent).

Immer erst gegen `anker-pve` (geringeres Risiko, kein Live-Publikum),
danach erst gegen `stock-pve` (dort laufen Radio/Odoo/Website live).

## Kompletten Lauf ausführen

```bash
ansible-playbook ansible/playbooks/baseline.yml --limit <stock-pve|anker-pve>
```

(`--check --diff` anhängen für den Probe-Modus aus Schritt 2 oben.)

## Struktur

- `inventory/hosts.yml` — 2 Hosts, Gruppe `pve_hosts`
- `inventory/group_vars/all/` — gemeinsame Variablen (`main.yml`) und
  verschlüsselte Geheimnisse (`vault.yml`)
- `inventory/host_vars/{stock-pve,anker-pve}.yml` — hostspezifische
  Variablen, u. a. die `guests:`-Liste für `autostart_guests`
- `playbooks/baseline.yml` — ruft alle Rollen für beide Hosts auf, plus
  `autoheal_anker` nur für `anker-pve`
- `roles/` — `ssh_hardening`, `firewall_baseline`, `autostart_guests`,
  `unattended_updates`, `fail2ban`, `autoheal_anker`
