# Operator Todo Queue

## Purpose

This file is the compact operator-facing queue for the next manual actions.

It is intentionally shorter than `MEMORY.md` and should answer one question quickly:

What does Wolf or Franz need to do next so Codex or Gemini can continue autonomously?

## Now

1. Let the first toolbox media sync run for a while.
   - Current path: Pi USB library -> `/srv/media-library/music/bootstrap-radio-usb`
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

3. Do not unplug the `64GB` USB stick from Proxmox.
  - Why: the stick has now been repurposed into the interim PBS USB storage path for `VM 240`.
  - Resume after this:
    - keep the stick attached as long as PBS uses it
    - Codex/Gemini can continue with PBS proof-backup verification and later migration to larger storage

4. Keep PBS interim online while proof backups are stabilized.
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
4. Continue the `frawo.studio` public edge when the internal platform is fully accepted.

## Canonical Detail Sources

- `MEMORY.md`
- `LIVE_CONTEXT.md`
- `MEDIA_SERVER_CLIENT_SETUP.md`
- `SURFACE_GO_FRONTEND_SETUP_PLAN.md`
- `PBS_VM_240_SETUP_PLAN.md`
