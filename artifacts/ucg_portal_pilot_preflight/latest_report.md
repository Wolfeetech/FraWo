# UCG Portal Pilot Preflight

- generated_at: `2026-04-05 01:32:41`
- pilot: `portal`
- change_class: `read_only`
- ready_for_gated_runtime_change: `false`
- runtime_alias_active: `false`
- recommendation: `fix_preflight_findings_before_any_runtime_portal_cutover`

## Checks

- `portal_frontdoor_http` -> `ok` / HTTP 200 via http://100.99.206.128:8447/
- `portal_frontdoor_status_json` -> `fail` / HTTP 200, platform_core=attention, healthy=6/7
- `portal_internal_hostname` -> `fail` / HTTP 0 via http://portal.hs27.internal/
- `portal_internal_status_json` -> `fail` / HTTP 0 via http://portal.hs27.internal/status.json
- `anker_management_ssh` -> `fail` / root@100.69.179.87: Permission denied (publickey,password).
- `stock_management_ssh` -> `fail` / ssh: Could not resolve hostname stock-pve: Temporary failure in name resolution
- `pilot_documentation_present` -> `ok` / pilot_section=True snapshot_rule=True verify_rule=True
- `toolbox_target_ip_alias_active` -> `fail` / root@100.69.179.87: Permission denied (publickey,password).
- `portal_target_ip_vhost_status_json` -> `fail` / platform_core=unknown, healthy=0/0

## Portal Status Summary

- platform_core: `attention`
- healthy_services: `6` / `7`
- frontdoor_root_http: `200`
- internal_root_http: `0`
- target_ip: `10.1.0.20`
- target_platform_core: `unknown`
- target_healthy_services: `0` / `0`
