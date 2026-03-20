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
- the first Jellyfin admin account still needs to be created in the UI

## Google TV / Android TV / Thomson

Use this path first because it is the clearest practical value for the household.

1. Install the `Jellyfin` app from the TV app store.
2. Add a server manually.
3. Preferred server URL on the home LAN:
   - `http://192.168.2.20:8096`
4. If internal DNS is available on that client, the nicer alternative is:
   - `http://media.hs27.internal`
5. Sign in with the Jellyfin admin or a later user account once the first UI setup is complete.

## Browser Clients

- ZenBook or other internal devices:
  - `http://media.hs27.internal`
- If a client does not use internal DNS yet:
  - `http://192.168.2.20:8096`

## Mobile Interim Access

- over Tailscale:
  - `http://100.99.206.128:8449`

This is an interim internal/mobile path, not the final public design.

## First UI Steps Still Needed

1. Open `http://media.hs27.internal`
2. Create the first Jellyfin admin account
3. Attach the initial libraries:
   - Movies -> `/media/movies`
   - Shows -> `/media/shows`
   - Music -> `/media/music`
   - Homevideos -> `/media/homevideos`
4. Leave transcoding conservative at first
5. Add TV clients only after the admin setup is complete

## Notes

- `AzuraCast` on the Pi remains the radio system
- `Jellyfin` on toolbox is for on-demand media playback
- the long-term storage source still needs to mature beyond the temporary USB/bootstrap state
