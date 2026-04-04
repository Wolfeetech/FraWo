# UCG Portal Pilot Preflight

- generated_at: `2026-04-03 23:26:52`
- pilot: `portal`
- change_class: `read_only`
- ready_for_gated_runtime_change: `true`
- runtime_alias_active: `true`
- recommendation: `portal_pilot_runtime_green`

## Checks

- `portal_frontdoor_http` -> `ok` / HTTP 200 via http://100.99.206.128:8447/
- `portal_frontdoor_status_json` -> `ok` / HTTP 200, platform_core=ok, healthy=7/7
- `portal_internal_hostname` -> `ok` / HTTP 200 via http://portal.hs27.internal/
- `portal_internal_status_json` -> `ok` / HTTP 200 via http://portal.hs27.internal/status.json
- `anker_management_ssh` -> `ok` / proxmox-anker; pve-manager/9.1.6/71482d1833ded40a (running kernel: 6.17.13-2-pve)
- `stock_management_ssh` -> `ok` / pve; pve-manager/9.1.4/5ac30304265fbd8e (running kernel: 6.17.2-2-pve)
- `pilot_documentation_present` -> `ok` / pilot_section=True snapshot_rule=True verify_rule=True
- `toolbox_target_ip_alias_active` -> `ok` / inet 10.1.0.20/24 scope global eth0
- `portal_target_ip_vhost_status_json` -> `ok` / platform_core=ok, healthy=7/7

## Portal Status Summary

- platform_core: `ok`
- healthy_services: `7` / `7`
- frontdoor_root_http: `200`
- internal_root_http: `200`
- target_ip: `10.1.0.20`
- target_platform_core: `ok`
- target_healthy_services: `7` / `7`
