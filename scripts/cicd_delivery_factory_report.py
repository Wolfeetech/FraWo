#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "cicd" / "delivery_factory.json"
PREFLIGHT = ROOT / "artifacts" / "cicd_delivery_factory" / "latest_preflight.json"
CATALOG = ROOT / "deployment" / "factory" / "apps" / "catalog.json"
ARTIFACT_DIR = ROOT / "artifacts" / "cicd_delivery_factory"
REPORT_MD = ARTIFACT_DIR / "latest_report.md"


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    preflight = json.loads(PREFLIGHT.read_text(encoding="utf-8")) if PREFLIGHT.exists() else {}
    catalog = json.loads(CATALOG.read_text(encoding="utf-8")) if CATALOG.exists() else {"apps": []}
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# CI/CD Delivery Factory Report")
    lines.append("")
    lines.append(f"- Generated at: `{datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}`")
    lines.append(f"- Status: `{data.get('status', 'unknown')}`")
    controller = data.get("controller", {})
    lines.append(f"- Preferred CD controller: `{controller.get('preferred_cd', '-')}`")
    lines.append(f"- Platform-independence rule: `{controller.get('platform_independence_rule', '-')}`")
    if preflight:
        lines.append(f"- Safe scope now: `{preflight.get('summary', {}).get('safe_scope_now', 'unknown')}`")
    lines.append("")
    lines.append("## Verified Start State")
    lines.append("")
    for item in preflight.get("verified_facts", []):
        lines.append(f"- {item}")
    for item in preflight.get("rejected_assumptions", [])[:4]:
        lines.append(f"- rejected: {item}")
    lines.append("")
    lines.append("## Open Prerequisites")
    lines.append("")
    for item in preflight.get("open_prerequisites", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Branch Model")
    lines.append("")
    for key, value in data.get("branch_model", {}).items():
        lines.append(f"- `{key}` -> `{value}`")
    lines.append("")
    lines.append("## Environments")
    lines.append("")
    for item in data.get("environments", []):
        lines.append(f"- `{item.get('id')}`: exposure `{item.get('exposure')}`, trigger `{item.get('deploy_trigger')}`")
    lines.append("")
    lines.append("## Topology")
    lines.append("")
    for key, value in data.get("topology", {}).items():
        lines.append(f"- `{key}` -> subnet `{value.get('subnet')}`, role `{value.get('role')}`")
    lines.append("")
    lines.append("## Service Classes")
    lines.append("")
    for key, value in data.get("service_classes", {}).items():
        examples = ", ".join(value.get("examples", []))
        lines.append(f"- `{key}` -> HA `{value.get('ha_mode')}` / examples `{examples}`")
    lines.append("")
    lines.append("## App Catalog")
    lines.append("")
    apps = catalog.get("apps", [])
    ready = [app for app in apps if app.get("factory_deploy_ready_now")]
    lines.append(f"- Factory-ready now: `{len(ready)}` / `{len(apps)}`")
    for app in apps:
        lines.append(
            f"- `{app.get('id')}` -> class `{app.get('service_class')}`, wave `{app.get('candidate_wave')}`, ready `{str(app.get('factory_deploy_ready_now', False)).lower()}`"
        )
    lines.append("")
    lines.append("## Registry Contract")
    lines.append("")
    registry = data.get("registry", {})
    if registry:
        lines.append(f"- Preferred registry: `{registry.get('preferred', '-')}`")
        lines.append(f"- Namespace: `{registry.get('repository_namespace', '-')}`")
        lines.append(f"- First reference image: `{registry.get('first_reference_image', '-')}`")
        for key, value in registry.get("tag_contract", {}).items():
            lines.append(f"- `{key}` tags -> `{', '.join(value)}`")
    lines.append("")
    lines.append("## Env And Secret Contract")
    lines.append("")
    env_contract = data.get("env_secret_contract", {})
    for item in env_contract.get("public_env_examples", []):
        lines.append(f"- env example: `{item}`")
    for item in env_contract.get("contract_docs", []):
        lines.append(f"- contract doc: `{item}`")
    for item in env_contract.get("future_controller_secret_names", []):
        lines.append(f"- future controller secret: `{item}`")
    lines.append("")
    lines.append("## Secret Distribution Model")
    lines.append("")
    secret_model = data.get("secret_distribution_model", {})
    if secret_model:
        lines.append(f"- doc: `{secret_model.get('doc', '-')}`")
        lines.append(f"- GitHub environments: `{', '.join(secret_model.get('github_environments', []))}`")
        lines.append(f"- Package push auth: `{secret_model.get('package_push_auth', '-')}`")
        lines.append(f"- Runtime secret plane: `{secret_model.get('runtime_secret_plane', '-')}`")
    lines.append("")
    lines.append("## Coolify Host Contract")
    lines.append("")
    host_contract = data.get("coolify_management_host_contract", {})
    if host_contract:
        lines.append(f"- Preferred target: `{host_contract.get('preferred_target', '-')}`")
        lines.append(f"- Temporary fallback: `{host_contract.get('temporary_fallback', '-')}`")
        for item in host_contract.get("rejected_targets", []):
            lines.append(f"- rejected target: `{item}`")
        lines.append(f"- contract doc: `{host_contract.get('contract_doc', '-')}`")
        lines.append(f"- node spec doc: `{host_contract.get('node_spec_doc', '-')}`")
    lines.append("")
    lines.append("## First Deploy Bundle")
    lines.append("")
    bundle = data.get("first_reference_deploy_bundle", {})
    if bundle:
        lines.append(f"- app id: `{bundle.get('app_id', '-')}`")
        lines.append(f"- bundle: `{bundle.get('bundle', '-')}`")
        lines.append(f"- readme: `{bundle.get('readme', '-')}`")
        for item in bundle.get("compose_env_examples", []):
            lines.append(f"- compose env example: `{item}`")
    lines.append("")
    lines.append("## Release Train")
    lines.append("")
    for key, value in data.get("release_train", {}).items():
        lines.append(f"- `{key}` -> `{value}`")
    lines.append("")
    lines.append("## Backup Strategy")
    lines.append("")
    backup = data.get("backup_strategy", {})
    for item in backup.get("layers", []):
        lines.append(f"- layer: `{item}`")
    artifact_retention = backup.get("artifact_retention", {})
    if artifact_retention:
        lines.append(
            f"- OCI retention: dev `{artifact_retention.get('dev_successful_images', 0)}` / prod `{artifact_retention.get('prod_stable_releases', 0)}` / keep last good tag `{artifact_retention.get('keep_last_known_good_tag', False)}`"
        )
    retention_v1 = backup.get("retention_v1", {})
    if retention_v1:
        lines.append(
            f"- Backup retention v1: daily `{retention_v1.get('daily', 0)}` / weekly `{retention_v1.get('weekly', 0)}` / monthly `{retention_v1.get('monthly', 0)}`"
        )
    for key, value in backup.get("service_classes", {}).items():
        lines.append(f"- `{key}` -> `{value}`")
    for item in backup.get("stockenweiler_legacy_payload_before_thinning", []):
        lines.append(f"- preserve first: `{item}`")
    if backup.get("offsite_rule"):
        lines.append(f"- Offsite rule: `{backup.get('offsite_rule')}`")
    lines.append("")
    lines.append("## Restore Strategy")
    lines.append("")
    restore = data.get("restore_strategy", {})
    for item in restore.get("restore_types", []):
        lines.append(f"- restore type: `{item}`")
    if restore.get("drill_policy_v1"):
        lines.append(f"- Drill policy: `{restore.get('drill_policy_v1')}`")
    if restore.get("promotion_rule"):
        lines.append(f"- Promotion rule: `{restore.get('promotion_rule')}`")
    for key, value in restore.get("rto_rpo", {}).items():
        lines.append(f"- `{key}` -> RTO `{value.get('rto')}` / RPO `{value.get('rpo')}`")
    lines.append("")
    lines.append("## Non-Goals V1")
    lines.append("")
    for item in data.get("non_goals_v1", []):
        lines.append(f"- `{item}`")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(REPORT_MD))


if __name__ == "__main__":
    main()
