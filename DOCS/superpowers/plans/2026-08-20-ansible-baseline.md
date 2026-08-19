# Ansible-Grundlinie Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Den sicheren Grundzustand beider Proxmox-Server (SSH-Härtung, Firewall, Autostart der Gäste, automatische Sicherheits-Updates, fail2ban, Anker-Absturzwächter) als Ansible-Rollen festhalten, damit er nicht mehr lautlos abweichen kann.

**Architecture:** Ein `ansible/`-Baum mit Inventory (2 Hosts: `stock-pve`, `anker-pve`), sechs kleinen, unabhängig testbaren Rollen, und einem `baseline.yml`-Playbook, das die Rollen den richtigen Hosts zuordnet. Geheimnisse liegen verschlüsselt (`ansible-vault`) in `group_vars/all/vault.yml`.

**Tech Stack:** Ansible (Control-Node = StudioPC), Ziel-Betriebssystem Debian/Proxmox VE auf beiden Hosts, SSH-Key-Auth (bereits vorhanden in `~/.ssh/config`).

**Spec:** `DOCS/superpowers/specs/2026-08-19-ansible-baseline-design.md`

## Global Constraints

- Keine Passwörter/Secrets im Klartext committen — nur über `ansible-vault` verschlüsselt (aus dem heutigen Audit: das war die Wurzel des größten Funds).
- Jede Rolle muss idempotent sein: ein zweiter echter Lauf ohne Änderungen dazwischen muss `changed=0` zeigen.
- Immer erst `--check --diff` (Probe-Modus), dann echter Lauf — nie direkt scharf schalten.
- Immer erst gegen `anker-pve` testen, erst danach gegen `stock-pve` (dort läuft Live-Radio/Odoo/Website).
- Diese Etappe verwaltet nur die Host-Betriebssystem-Ebene, keine Anwendungs-Deployments (Odoo, AzuraCast, Docker-Compose-Inhalte).

---

## Task 1: Altes Ansible archivieren, neue Struktur + Inventory anlegen

**Files:**
- Create: `archive/ansible-homeserver2027/` (Ziel für den Umzug)
- Modify: `ansible/` (aufräumen, siehe Schritte)
- Create: `ansible/inventory/hosts.yml`
- Create: `ansible/inventory/group_vars/all.yml`
- Create: `ansible/inventory/host_vars/stock-pve.yml`
- Create: `ansible/inventory/host_vars/anker-pve.yml`
- Modify: `ansible.cfg` (Repo-Root, bereits vorhanden)

**Interfaces:**
- Produces: Inventory-Gruppen `all`, `pve_hosts` (beide Server), nutzbar von allen folgenden Rollen über `hosts: pve_hosts` bzw. `hosts: anker-pve`.

- [ ] **Step 1: Alten Ansible-Baum verschieben**

```bash
mkdir -p archive/ansible-homeserver2027
git mv ansible archive/ansible-homeserver2027/ansible
git mv ansible.cfg archive/ansible-homeserver2027/ansible.cfg.old
```

- [ ] **Step 2: Neue Verzeichnisstruktur anlegen**

```bash
mkdir -p ansible/inventory/group_vars/all
mkdir -p ansible/inventory/host_vars
mkdir -p ansible/playbooks
mkdir -p ansible/roles
```

- [ ] **Step 3: Inventory schreiben**

`ansible/inventory/hosts.yml`:
```yaml
all:
  children:
    pve_hosts:
      hosts:
        stock-pve:
        anker-pve:
```

`ansible/inventory/host_vars/stock-pve.yml`:
```yaml
ansible_host: 100.91.20.116
ansible_user: root
ansible_ssh_private_key_file: ~/.ssh/id_ed25519
is_anker: false
```

`ansible/inventory/host_vars/anker-pve.yml`:
```yaml
ansible_host: 10.1.0.92
ansible_user: root
ansible_ssh_private_key_file: ~/.ssh/pve_ed25519
is_anker: true
```

`ansible/inventory/group_vars/all.yml`:
```yaml
ansible_python_interpreter: auto_silent
```

- [ ] **Step 4: `ansible.cfg` neu anlegen (Repo-Root)**

```ini
[defaults]
inventory = ansible/inventory/hosts.yml
interpreter_python = auto_silent
retry_files_enabled = False
vault_password_file = ansible/.vault_pass
host_key_checking = True

[ssh_connection]
pipelining = True
```

- [ ] **Step 5: Testen — Inventory ist gültig und erreicht beide Hosts**

Run: `ansible-inventory --list`
Expected: JSON-Ausgabe zeigt `stock-pve` und `anker-pve` unter `pve_hosts` mit den richtigen `ansible_host`-Werten, kein Fehler.

Run: `ansible pve_hosts -m ping`
Expected: Beide Hosts antworten `"ping": "pong"` (SUCCESS), kein `UNREACHABLE`.

- [ ] **Step 6: Commit**

```bash
git add archive/ansible-homeserver2027 ansible ansible.cfg
git commit -m "chore: alte Ansible-Struktur archiviert, neue Grundlage angelegt"
```

---

## Task 2: Vault für Geheimnisse einrichten

**Files:**
- Create: `ansible/inventory/group_vars/all/vault.yml` (verschlüsselt)
- Modify: `.gitignore` (Vault-Passwort-Datei ausschließen)

**Interfaces:**
- Consumes: nichts
- Produces: Variable `vault_prodesk_root_password`, `vault_anker_root_password` — nutzbar (aber in dieser Etappe von keiner Rolle zwingend gebraucht, da SSH bereits Key-only ist; die Variablen stehen für spätere Rollen bereit, die sie brauchen).

- [ ] **Step 1: Vault-Passwort lokal erzeugen (NICHT ins Repo)**

```bash
openssl rand -base64 24 > ansible/.vault_pass
echo "ansible/.vault_pass" >> .gitignore
```

- [ ] **Step 2: Verschlüsselte Vault-Datei anlegen**

```bash
ansible-vault create ansible/inventory/group_vars/all/vault.yml
```

Inhalt (im Editor, der sich öffnet):
```yaml
vault_prodesk_root_password: "JsEh9LLr5UowqzY2RKoW"
vault_anker_root_password: "wFOHTHVEIE0VxAVI0MSo"
```

- [ ] **Step 3: Testen — Vault ist wirklich verschlüsselt und entschlüsselbar**

Run: `cat ansible/inventory/group_vars/all/vault.yml`
Expected: Beginnt mit `$ANSIBLE_VAULT;1.1;AES256` — kein Klartext-Passwort lesbar.

Run: `ansible-vault view ansible/inventory/group_vars/all/vault.yml`
Expected: Zeigt den Klartext-Inhalt von Schritt 2 korrekt an (Passwort-Datei wird automatisch über `ansible.cfg` gefunden).

- [ ] **Step 4: Vault-Passwort an Wolf übergeben**

Inhalt von `ansible/.vault_pass` ausgeben und Wolf explizit mitteilen, er soll es in Vaultwarden ablegen (eigener Eintrag "Ansible Vault Master-Passwort"). Diese Datei existiert nur lokal auf StudioPC, nicht im Repo.

- [ ] **Step 5: Commit (nur die verschlüsselte Datei + .gitignore, NICHT .vault_pass)**

```bash
git status --short   # sicherstellen: ansible/.vault_pass taucht NICHT als "??" oder "A" auf
git add ansible/inventory/group_vars/all/vault.yml .gitignore
git commit -m "feat: ansible-vault fuer Geheimnisse eingerichtet"
```

---

## Task 3: Rolle `ssh_hardening`

**Files:**
- Create: `ansible/roles/ssh_hardening/tasks/main.yml`
- Create: `ansible/roles/ssh_hardening/handlers/main.yml`

**Interfaces:**
- Consumes: nichts
- Produces: Handler `restart sshd`, wiederverwendbar von späteren Rollen falls nötig.

- [ ] **Step 1: Tasks schreiben**

`ansible/roles/ssh_hardening/tasks/main.yml`:
```yaml
---
- name: Sicherstellen, dass Passwort-Anmeldung per SSH aus ist
  ansible.builtin.lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?PasswordAuthentication\s'
    line: 'PasswordAuthentication no'
    validate: 'sshd -t -f %s'
  notify: restart sshd

- name: Sicherstellen, dass Root nur per Schluessel darf
  ansible.builtin.lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?PermitRootLogin\s'
    line: 'PermitRootLogin prohibit-password'
    validate: 'sshd -t -f %s'
  notify: restart sshd

- name: Sicherstellen, dass Schluessel-Anmeldung aktiv ist
  ansible.builtin.lineinfile:
    path: /etc/ssh/sshd_config
    regexp: '^#?PubkeyAuthentication\s'
    line: 'PubkeyAuthentication yes'
    validate: 'sshd -t -f %s'
  notify: restart sshd
```

- [ ] **Step 2: Handler schreiben**

`ansible/roles/ssh_hardening/handlers/main.yml`:
```yaml
---
- name: restart sshd
  ansible.builtin.service:
    name: ssh
    state: restarted
```

- [ ] **Step 3: Testen — Syntax**

Run: `ansible-playbook --syntax-check -e "role_test=ssh_hardening" ansible/playbooks/baseline.yml` (nach Task 9 verfuegbar — bis dahin ersatzweise: `ansible-lint ansible/roles/ssh_hardening/` falls installiert, sonst Schritt hier nur vormerken und in Task 9 gesamthaft pruefen)

- [ ] **Step 4: Commit**

```bash
git add ansible/roles/ssh_hardening
git commit -m "feat: Rolle ssh_hardening"
```

---

## Task 4: Rolle `firewall_baseline`

**Files:**
- Create: `ansible/roles/firewall_baseline/tasks/main.yml`
- Create: `ansible/roles/firewall_baseline/files/stock-pve.cluster.fw`
- Create: `ansible/roles/firewall_baseline/files/anker-pve.cluster.fw`

**Interfaces:**
- Consumes: `is_anker` aus host_vars (Task 1)
- Produces: nichts, was andere Rollen brauchen

Die Regeln werden 1:1 als heutiger IST-Zustand übernommen (kein Umbau — Regeln aendern ist ein eigener, spaeterer Schritt, siehe Spec "Nicht in dieser Version"). Das verhindert nur, dass sie sich still veraendern.

- [ ] **Step 1: Aktuellen Zustand als Vorlage ablegen**

`ansible/roles/firewall_baseline/files/stock-pve.cluster.fw`:
```
[OPTIONS]

enable: 1

[RULES]
IN ACCEPT -source 100.64.0.0/10 -log nolog
```

`ansible/roles/firewall_baseline/files/anker-pve.cluster.fw`:
```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT

[RULES]
# --- Management Networks (alle Ports erlaubt) ---
IN ACCEPT -source 100.64.0.0/10 -log nolog            # Tailscale (alle Services)
IN ACCEPT -source 10.1.0.0/24 -log nolog            # Server-VLAN101 Rothkreuz (StudioPC, ProDesk, Odoo)
IN ACCEPT -source 10.4.0.0/24 -log nolog               # CT/VM-Netz (NFS, Monitoring, SSH)

# --- Lokale LANs (nur kritische Ports) ---
IN ACCEPT -source 192.168.2.0/24 -p tcp -dport 22 -log nolog   # Rothkreuz LAN: SSH
IN ACCEPT -source 192.168.2.0/24 -p tcp -dport 8006 -log nolog # Rothkreuz LAN: PVE-UI
IN ACCEPT -source 192.168.178.0/24 -p tcp -dport 22 -log nolog   # Heim-LAN: SSH
IN ACCEPT -source 192.168.178.0/24 -p tcp -dport 8006 -log nolog # Heim-LAN: PVE-UI

# --- Immer erlaubt ---
IN ACCEPT -p icmp -log nolog                           # Ping / Diagnose
```

> ⚠️ Bekannter offener Punkt aus dem Audit vom 19.08.: die Anker-Regel
> `-source 10.1.0.0/24` erlaubt ALLE Ports, nicht nur die noetigen —
> das war die Ursache fuer die frei erreichbare Radio-Datenbank. Diese
> Rolle friert bewusst nur den JETZIGEN Zustand ein (Drift-Schutz).
> Das Einengen auf konkrete Ports ist ein eigener Folge-Schritt
> (braucht eine vollstaendige Liste, welche Ports von ProDesk/StudioPC
> aus wirklich gebraucht werden), keine Aufgabe dieses Plans.

- [ ] **Step 2: Task schreiben**

`ansible/roles/firewall_baseline/tasks/main.yml`:
```yaml
---
- name: Node-Firewall-Regeln aus der Vorlage bereitstellen (ProDesk)
  ansible.builtin.copy:
    src: stock-pve.cluster.fw
    dest: /etc/pve/firewall/cluster.fw
    owner: root
    group: www-data
    mode: "0640"
  when: not is_anker

- name: Node-Firewall-Regeln aus der Vorlage bereitstellen (Anker)
  ansible.builtin.copy:
    src: anker-pve.cluster.fw
    dest: /etc/pve/firewall/cluster.fw
    owner: root
    group: www-data
    mode: "0640"
  when: is_anker

- name: Sicherstellen, dass die Proxmox-Firewall wirklich laeuft
  ansible.builtin.command: pve-firewall status
  register: fw_status
  changed_when: false
  failed_when: "'enabled/running' not in fw_status.stdout"
```

- [ ] **Step 3: Commit**

```bash
git add ansible/roles/firewall_baseline
git commit -m "feat: Rolle firewall_baseline (IST-Zustand als Schutz vor Abweichung)"
```

---

## Task 5: Rolle `autostart_guests`

**Files:**
- Create: `ansible/roles/autostart_guests/tasks/main.yml`
- Modify: `ansible/inventory/host_vars/stock-pve.yml` (Gaesteliste ergaenzen)
- Modify: `ansible/inventory/host_vars/anker-pve.yml` (Gaesteliste ergaenzen)

Das ist die direkte Ursache des heutigen Ausfalls (7 von 9 ProDesk-Diensten kamen nach einem Neustart nicht von selbst hoch) — als Code festgehalten, damit es nicht wieder passiert.

**Interfaces:**
- Consumes: `guests` (neue Liste in host_vars)

- [ ] **Step 1: Gaesteliste in host_vars ergaenzen**

`ansible/inventory/host_vars/stock-pve.yml` (Ergaenzung):
```yaml
guests:
  - { id: 101, type: pct }
  - { id: 103, type: pct, order: 2 }
  - { id: 106, type: pct, order: 2 }
  - { id: 108, type: pct, order: 2 }
  - { id: 110, type: pct, order: 2, up: 30 }
  - { id: 120, type: pct, order: 1 }
  - { id: 121, type: pct, order: 2, up: 30 }
  - { id: 140, type: pct, order: 2 }
  - { id: 150, type: pct, order: 2 }
  - { id: 210, type: qm, order: 3 }
  - { id: 360, type: qm, order: 4 }
```

`ansible/inventory/host_vars/anker-pve.yml` (Ergaenzung):
```yaml
guests:
  - { id: 100, type: pct }
  - { id: 101, type: pct }
  - { id: 110, type: pct }
  - { id: 130, type: pct }
  - { id: 150, type: pct }
  - { id: 210, type: qm }
  - { id: 240, type: qm }
  - { id: 300, type: qm }
```

- [ ] **Step 2: Task schreiben**

`ansible/roles/autostart_guests/tasks/main.yml`:
```yaml
---
- name: Aktuellen onboot-Wert je Gast auslesen
  ansible.builtin.command: "{{ item.type }} config {{ item.id }}"
  loop: "{{ guests }}"
  loop_control:
    label: "{{ item.type }} {{ item.id }}"
  register: guest_config
  changed_when: false

- name: Autostart (onboot) setzen, falls noch nicht aktiv
  ansible.builtin.command: >
    {{ item.item.type }} set {{ item.item.id }} -onboot 1
  loop: "{{ guest_config.results }}"
  loop_control:
    label: "{{ item.item.type }} {{ item.item.id }}"
  when: "'onboot: 1' not in item.stdout"
  changed_when: true

- name: Start-Reihenfolge setzen, wo im Inventory angegeben
  ansible.builtin.command: >
    {{ item.type }} set {{ item.id }}
    -startup order={{ item.order }}{{ (',up=' + (item.up | string)) if item.up is defined else '' }}
  loop: "{{ guests }}"
  loop_control:
    label: "{{ item.type }} {{ item.id }}"
  when: item.order is defined
  changed_when: true
```

> Hinweis für die Umsetzung: der `changed_when` im letzten Task ist
> bewusst grob (immer `changed`), weil `pct/qm set -startup` keinen
> einfachen Vorher-Zustand zum Vergleichen zurückgibt. Das ist
> akzeptabel — der Befehl selbst ist idempotent (setzt immer denselben
> Zielwert), nur die Ansible-"changed"-Anzeige ist nicht perfekt exakt.
> Kein Blocker, nur eine bekannte Kleinigkeit für die Umsetzung.

- [ ] **Step 3: Commit**

```bash
git add ansible/roles/autostart_guests ansible/inventory/host_vars
git commit -m "feat: Rolle autostart_guests - Fix vom 19.08. als Code festgehalten"
```

---

## Task 6: Rolle `unattended_updates`

**Files:**
- Create: `ansible/roles/unattended_updates/tasks/main.yml`
- Create: `ansible/roles/unattended_updates/templates/50unattended-upgrades.j2`

Bewusst: Sicherheits-Updates automatisch, aber KEIN automatischer Neustart — nach dem heutigen unangekündigten Reboot (der einen ungeplanten Ausfall von 7 Diensten verursacht hat) soll ein Neustart immer eine bewusste, geplante Aktion bleiben.

- [ ] **Step 1: Template schreiben**

`ansible/roles/unattended_updates/templates/50unattended-upgrades.j2`:
```
Unattended-Upgrade::Origins-Pattern {
    "origin=Debian,codename=${distro_codename},label=Debian-Security";
    "origin=Proxmox";
};
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
```

- [ ] **Step 2: Task schreiben**

`ansible/roles/unattended_updates/tasks/main.yml`:
```yaml
---
- name: unattended-upgrades installieren
  ansible.builtin.apt:
    name: unattended-upgrades
    state: present
    update_cache: true
    cache_valid_time: 3600

- name: Automatische Sicherheits-Updates konfigurieren, kein Auto-Reboot
  ansible.builtin.template:
    src: 50unattended-upgrades.j2
    dest: /etc/apt/apt.conf.d/50unattended-upgrades.local
    owner: root
    group: root
    mode: "0644"

- name: Taeglichen Update-Check aktivieren
  ansible.builtin.copy:
    dest: /etc/apt/apt.conf.d/20auto-upgrades
    content: |
      APT::Periodic::Update-Package-Lists "1";
      APT::Periodic::Unattended-Upgrade "1";
    owner: root
    group: root
    mode: "0644"
```

- [ ] **Step 3: Commit**

```bash
git add ansible/roles/unattended_updates
git commit -m "feat: Rolle unattended_updates - Sicherheits-Updates automatisch, Neustart bewusst nicht"
```

---

## Task 7: Rolle `fail2ban`

**Files:**
- Create: `ansible/roles/fail2ban/tasks/main.yml`
- Create: `ansible/roles/fail2ban/templates/jail.local.j2`

- [ ] **Step 1: Template schreiben**

`ansible/roles/fail2ban/templates/jail.local.j2`:
```ini
[sshd]
enabled = true
maxretry = 5
bantime = 1h
findtime = 10m
```

- [ ] **Step 2: Task schreiben**

`ansible/roles/fail2ban/tasks/main.yml`:
```yaml
---
- name: fail2ban installieren
  ansible.builtin.apt:
    name: fail2ban
    state: present
    update_cache: true
    cache_valid_time: 3600

- name: SSH-Jail konfigurieren
  ansible.builtin.template:
    src: jail.local.j2
    dest: /etc/fail2ban/jail.local
    owner: root
    group: root
    mode: "0644"
  notify: restart fail2ban

- name: fail2ban aktiv und beim Start dabei
  ansible.builtin.service:
    name: fail2ban
    state: started
    enabled: true
```

- [ ] **Step 3: Handler schreiben**

`ansible/roles/fail2ban/handlers/main.yml`:
```yaml
---
- name: restart fail2ban
  ansible.builtin.service:
    name: fail2ban
    state: restarted
```

- [ ] **Step 4: Commit**

```bash
git add ansible/roles/fail2ban
git commit -m "feat: Rolle fail2ban"
```

---

## Task 8: Rolle `autoheal_anker` (nur Anker)

**Files:**
- Create: `ansible/roles/autoheal_anker/tasks/main.yml`

Übernommen aus dem alten `archive/ansible-homeserver2027/ansible/playbooks/pve_autoheal.yml` (inhaltlich brauchbar, siehe Spec), an die neue Rollen-Struktur angepasst.

- [ ] **Step 1: Task schreiben**

`ansible/roles/autoheal_anker/tasks/main.yml`:
```yaml
---
- name: Automatischen Neustart nach Kernel-Panik aktivieren
  ansible.posix.sysctl:
    name: kernel.panic
    value: "10"
    state: present
    reload: true
    sysctl_file: /etc/sysctl.d/99-autoheal.conf

- name: Watchdog-Paket installieren
  ansible.builtin.apt:
    name: watchdog
    state: present
    update_cache: true
    cache_valid_time: 3600

- name: Watchdog-Geraet konfigurieren
  ansible.builtin.lineinfile:
    path: /etc/watchdog.conf
    regexp: '^#?watchdog-device'
    line: 'watchdog-device = /dev/watchdog'

- name: Lastgrenze fuer Watchdog konfigurieren
  ansible.builtin.lineinfile:
    path: /etc/watchdog.conf
    regexp: '^#?max-load-1\s*='
    line: 'max-load-1            = 24'

- name: Watchdog-Dienst aktiv und beim Start dabei
  ansible.builtin.service:
    name: watchdog
    state: started
    enabled: true
```

- [ ] **Step 2: Commit**

```bash
git add ansible/roles/autoheal_anker
git commit -m "feat: Rolle autoheal_anker - aus altem Playbook uebernommen"
```

---

## Task 9: `baseline.yml` zusammenstellen + kompletter Testlauf gegen Anker

**Files:**
- Create: `ansible/playbooks/baseline.yml`

**Interfaces:**
- Consumes: alle Rollen aus Task 3-8

- [ ] **Step 1: Playbook schreiben**

`ansible/playbooks/baseline.yml`:
```yaml
---
- name: FraWo Server-Grundlinie
  hosts: pve_hosts
  become: false
  roles:
    - ssh_hardening
    - firewall_baseline
    - autostart_guests
    - unattended_updates
    - fail2ban

- name: Anker-spezifische Zusatzhaertung
  hosts: anker-pve
  become: false
  roles:
    - autoheal_anker
```

- [ ] **Step 2: Syntax pruefen**

Run: `ansible-playbook ansible/playbooks/baseline.yml --syntax-check`
Expected: `playbook: ansible/playbooks/baseline.yml` ohne Fehlermeldung.

- [ ] **Step 3: Probe-Modus gegen Anker**

Run: `ansible-playbook ansible/playbooks/baseline.yml --limit anker-pve --check --diff`
Expected: Laeuft durch ohne Fehler. Erwartete Aenderungen: `firewall_baseline` und `unattended_updates`/`fail2ban` zeigen `changed` (noch nicht vorhanden), `ssh_hardening` und `autostart_guests` zeigen **keine Aenderung** (Anker ist laut heutigem Audit bereits SSH-gehaertet und hat bereits fuer alle Gaeste `onboot: 1`).

- [ ] **Step 4: Ergebnis mit Wolf durchsehen**

Die `--diff`-Ausgabe aus Schritt 3 zeigen und kurz erklaeren was sich aendern wuerde, bevor es echt angewendet wird.

- [ ] **Step 5: Echter Lauf gegen Anker**

Run: `ansible-playbook ansible/playbooks/baseline.yml --limit anker-pve`
Expected: `PLAY RECAP` zeigt `failed=0`, `unreachable=0`.

- [ ] **Step 6: Idempotenz pruefen — zweiter Lauf sofort danach**

Run: `ansible-playbook ansible/playbooks/baseline.yml --limit anker-pve`
Expected: `PLAY RECAP` zeigt `changed=0` (bis auf den `autostart_guests`-Startreihenfolge-Task, siehe Hinweis in Task 5 — dieser eine Task darf `changed` bleiben, alle anderen nicht).

- [ ] **Step 7: Live-Funktionen pruefen**

```bash
ssh anker-pve "systemctl is-active fail2ban watchdog"
ssh anker-pve "pve-firewall status"
timeout 8 bash -c "echo > /dev/tcp/10.1.0.92/22" && echo "SSH erreichbar"
```
Expected: `active`/`active`, `enabled/running`, SSH erreichbar — nichts an der Kernfunktion des Anker-Servers hat sich verschlechtert.

- [ ] **Step 8: Commit**

```bash
git add ansible/playbooks/baseline.yml
git commit -m "feat: baseline.yml Playbook, gegen Anker getestet"
```

---

## Task 10: Kompletter Lauf gegen ProDesk (Live-System)

**Files:** keine neuen — nur Ausfuehrung + Verifikation

- [ ] **Step 1: Probe-Modus gegen ProDesk**

Run: `ansible-playbook ansible/playbooks/baseline.yml --limit stock-pve --check --diff`
Expected: Laeuft ohne Fehler durch. `autostart_guests` zeigt **keine** Aenderung (heute bereits manuell gesetzt), `firewall_baseline`/`unattended_updates`/`fail2ban` zeigen `changed` (erste Einrichtung).

- [ ] **Step 2: Ergebnis mit Wolf durchsehen**

- [ ] **Step 3: Echter Lauf gegen ProDesk**

Run: `ansible-playbook ansible/playbooks/baseline.yml --limit stock-pve`
Expected: `PLAY RECAP` zeigt `failed=0`, `unreachable=0`.

- [ ] **Step 4: Idempotenz pruefen**

Run: `ansible-playbook ansible/playbooks/baseline.yml --limit stock-pve`
Expected: `changed=0` (Ausnahme wie in Task 5 vermerkt).

- [ ] **Step 5: Live-Funktionen pruefen — besonders wichtig, hier laeuft das Live-Radio**

```bash
curl -s -o /dev/null -w "Website: %{http_code}\n" https://frawo.tech
curl -s -o /dev/null -w "Radio: %{http_code}\n" https://funk.frawo.tech
curl -s -o /dev/null -w "Vault: %{http_code}\n" https://vault.frawo.tech
ssh stock-pve "systemctl is-active fail2ban"
```
Expected: Website/Radio je `200`/`302`, Vault `200`, fail2ban `active`.

- [ ] **Step 6: Commit (Abschluss)**

```bash
git add -A
git commit -m "chore: Ansible-Grundlinie gegen beide Server verifiziert"
```
