# Stockenweiler Support Brief

- site: `Stockenweiler`
- support label: `Rentner OS`
- canonical external name: `online-prinz.de`
- primary remote access: `tailscale`
- fallback remote access: `anydesk`
- WAN admin exposure allowed: `False`

## First Support Targets

- MagentaTV / TV path
- Father desktop remote help
- Printer / scanner help
- Existing local Home Assistant support

## Current Known Local Facts

- Router: `FRITZ!Box 5690 Pro` @ `192.168.178.1`
- Proxmox: `proxmox Host` @ `192.168.178.25`
- Home Assistant: `homeassistant` @ `192.168.178.67`
- Printer: `Brother - Drucker` @ `192.168.178.153`
- MagentaTV: `MagentaTV` @ `192.168.178.120`

## Do Not Do

- do not expose admin paths to the internet
- do not build site-to-site VPN in V1
- do not mix the Stockenweiler LAN into the FraWo production LAN

## Legacy Conflicts To Revalidate

- `proxmox_host_ip`: best guess `192.168.178.25`, conflicting legacy `192.168.178.172`
- `home_assistant_ip`: best guess `192.168.178.67`, conflicting legacy `192.168.178.68`
