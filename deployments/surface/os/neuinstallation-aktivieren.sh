#!/bin/bash
# Aktiviert EINMALIG den Start ins Installationsabbild (GRUB-Loopback + toram).
# Scheitert der Abbildstart, bootet der darauffolgende Start wieder das alte System.
set -euo pipefail

cd /frawo-install
sha256sum -c frawo-surface.iso.sha256
cp -n /etc/default/grub "/etc/default/grub.bak-$(date +%Y%m%d)"
sed -i 's/^GRUB_DEFAULT=.*/GRUB_DEFAULT=saved/' /etc/default/grub

cat > /etc/grub.d/42_frawo_neuinstallation <<'EOF'
#!/bin/sh
exec tail -n +3 $0
menuentry "FraWo-Neuinstallation (automatisch)" --id frawo-neu {
    insmod part_gpt
    insmod ext2
    insmod iso9660
    insmod loopback
    set isofile="/frawo-install/frawo-surface.iso"
    search --no-floppy --set=root --file $isofile
    loopback loop ($root)$isofile
    linux (loop)/casper/vmlinuz iso-scan/filename=$isofile toram autoinstall ---
    initrd (loop)/casper/initrd
}
EOF
chmod 755 /etc/grub.d/42_frawo_neuinstallation
update-grub
grub-set-default 0
grub-reboot frawo-neu
grub-editenv list
echo "Bereit - naechster Start (einmalig): FraWo-Neuinstallation"
