# Jellyfin User Management & Profile Plan

## Goal
Establish a clean Jellyfin user model before broader TV and shared-device rollout.

## Current State

- `root` remains the hidden technical bootstrap admin.
- `Wolf` exists, is visible on the login screen and has admin rights.
- `Franz` exists, is visible on the login screen and has no admin rights.
- `TV Wohnzimmer` exists, is visible on the login screen and has no admin rights.
- All three interactive profiles have working passwords.
- The productive credentials belong in `Vaultwarden / FraWo / Media`, not in this Markdown file.
- On `2026-03-26`, a browser-side connection error was traced to `CT100 toolbox` running with rootfs flag `emergency_ro`; after `e2fsck` on `/var/lib/vz/images/100/vm-100-disk-0.raw`, the Jellyfin auth endpoint returned `200` again.
- The active production library is `Musik Netzwerk` on `/media/music-network/yourparty_Libary`.
- The obsolete local bootstrap library has been removed from `CT 100 toolbox`.
- Quick PIN setup is still open; the Easy Password API returned `403` in this environment, so PINs should be set later in the UI if still wanted.

## Current Credentials

| Profile | Role | Vaultwarden Reference | Status |
| --- | --- | --- | --- |
| `root` | hidden bootstrap admin | `FraWo / Media / Jellyfin Admin` | existing technical admin |
| `Wolf` | personal admin profile | `FraWo / Media / Jellyfin - Wolf` | live and verified |
| `Franz` | personal standard profile | `FraWo / Media / Jellyfin - Franz` | live and verified |
| `TV Wohnzimmer` | shared device profile | `FraWo / Media / Jellyfin - TV Wohnzimmer` | live and verified |

## Required Users

1. `Wolf`
   - personal main profile
   - admin rights
2. `Franz`
   - personal standard profile
   - separate history and settings
3. `TV Wohnzimmer`
   - shared device profile
   - no admin rights

## Quick User Switching Strategy

- Keep `root` hidden.
- Keep `Wolf`, `Franz` and `TV Wohnzimmer` visible on the login screen.
- Use `TV Wohnzimmer` as the default shared device profile on TVs.
- If quick PIN login is still desired, set it later in the Jellyfin UI for `Wolf` and `Franz`.

## Remaining Operator Work

1. Verify that all four Jellyfin credentials are present in `Vaultwarden / FraWo / Media`.
2. Optionally set UI PINs for `Wolf` and `Franz` under `http://media.hs27.internal`.
3. Configure client auto-login to `TV Wohnzimmer` on the first production TV.
4. Keep `root` as break-glass only.
