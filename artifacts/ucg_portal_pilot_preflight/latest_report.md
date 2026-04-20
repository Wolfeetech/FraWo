# UCG Portal Pilot Preflight

- generated_at: `2026-04-20 15:27:48`
- pilot: `portal`
- change_class: `read_only`
- ready_for_gated_runtime_change: `false`
- runtime_alias_active: `false`
- recommendation: `fix_preflight_findings_before_any_runtime_portal_cutover`

## Checks

- `portal_frontdoor_http` -> `ok` / HTTP 200 via http://100.82.26.53:8447/
- `portal_frontdoor_status_json` -> `fail` / HTTP 404, platform_core=unknown, healthy=0/0
- `portal_internal_hostname` -> `fail` / HTTP 0 via http://100.82.26.53/
- `portal_internal_status_json` -> `fail` / HTTP 0 via http://100.82.26.53/status.json
- `anker_management_ssh` -> `ok` / proxmox-anker; pve-manager/9.1.6/71482d1833ded40a (running kernel: 6.17.13-2-pve)
- `stock_management_ssh` -> `ok` / pve; pve-manager/9.1.4/5ac30304265fbd8e (running kernel: 6.17.2-2-pve)
- `pilot_documentation_present` -> `fail` / pilot_section=False snapshot_rule=False verify_rule=False
- `toolbox_target_ip_alias_active` -> `ok` / inet 10.1.0.20/24 brd 10.1.0.255 scope global eth0
- `portal_target_ip_vhost_status_json` -> `fail` / platform_core=unknown, healthy=0/0

## Portal Status Summary

- platform_core: `unknown`
- healthy_services: `0` / `0`
- frontdoor_root_http: `200`
- internal_root_http: `0`
- target_ip: `10.1.0.20`
- target_platform_core: `unknown`
- target_healthy_services: `0` / `0`
