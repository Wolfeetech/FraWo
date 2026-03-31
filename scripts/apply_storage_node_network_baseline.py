from __future__ import annotations

import pathlib
import socket
import subprocess

import jinja2
import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
HOSTS_PATH = REPO_ROOT / "ansible" / "inventory" / "hosts.yml"
GROUP_VARS_PATH = REPO_ROOT / "ansible" / "inventory" / "group_vars" / "all" / "main.yml"
TEMPLATE_PATH = REPO_ROOT / "ansible" / "templates" / "storage" / "smb.conf.j2"


def load_yaml(path: pathlib.Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def find_host(node: object, host_key: str) -> dict[str, object] | None:
    if isinstance(node, dict):
        hosts = node.get("hosts")
        if isinstance(hosts, dict) and host_key in hosts:
            value = hosts[host_key]
            return value if isinstance(value, dict) else None
        for value in node.values():
            found = find_host(value, host_key)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = find_host(value, host_key)
            if found is not None:
                return found
    return None


def render_template(path: pathlib.Path, context: dict[str, object]) -> str:
    env = jinja2.Environment(undefined=jinja2.StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    template = env.from_string(path.read_text(encoding="utf-8"))
    return template.render(**context).rstrip() + "\n"


def run_remote_script(script: str) -> str:
    script = script.replace("\r\n", "\n").replace("\r", "\n")
    result = subprocess.run(
        ["ssh", "hs27-proxmox", "bash", "-s"],
        input=script.encode("utf-8"),
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        stdout = result.stdout.decode("utf-8", errors="replace").strip()
        raise RuntimeError(stderr or stdout or f"remote rc={result.returncode}")
    return result.stdout.decode("utf-8", errors="replace")


def check_tcp(host: str, port: int, timeout: float = 5.0) -> None:
    with socket.create_connection((host, port), timeout=timeout):
        return


def main() -> int:
    inventory = load_yaml(HOSTS_PATH)
    host = find_host(inventory, "storage_node")
    if not host:
        raise SystemExit("storage_node host missing in inventory")
    group_vars = load_yaml(GROUP_VARS_PATH)
    if not isinstance(group_vars, dict):
        raise SystemExit("group vars invalid")

    storage = group_vars["homeserver_storage_node"]
    context = {
        "homeserver_storage_node": storage,
        "storage_shares": storage["smb_shares"],
        "storage_share_user": storage["smb_user"],
    }
    smb_conf = render_template(TEMPLATE_PATH, context)
    vmid = str(host["proxmox_vmid"])
    ansible_host = str(host["ansible_host"])

    remote_script = f"""set -euo pipefail
cat > /tmp/hs27_storage_smb.conf <<'EOF'
{smb_conf}EOF
cat /tmp/hs27_storage_smb.conf | pct exec {vmid} -- tee /etc/samba/smb.conf >/dev/null
rm -f /tmp/hs27_storage_smb.conf
pct exec {vmid} -- systemctl restart smbd nmbd
pct exec {vmid} -- systemctl disable --now ssh || true
pct exec {vmid} -- systemctl disable --now ssh.socket || true
pct exec {vmid} -- sh -lc 'systemctl is-enabled ssh >/dev/null 2>&1 && echo ssh_enabled=yes || echo ssh_enabled=no'
pct exec {vmid} -- sh -lc 'systemctl is-enabled ssh.socket >/dev/null 2>&1 && echo ssh_socket_enabled=yes || echo ssh_socket_enabled=no'
"""

    output = run_remote_script(remote_script)
    check_tcp(ansible_host, 445)

    print(output.strip())
    print(f"storage_node_smb_host={ansible_host}")
    print("storage_node_tcp_445=reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
