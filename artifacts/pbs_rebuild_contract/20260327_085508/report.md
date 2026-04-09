# PBS Rebuild Contract Check

Recommendation: `blocked_wait_for_explicit_device_contract`

## Contract

- Contract file: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/manifests/pbs_rebuild/device_contract.json`
- Approved by: `missing`
- Approved at: `missing`
- Change ticket: `missing`
- Expected datastore mount: `/srv/pbs-datastore`
- Proxmox storage ID: `pbs-usb`

## Boot USB

- Approved serial: `missing`
- Destructive approval: `false`
- Allowed size range: `50.0` - `70.0` GiB
- Visible device: `not found`

## Datastore Device

- Approved serial: `missing`
- Destructive approval: `false`
- Reformat existing filesystem approved: `false`
- Minimum size: `200.0` GiB
- Visible device: `not found`

## Findings

- Boot USB serial is not approved in the device contract.
- Datastore device serial is not approved in the device contract.
- Device contract is missing operator approval metadata.