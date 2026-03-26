# Identity Standard

## Goal

Use personal identities for people, role identities for shared functions, and never use a shared mailbox as a personal admin login.

## Canonical Mailboxes

| Identity | Type | Purpose |
| --- | --- | --- |
| `wolf@frawo-tech.de` | personal | owner, admin, audit trail |
| `franz@frawo-tech.de` | personal | standard user, audit trail |
| `frontend@frawo-tech.de` | shared role | Surface Go, kiosk, shared frontend workflows |
| `info@frawo-tech.de` | role | website/contact/inbound company mail |
| `noreply@frawo-tech.de` | role | system notifications |
| `admin@frawo-tech.de` | role | optional break-glass/admin alias |

## Mail And Secrets Default

- Real mailboxes are created first at `STRATO`.
- `Vaultwarden` on `CT120` is the target secret home.
- Shared business secrets live in the `FraWo` organization, not in isolated personal vaults.
- Markdown files may document state, but they are not the final password store.

## Rules

- `wolf@frawo-tech.de` and `franz@frawo-tech.de` are the primary human identities.
- `info@frawo-tech.de` is not a personal admin account.
- `frontend@frawo-tech.de` is the only shared device identity.
- Shared device identities get no infrastructure-wide admin rights.
- Every service should map back to a personal owner plus a documented role account where needed.

## Service Mapping

| Service | Wolf | Franz | Frontend | Notes |
| --- | --- | --- | --- | --- |
| Nextcloud | personal account | personal account | limited shared account | main file workflows |
| Paperless | personal account | personal account | limited shared search/upload account | access should follow filing rules |
| Odoo | named user | named user | no admin | business actions must stay attributable |
| Jellyfin | named profile | named profile | shared device profile | quick switching on TV/Surface |
| AzuraCast | named admin | optional editor later | no admin | avoid shared admin |
| Surface Go | local admin `frawo` | none | kiosk user `frontend` | kiosk is read-only by default |
| Stockenweiler | support owner | n/a | n/a | separate support and provider identities |

## Surface Go Standard

- Local Linux admin stays separate from the kiosk user.
- `frontend` gets no `sudo`.
- `frontend` gets launcher-based access to approved UIs only.
- Remote control of the Studio PC is behind an admin hurdle.
- Monitoring may be visible by default; control actions may not.

## FraWo Organization

- Organization name: `FraWo`
- Legal frame: `FraWo GbR`
- Members:
  - `wolf@frawo-tech.de` as first owner and DevOps lead
  - `franz@frawo-tech.de` as second shared business member
- Site contexts:
  - `Anker` for the base server and private core network
  - `Villa` for studio and radio operations
  - `Stockenweiler` for the external support location

## Vaultwarden Structure

- `Core Infra`
- `Business Apps`
- `Media`
- `Mail & Domains`
- `Devices`
- `Stockenweiler`

## Order Of Work

1. Create the final mailboxes at `STRATO`.
2. Finish internal `HTTPS` for `Vaultwarden`.
3. Create the `FraWo` organization and the six collections.
4. Store current platform secrets in `Vaultwarden`.
5. Create or rename app users to match the canonical identities.
6. Remove temporary shared admin usage.
7. Harden the Surface Go around the `frontend` role.
8. Keep a separate secret area for `Stockenweiler`.
