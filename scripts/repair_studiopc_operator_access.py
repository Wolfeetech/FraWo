#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import os
import shlex
from pathlib import Path

import paramiko


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Distribute the StudioPC operator SSH public key to core Homeserver nodes via Proxmox."
    )
    parser.add_argument(
        "--public-key",
        default=str(Path.home() / ".ssh" / "hs27_ops_ed25519.pub"),
        help="StudioPC operator public key to distribute.",
    )
    parser.add_argument(
        "--proxmox-host",
        default="192.168.2.10",
        help="Proxmox host used as the repair pivot.",
    )
    parser.add_argument(
        "--proxmox-user",
        default="root",
        help="SSH user for the Proxmox pivot host.",
    )
    parser.add_argument(
        "--proxmox-key",
        default=str(Path.home() / ".ssh" / "pve_ed25519"),
        help="SSH private key for the Proxmox pivot host.",
    )
    parser.add_argument(
        "--surface-host",
        default="100.106.67.127",
        help="Surface Go host to repair directly.",
    )
    parser.add_argument(
        "--surface-user",
        default="frawo",
        help="Surface Go admin user for direct SSH access.",
    )
    parser.add_argument(
        "--surface-password-env",
        default="HS27_SURFACE_PASSWORD",
        help="Environment variable that contains the Surface Go password.",
    )
    return parser.parse_args()


class Remote:
    def __init__(self, host: str, user: str, key_file: str) -> None:
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            host,
            username=user,
            key_filename=key_file,
            timeout=20,
            banner_timeout=20,
            auth_timeout=20,
        )

    def run(self, command: str, check: bool = True) -> tuple[int, str, str]:
        stdin, stdout, stderr = self.client.exec_command(command)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        if check and code != 0:
            raise RuntimeError(f"command failed ({code}): {command}\nout={out}\nerr={err}")
        return code, out, err

    def close(self) -> None:
        self.client.close()


class PasswordRemote:
    def __init__(self, host: str, user: str, password: str) -> None:
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            host,
            username=user,
            password=password,
            timeout=20,
            banner_timeout=20,
            auth_timeout=20,
        )

    def run(self, command: str, check: bool = True) -> tuple[int, str, str]:
        stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        if check and code != 0:
            raise RuntimeError(f"command failed ({code}): {command}\nout={out}\nerr={err}")
        return code, out, err

    def close(self) -> None:
        self.client.close()


def bash_quote(command: str) -> str:
    return shlex.quote(command)


def ensure_key_snippet(pub_b64: str, user: str, home: str) -> str:
    return (
        f"pub=$(printf %s {shlex.quote(pub_b64)} | base64 -d); "
        f"install -d -m 700 -o {user} -g {user} {home}/.ssh; "
        f"touch {home}/.ssh/authorized_keys; "
        f"chown {user}:{user} {home}/.ssh/authorized_keys; "
        f"chmod 600 {home}/.ssh/authorized_keys; "
        f"grep -qxF \"$pub\" {home}/.ssh/authorized_keys || echo \"$pub\" >> {home}/.ssh/authorized_keys; "
        f"chown {user}:{user} {home}/.ssh/authorized_keys; "
        f"tail -n 1 {home}/.ssh/authorized_keys"
    )


def ensure_root_key_snippet(pub_b64: str) -> str:
    return (
        f"pub=$(printf %s {shlex.quote(pub_b64)} | base64 -d); "
        "install -d -m 700 /root/.ssh; "
        "touch /root/.ssh/authorized_keys; "
        "chmod 600 /root/.ssh/authorized_keys; "
        "grep -qxF \"$pub\" /root/.ssh/authorized_keys || echo \"$pub\" >> /root/.ssh/authorized_keys; "
        "tail -n 1 /root/.ssh/authorized_keys"
    )


def main() -> None:
    args = parse_args()
    pub_key_path = Path(args.public_key)
    proxmox_key_path = Path(args.proxmox_key)

    pub_key = pub_key_path.read_text(encoding="utf-8").strip()
    if not pub_key.startswith("ssh-"):
        raise SystemExit(f"invalid public key in {pub_key_path}")
    if not proxmox_key_path.exists():
        raise SystemExit(f"missing proxmox key: {proxmox_key_path}")

    pub_b64 = base64.b64encode(pub_key.encode("utf-8")).decode("ascii")
    remote = Remote(args.proxmox_host, args.proxmox_user, str(proxmox_key_path))

    try:
        # Proxmox root
        _, out, _ = remote.run(f"bash -lc {bash_quote(ensure_root_key_snippet(pub_b64))}")
        print("proxmox_operator_key=ok")
        print(out.strip())

        # Toolbox root in CT100
        pct_cmd = f"pct exec 100 -- bash -lc {bash_quote(ensure_root_key_snippet(pub_b64))}"
        _, out, _ = remote.run(pct_cmd)
        print("toolbox_operator_key=ok")
        print(out.strip())

        # Business VMs via QGA
        for vmid in (200, 220, 230):
            guest_cmd = ensure_key_snippet(pub_b64, "wolf", "/home/wolf")
            cmd = f"qm guest exec {vmid} -- bash -lc {bash_quote(guest_cmd)}"
            _, out, _ = remote.run(cmd)
            print(f"vm_{vmid}_operator_key=ok")
            print(out.strip())

        # PBS only if running
        _, out, _ = remote.run("qm status 240", check=False)
        if "status: running" in out:
            guest_cmd = ensure_root_key_snippet(pub_b64)
            cmd = f"qm guest exec 240 -- bash -lc {bash_quote(guest_cmd)}"
            _, out, _ = remote.run(cmd)
            print("pbs_operator_key=ok")
            print(out.strip())
        else:
            print("pbs_operator_key=skipped_vm_stopped")
    finally:
        remote.close()

    surface_password = os.environ.get(args.surface_password_env, "")
    if surface_password:
        surface = PasswordRemote(args.surface_host, args.surface_user, surface_password)
        try:
            cmd = ensure_key_snippet(pub_b64, args.surface_user, f"/home/{args.surface_user}")
            _, out, _ = surface.run(f"bash -lc {bash_quote(cmd)}")
            print("surface_operator_key=ok")
            print(out.strip())
        finally:
            surface.close()
    else:
        print(f"surface_operator_key=skipped_missing_env:{args.surface_password_env}")


if __name__ == "__main__":
    main()
