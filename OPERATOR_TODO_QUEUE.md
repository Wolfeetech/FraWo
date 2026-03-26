# Operator Todo Queue

## Purpose

This file is the compact operator-facing queue for the next manual actions.

It is intentionally shorter than `MEMORY.md` and should answer one question quickly:

What does Wolf or Franz need to do next so Codex or Gemini can continue autonomously?

## Now

1. Deploy the new **Single Source of Truth Storage Node (CT 110)**.
   - Why: Instead of isolating data in VMs (Nextcloud vs Paperless) or copying media via Rsync (Pi vs Toolbox), we need a centralized NFSv4 data node.
   - Action: Complete and run `ansible/playbooks/deploy_storage_node.yml` to spin up `CT 110`.
   - Setup `/mnt/data/documents` and `/mnt/data/media` and export them via NFS.
   - Reference: `SHARED_STORAGE_ARCHITECTURE_PLAN.md`

2. Implement NFS Mounts in existing VMs:
   - Mount `/mnt/data/documents` into `VM 230` (Paperless) as `/media/archive`.
   - Mount `/mnt/data/documents` into `VM 200` (Nextcloud) as an External Storage (Local/NFS).
   - Mount `/mnt/data/media` into `CT 100` (Jellyfin) and `raspberry_pi_radio` (AzuraCast, via Tailscale).

3. Let the first toolbox media sync run for a while.
   - Why: Jellyfin gets immediate practical value once enough media has landed on the toolbox side.
   - Quick check: `make toolbox-media-bootstrap-progress`

2. Let the first Jellyfin bootstrap import continue.
   - Current source path: Pi USB library -> `/srv/media-library/music/bootstrap-radio-usb`
   - Current client path: Jellyfin music library is already attached at `/media/music`
   - Quick checks:
      - `make toolbox-media-bootstrap-progress`
      - `make toolbox-jellyfin-ui-check`
      - `make toolbox-music-scan-issues`
      - `make toolbox-music-curation-candidates`
      - `make toolbox-music-curated-layout`
      - `make toolbox-music-selection-seed-report`
      - `make toolbox-music-selection-sync`
    - Current state:
      - import is effectively complete
      - no current quarantine candidates remain
      - `favorites` starter is live
      - `curated` starter is live
    - Resume after this: Thomson / Google TV clients can be connected cleanly and the starter selection can be refined over time.

3. Use the Surface locally and note any remaining UX rough edges.
   - Why: the technical hardening is done; the remaining work is browser and touch-keyboard polish, not remote admin or base setup.
   - Current expectation:
     - the device stays awake on its own
     - `FRAWO Control` opens the local portal on `127.0.0.1:17827`
     - touch keyboard behavior may still need one more local polish pass
   - Resume after this: capture concrete UX issues for Gemini instead of reopening the infrastructure baseline.

4. Place the workspace on `WOLFSTUDIOPC` and run the Windows bootstrap once.
   - Current live fingerprint:
     - hostname `WOLFSTUDIOPC.local`
     - IP `192.168.2.162`
     - Ethernet link active
   - Needed local action on the PC:
     - put the repo folder onto the machine
     - run `scripts\bootstrap_windows_workspace.cmd`
   - Resume after this: Codex or Gemini can verify the stable alias and fold the PC into the managed trusted-client path.

## Soon

1. Test one real mobile off-LAN path.
   - On the phone with Wi-Fi off and Tailscale connected:
     - `http://portal.hs27.internal`
     - `http://ha.hs27.internal`
     - `http://odoo.hs27.internal/web/login`

2. Resolve the remaining Easy Box unknowns.
   - Main unresolved area: `.141-.144` as private MAC clients without owner mapping.
   - Current fingerprint: they answer ping but expose no common admin/app ports and no HTTP response.
   - Quick check: `make inventory-unknown-report`
   - Resume after this: DHCP and gateway planning become cleaner.

3. Decide the document flow for Paperless and Nextcloud.
   - Current technical base is now live:
     - `VM 200 nextcloud` is fully installed
     - `VM 230 paperless` has the required app users
     - passwords are stored only in encrypted Ansible Vault
     - `Paperless/Eingang` in Nextcloud is now the upload path into the Paperless consume flow
     - `Paperless/Archiv` in Nextcloud receives mirrored archive output
   - Resume after this:
     - test one real PDF/scan through the new path
     - then Codex/Gemini can refine shortcuts, naming and user UX

4. Do not unplug the `64GB` USB stick from Proxmox.
  - Why: the stick has now been repurposed into the interim PBS USB storage path for `VM 240`.
  - Resume after this:
    - keep the stick attached as long as PBS uses it
    - Codex/Gemini can continue with PBS proof-backup verification and later migration to larger storage

5. Keep PBS interim online while proof backups are stabilized.
  - Current live state:
    - `VM 240 pbs` installed on `192.168.2.25`
    - datastore `hs27-interim` active
     - Proxmox storage `pbs-interim` active
     - daily job `hs27-pbs-interim-daily` exists
     - retention now keeps the USB usable over time:
       - `02:40,14:40`
       - `keep-daily=2`
       - `keep-weekly=1`
       - `keep-monthly=1`
     - first green proof-backup run is already done for `VM 220`
     - first green restore drill is also already done for `VM 220`
   - Remaining technical blocker:
     - recurring restore drills and later migration to larger PBS storage

## Later

1. Connect HAOS USB hardware on the Proxmox host.
   - Quick check first: `make haos-usb-audit`
2. Continue radio curation from temporary USB music to `RadioLibrary` / `RadioAssets`.
3. Move from bootstrap media paths to a more durable long-term media storage layout.
4. Continue the `frawo-tech.de` public edge only after the internal platform is fully accepted.

## Canonical Detail Sources

- `MEMORY.md`
- `LIVE_CONTEXT.md`
- `SHARED_STORAGE_ARCHITECTURE_PLAN.md`
- `MEDIA_SERVER_CLIENT_SETUP.md`
- `SURFACE_GO_FRONTEND_SETUP_PLAN.md`
- `PBS_VM_240_SETUP_PLAN.md`
