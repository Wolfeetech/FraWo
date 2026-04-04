#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "cicd_delivery_factory"
REPORT_JSON = ARTIFACT_DIR / "latest_preflight.json"
REPORT_MD = ARTIFACT_DIR / "latest_preflight.md"
PLAN_PATH = ROOT / "CI_CD_DELIVERY_FACTORY_PLAN.md"
UCG_PATH = ROOT / "UCG_NETWORK_ARCHITECTURE.md"
CATALOG_PATH = ROOT / "deployment" / "factory" / "apps" / "catalog.json"
GHCR_CONTRACT_PATH = ROOT / "deployment" / "factory" / "contracts" / "GHCR_CONTRACT.md"
SECRET_CONTRACT_PATH = ROOT / "deployment" / "factory" / "contracts" / "SECRET_ENV_CONTRACT.md"
DEPLOY_BUNDLE_PATH = ROOT / "deployment" / "factory" / "apps" / "radio-player-frontend" / "compose.yaml"
COOLIFY_HOST_SELECTION_PATH = ROOT / "deployment" / "coolify" / "COOLIFY_HOST_SELECTION.md"


def run_cmd(argv: list[str], timeout: int = 30) -> tuple[int, str, str]:
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def git_origin() -> str:
    code, out, _ = run_cmd(["git", "-C", str(ROOT), "remote", "get-url", "origin"])
    return out if code == 0 else ""


def find_matches(names: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for path in ROOT.rglob("*"):
        if any(part == ".git" for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.name in names:
            matches.append(path.relative_to(ROOT).as_posix())
    return sorted(matches)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    origin = git_origin()
    workflow_files = find_matches(("Jenkinsfile", ".gitlab-ci.yml",))
    if (ROOT / ".github").exists():
        workflow_files.extend([p.relative_to(ROOT).as_posix() for p in (ROOT / ".github").rglob("*") if p.is_file()])
    if (ROOT / ".gitea").exists():
        workflow_files.extend([p.relative_to(ROOT).as_posix() for p in (ROOT / ".gitea").rglob("*") if p.is_file()])
    workflow_files = sorted(set(workflow_files))

    dockerfiles = find_matches(("Dockerfile", "Containerfile"))
    compose_templates = [
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob("docker-compose.yml.j2")
        if p.is_file() and ".git" not in p.parts
    ]

    plan_text = read_text(PLAN_PATH)
    ucg_text = read_text(UCG_PATH)
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    apps = catalog.get("apps", [])
    ready_apps = [app for app in apps if app.get("factory_deploy_ready_now")]

    verified_facts = []
    open_prerequisites = []
    rejected_assumptions = []

    if origin:
        verified_facts.append(f"Git remote is configured: `{origin}`.")
    if "github.com" in origin.lower():
        verified_facts.append("Current repo host is GitHub, so a thin GitHub Actions wrapper is a factual option.")
    if "10.2.0.0/24" in ucg_text and "10.3.0.0/24" in ucg_text:
        verified_facts.append("Anker DMZ target subnets are already canonical in UCG_NETWORK_ARCHITECTURE.md: VLAN 102 `10.2.0.0/24`, VLAN 103 `10.3.0.0/24`.")
    if compose_templates:
        verified_facts.append(f"Repo already contains `{len(compose_templates)}` stack compose templates, but they are runtime templates, not standalone OCI app definitions.")
    if GHCR_CONTRACT_PATH.exists() and SECRET_CONTRACT_PATH.exists():
        verified_facts.append("GHCR registry contract and env/secret contract docs now exist for the first reference app.")
    if DEPLOY_BUNDLE_PATH.exists():
        verified_facts.append("A neutral compose deploy bundle now exists for the first reference app.")
    if COOLIFY_HOST_SELECTION_PATH.exists():
        verified_facts.append("Coolify host selection contract now exists and keeps the controller out of the DMZ and off the hypervisor host itself.")
    if dockerfiles:
        verified_facts.append(f"Repo now contains `{len(dockerfiles)}` verified Dockerfile/Containerfile artifact for factory build work.")
    if ready_apps:
        verified_facts.append(f"App catalog now contains `{len(ready_apps)}` factory-deploy-ready reference app candidate.")
    if not dockerfiles:
        rejected_assumptions.append("There is currently no verified Dockerfile/Containerfile in the repo for a first factory-managed app build.")
    if not ready_apps:
        rejected_assumptions.append("There is currently no verified app in the catalog that is factory-deploy-ready right now.")
    if not workflow_files:
        rejected_assumptions.append("There was no existing CI workflow file in the repo before this preflight.")

    open_prerequisites.extend(
        [
            "OCI registry is still undecided.",
            "Coolify management host is still undecided.",
            "Stockenweiler secondary DMZ subnet and runtime node are not yet fixed facts.",
            "Prod secret distribution model for dev/prod is not yet encoded in the repo.",
        ]
    )
    if not ready_apps:
        open_prerequisites.append("No separate standalone public app artifact exists yet for the first real factory deployment.")

    implementation_scope_now = [
        "Repo-side factory scaffolding is in scope now.",
        "A thin GitHub Actions validation workflow is in scope because GitHub origin is verified.",
        "Actual Coolify deployment, registry setup, DMZ node provisioning, and public cutover remain gated infra and are not in scope now.",
    ]

    payload = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "origin": origin,
        "workflow_file_count": len(workflow_files),
        "workflow_files": workflow_files,
        "dockerfile_count": len(dockerfiles),
        "dockerfiles": dockerfiles,
        "compose_template_count": len(compose_templates),
        "compose_templates": compose_templates,
        "catalog_app_count": len(apps),
        "factory_ready_app_count": len(ready_apps),
        "verified_facts": verified_facts,
        "rejected_assumptions": rejected_assumptions,
        "open_prerequisites": open_prerequisites,
        "implementation_scope_now": implementation_scope_now,
        "summary": {
            "repo_host": "github" if "github.com" in origin.lower() else "other_or_unknown",
            "factory_ready_app_count": len(ready_apps),
            "workflow_file_count_before_factory": len([w for w in workflow_files if "delivery-factory" not in w]),
            "oci_build_artifact_present": len(dockerfiles) > 0,
            "safe_scope_now": "repo_side_factory_only",
        },
    }

    lines: list[str] = []
    lines.append("# CI/CD Delivery Factory Preflight")
    lines.append("")
    lines.append(f"- Generated at: `{payload['generated_at']}`")
    lines.append(f"- Git origin: `{origin or 'unknown'}`")
    lines.append(f"- Existing workflow files: `{len(workflow_files)}`")
    lines.append(f"- Dockerfiles/Containerfiles: `{len(dockerfiles)}`")
    lines.append(f"- Stack compose templates: `{len(compose_templates)}`")
    lines.append(f"- Factory-ready apps now: `{len(ready_apps)}` / `{len(apps)}`")
    lines.append("")
    lines.append("## Verified Facts")
    lines.append("")
    for item in verified_facts:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Rejected Assumptions")
    lines.append("")
    for item in rejected_assumptions:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Open Prerequisites")
    lines.append("")
    for item in open_prerequisites:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Safe Scope Now")
    lines.append("")
    for item in implementation_scope_now:
        lines.append(f"- {item}")
    lines.append("")

    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(REPORT_MD))


if __name__ == "__main__":
    main()
