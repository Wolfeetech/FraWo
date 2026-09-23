#!/bin/bash
# Baut /root/surface-iso/frawo-surface.iso (Ubuntu 24.04 Server + /autoinstall.yaml).
# Laeuft auf dem OptiPlex als root. Das Abbild enthaelt das WLAN-Passwort und wird
# deshalb mit 0600 angelegt, niemals eingecheckt und nach dem Einsatz geloescht.
# Aufruf: REPO_OS=/root/surface-os bash baue-iso.sh
set -euo pipefail

REPO_OS=${REPO_OS:-/root/surface-os}
ARBEIT=/root/surface-iso
BASIS=https://releases.ubuntu.com/24.04

command -v xorriso >/dev/null || apt-get install -y xorriso
mkdir -p "$ARBEIT"
chmod 700 "$ARBEIT"
cd "$ARBEIT"

curl -fsSL "$BASIS/SHA256SUMS" -o SHA256SUMS
ISO=$(grep -o 'ubuntu-24\.04\.[0-9]*-live-server-amd64\.iso' SHA256SUMS | sort -V | tail -1)
[ -f "$ISO" ] || curl -fL --retry 3 -o "$ISO" "$BASIS/$ISO"
grep -E " \*?$ISO$" SHA256SUMS | sha256sum -c -

PSK=$(python3 -c "
import sys; sys.path.insert(0, '/root/m1')
from ucg import call
print([w for w in call('GET', '/rest/wlanconf') if w.get('name') == 'FraWo__ioT'][0]['x_passphrase'])")
HASH=$(openssl passwd -6 "$(openssl rand -base64 24)")
export PSK HASH

umask 077
python3 - "$REPO_OS/autoinstall.yaml.vorlage" "$REPO_OS/schluessel" > autoinstall.yaml <<'PY'
import glob, json, os, sys

template = open(sys.argv[1], encoding="utf-8").read()
keys = [open(path, encoding="utf-8").read().strip() for path in sorted(glob.glob(sys.argv[2] + "/*.pub"))]
assert keys, "keine oeffentlichen SSH-Schluessel"
template = template.replace("@@WLAN_PSK@@", json.dumps(os.environ["PSK"])[1:-1])
template = template.replace("@@PASSWORT_HASH@@", os.environ["HASH"])
template = template.replace("@@SSH_KEYS@@", "\n".join('      - "%s"' % key for key in keys))
sys.stdout.write(template)
PY
python3 -c "import yaml; data=yaml.safe_load(open('autoinstall.yaml')); assert data['autoinstall']['ssh']['authorized-keys']; assert '@@' not in open('autoinstall.yaml').read()"

xorriso -osirrox on -indev "$ISO" -extract /boot/grub/grub.cfg grub.cfg >/dev/null 2>&1
chmod u+w grub.cfg
sed -i -E 's|(linux\s+/casper/vmlinuz)\s+---|\1 autoinstall ---|' grub.cfg
sed -i -E 's/^set timeout=.*/set timeout=3/' grub.cfg
grep -q 'vmlinuz autoinstall ---' grub.cfg

rm -f frawo-surface.iso
xorriso -indev "$ISO" -outdev frawo-surface.iso \
  -map autoinstall.yaml /autoinstall.yaml \
  -map grub.cfg /boot/grub/grub.cfg \
  -boot_image any replay >/dev/null 2>&1
chmod 600 frawo-surface.iso autoinstall.yaml
sha256sum frawo-surface.iso > frawo-surface.iso.sha256
chmod 600 frawo-surface.iso.sha256

# Nachweis ohne Ausgabe des WLAN-Passworts.
rm -f nachweis.yaml nachweis.grub.cfg
xorriso -osirrox on -indev frawo-surface.iso -extract /autoinstall.yaml nachweis.yaml >/dev/null 2>&1
xorriso -osirrox on -indev frawo-surface.iso -extract /boot/grub/grub.cfg nachweis.grub.cfg >/dev/null 2>&1
grep -c 'FraWo__ioT' nachweis.yaml
grep -c 'vmlinuz autoinstall ---' nachweis.grub.cfg
rm -f nachweis.yaml nachweis.grub.cfg
cat frawo-surface.iso.sha256
