# Media Server Client Setup

## Purpose

This document is the operator runbook for the first usable FRAWO media experience on internal clients and TVs.

## Current Server Paths

- Internal browser path: `http://media.hs27.internal`
- Direct LAN path for TV apps: `http://192.168.2.20:8096`
- Mobile Tailscale interim path: `http://100.99.206.128:8449`

## Current Runtime State

- Jellyfin V1 runs on `CT 100 toolbox`
- reverse proxy path is verified internally
- mobile Tailscale frontdoor is verified
- no public edge is involved yet
- the Jellyfin startup wizard is complete
- at least one local Jellyfin user exists
- the `Music` library is already attached at:
  - `/media/music`
- a bootstrap sync from the Pi USB music library into the toolbox media library is now running
- current target path for the imported radio music is:
  - `/media/music/bootstrap-radio-usb`

## Google TV / Android TV / Thomson

Use this path first because it is the clearest practical value for the household.

1. Install the `Jellyfin` app from the TV app store.
2. Add a server manually.
3. Preferred server URL on the home LAN:
   - `http://192.168.2.20:8096`
4. If internal DNS is available on that client, the nicer alternative is:
   - `http://media.hs27.internal`
5. Sign in with the Jellyfin admin or a later user account.

## Browser Clients

- ZenBook or other internal devices:
  - `http://media.hs27.internal`
- If a client does not use internal DNS yet:
  - `http://192.168.2.20:8096`

## Mobile Interim Access

- over Tailscale:
  - `http://100.99.206.128:8449`

This is an interim internal/mobile path, not the final public design.

## First Client Rollout Steps

1. Install the Jellyfin app on the first Thomson / Google TV device.
2. Add the server:
   - preferred: `http://192.168.2.20:8096`
   - alternative with internal DNS: `http://media.hs27.internal`
3. Sign in with the existing Jellyfin user.
4. Start with the `Music` library only.
5. Expect the library to keep growing while the bootstrap sync is still running.
6. Add `Movies`, `Shows` and `Homevideos` only when there is real content there.

## Notes

- `AzuraCast` on the Pi remains the radio system
- `Jellyfin` on toolbox is for on-demand media playback
- the long-term storage source still needs to mature beyond the temporary USB/bootstrap state
- the current practical bridge is: Pi USB library -> toolbox media bootstrap path -> Jellyfin
- a local manifest-based workflow for later `favorites` and `curated` selections now exists in the workspace:
  - `manifests/media/favorites_paths.txt`
  - `manifests/media/curated_paths.txt`
  - `make toolbox-music-selection-seed-report`
  - `make toolbox-music-selection-sync`
