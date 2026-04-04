# Coolify Management Host Audit

- Generated at: `2026-04-04T01:55:32+02:00`
- Target: `root@100.69.179.87`
- Host: `proxmox-anker`
- Version: `pve-manager/9.1.6/71482d1833ded40a (running kernel: 6.17.13-2-pve)`
- Memory available: `5.14 GiB`
- local-lvm free: `60.91 GiB`
- local dir free: `17.39 GiB`
- Toolbox temporary fallback ok: `true`
- Recommendation: `dedicated_internal_anker_management_node`

## Recommended Node

- kind: `lxc`
- suggested_vmid: `130`
- name: `coolify-mgmt`
- vcpus: `2`
- memory_mb: `2048`
- rootfs_gb: `24`
- storage: `local-lvm`
- network: `internal_management_non_dmz`

## Fit Checks

- memory_ok: `true`
- local_lvm_ok: `true`
- local_dir_ok: `false`

## Rejected Targets

- `proxmox_anker_host_itself`
- `stock_pve`
- `dmz_nodes`
- `surface_go_frontend_while_unstable`

## Next Gated Step

- `create_dedicated_internal_management_ct_or_vm_on_anker`
