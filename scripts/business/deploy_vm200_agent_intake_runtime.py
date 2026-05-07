#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import os
import shlex
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SSH_CONFIG = REPO_ROOT / "Codex" / "ssh_config"
ASSET_DIR = REPO_ROOT / "infrastructure" / "vm200_agent_intake"

REMOTE_TOOL_DIR = "/opt/homeserver2027/tools"
REMOTE_RUNNER_DIR = "/usr/local/sbin"
REMOTE_SYSTEMD_DIR = "/etc/systemd/system"
REMOTE_SECRET_DIR = "/root/.config/homeserver2027"

TOOL_FILES = {
    REPO_ROOT / "scripts" / "business" / "nextcloud_imap_alias_router.py": f"{REMOTE_TOOL_DIR}/nextcloud_imap_alias_router.py",
    REPO_ROOT / "scripts" / "business" / "odoo_rpc_client.py": f"{REMOTE_TOOL_DIR}/odoo_rpc_client.py",
    REPO_ROOT / "scripts" / "business" / "odoo_agent_intake_bridge.py": f"{REMOTE_TOOL_DIR}/odoo_agent_intake_bridge.py",
}

RUNTIME_FILES = {
    ASSET_DIR / "nextcloud_alias_router_runner.sh": f"{REMOTE_RUNNER_DIR}/nextcloud_alias_router_runner.sh",
    ASSET_DIR / "odoo_agent_intake_runner.sh": f"{REMOTE_RUNNER_DIR}/odoo_agent_intake_runner.sh",
    ASSET_DIR / "hs27-nextcloud-alias-router.service": f"{REMOTE_SYSTEMD_DIR}/hs27-nextcloud-alias-router.service",
    ASSET_DIR / "hs27-nextcloud-alias-router.timer": f"{REMOTE_SYSTEMD_DIR}/hs27-nextcloud-alias-router.timer",
    ASSET_DIR / "hs27-odoo-agent-intake.service": f"{REMOTE_SYSTEMD_DIR}/hs27-odoo-agent-intake.service",
    ASSET_DIR / "hs27-odoo-agent-intake.timer": f"{REMOTE_SYSTEMD_DIR}/hs27-odoo-agent-intake.timer",
}

EXAMPLE_FILES = {
    ASSET_DIR / "mail_alias_router.env.example": f"{REMOTE_SECRET_DIR}/mail_alias_router.env.example",
    ASSET_DIR / "odoo_agent_rpc.env.example": f"{REMOTE_SECRET_DIR}/odoo_agent_rpc.env.example",
}


def build_remote_command(vmid: int, script: str, *, pass_stdin: bool = False) -> str:
    parts = ["qm", "guest", "exec", str(vmid)]
    if pass_stdin:
        parts.extend(["--pass-stdin", "1"])
    parts.extend(["--", "bash", "-lc", script])
    return " ".join(shlex.quote(part) for part in parts)


def run_ssh(ssh_host: str, remote_command: str, *, stdin: bytes | None = None) -> subprocess.CompletedProcess[str]:
    command = ["ssh", "-F", str(SSH_CONFIG), ssh_host, remote_command]
    return subprocess.run(
        command,
        input=stdin,
        text=False,
        capture_output=True,
        check=False,
    )


def require_ok(result: subprocess.CompletedProcess[bytes], context: str) -> None:
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace").strip()
        stdout = result.stdout.decode(errors="replace").strip()
        details = stderr or stdout or f"exit code {result.returncode}"
        raise RuntimeError(f"{context} fehlgeschlagen: {details}")


def push_file(ssh_host: str, vmid: int, local_path: Path, remote_path: str, mode: str) -> None:
    payload = base64.b64encode(local_path.read_bytes())
    script = (
        "set -euo pipefail; "
        f"mkdir -p {shlex.quote(os.path.dirname(remote_path))}; "
        f"base64 -d > {shlex.quote(remote_path)}; "
        f"chmod {mode} {shlex.quote(remote_path)}"
    )
    result = run_ssh(ssh_host, build_remote_command(vmid, script, pass_stdin=True), stdin=payload)
    require_ok(result, f"Push {local_path.name} -> {remote_path}")


def run_guest_shell(ssh_host: str, vmid: int, script: str) -> str:
    result = run_ssh(ssh_host, build_remote_command(vmid, script))
    require_ok(result, "Guest-Shell")
    return result.stdout.decode(errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Staged den VM-200 agent intake runtime via qga.")
    parser.add_argument("--ssh-host", default="pve-anker")
    parser.add_argument("--vmid", type=int, default=200)
    parser.add_argument("--enable-timers", action="store_true")
    parser.add_argument("--write-example-env", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    for local_path, remote_path in TOOL_FILES.items():
        push_file(args.ssh_host, args.vmid, local_path, remote_path, "0755")

    for local_path, remote_path in RUNTIME_FILES.items():
        mode = "0755" if remote_path.startswith(REMOTE_RUNNER_DIR) else "0644"
        push_file(args.ssh_host, args.vmid, local_path, remote_path, mode)

    run_guest_shell(
        args.ssh_host,
        args.vmid,
        "set -euo pipefail; "
        f"mkdir -p {shlex.quote(REMOTE_SECRET_DIR)}; "
        f"chmod 700 {shlex.quote(REMOTE_SECRET_DIR)}; "
        "systemctl daemon-reload",
    )

    if args.write_example_env:
        for local_path, remote_path in EXAMPLE_FILES.items():
            push_file(args.ssh_host, args.vmid, local_path, remote_path, "0600")

    if args.enable_timers:
        run_guest_shell(
            args.ssh_host,
            args.vmid,
            "set -euo pipefail; "
            "systemctl enable hs27-nextcloud-alias-router.timer hs27-odoo-agent-intake.timer",
        )

    verification = run_guest_shell(
        args.ssh_host,
        args.vmid,
        "set -euo pipefail; "
        "echo '=== files ==='; "
        f"find {shlex.quote(REMOTE_TOOL_DIR)} {shlex.quote(REMOTE_RUNNER_DIR)} {shlex.quote(REMOTE_SYSTEMD_DIR)} "
        "\\( -name 'nextcloud_imap_alias_router.py' -o -name 'odoo_rpc_client.py' -o -name 'odoo_agent_intake_bridge.py' "
        "-o -name 'nextcloud_alias_router_runner.sh' -o -name 'odoo_agent_intake_runner.sh' "
        "-o -name 'hs27-nextcloud-alias-router.service' -o -name 'hs27-nextcloud-alias-router.timer' "
        "-o -name 'hs27-odoo-agent-intake.service' -o -name 'hs27-odoo-agent-intake.timer' \\) -print | sort; "
        "echo '=== units ==='; "
        "systemctl list-unit-files | grep -E 'hs27-nextcloud-alias-router|hs27-odoo-agent-intake' || true",
    )
    print(verification.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
