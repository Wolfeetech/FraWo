from __future__ import annotations

import pathlib
import subprocess
import urllib.request

import jinja2
import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
HOSTS_PATH = REPO_ROOT / "ansible" / "inventory" / "hosts.yml"
HOST_VARS_PATH = REPO_ROOT / "ansible" / "inventory" / "host_vars" / "vaultwarden.yml"
TEMPLATE_PATH = REPO_ROOT / "ansible" / "templates" / "stacks" / "vaultwarden" / "docker-compose.yml.j2"


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


def verify_http(url: str) -> tuple[int, str]:
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read().decode("utf-8", errors="replace").strip()
        return response.status, body


def main() -> int:
    inventory = load_yaml(HOSTS_PATH)
    host = find_host(inventory, "vaultwarden")
    if not host:
        raise SystemExit("vaultwarden host missing in inventory")
    vars_data = load_yaml(HOST_VARS_PATH)
    if not isinstance(vars_data, dict):
        raise SystemExit("vaultwarden host vars invalid")

    context = dict(vars_data)
    compose_root = str(context["vaultwarden_compose_root"])
    vmid = str(host["proxmox_vmid"])
    ansible_host = str(host["ansible_host"])
    port = str(context["compose_http_port"])
    compose_content = render_template(TEMPLATE_PATH, context)

    # Use a local temp file push via the Proxmox host to avoid quoting the compose body into pct exec.
    temp_name = f"/tmp/hs27_vaultwarden_compose_{vmid}.yml"
    remote_script = f"""set -euo pipefail
cat > {temp_name} <<'EOF'
{compose_content}EOF
pct exec {vmid} -- mkdir -p {compose_root}
cat {temp_name} | pct exec {vmid} -- tee {compose_root}/docker-compose.yml >/dev/null
rm -f {temp_name}
pct exec {vmid} -- systemctl disable --now ssh || true
pct exec {vmid} -- systemctl disable --now ssh.socket || true
pct exec {vmid} -- sh -lc 'cd {compose_root} && if docker compose version >/dev/null 2>&1; then docker compose up -d >/dev/null; else docker-compose up -d >/dev/null; fi'
pct exec {vmid} -- sh -lc 'systemctl is-enabled ssh >/dev/null 2>&1 && echo ssh_enabled=yes || echo ssh_enabled=no'
pct exec {vmid} -- sh -lc 'systemctl is-enabled ssh.socket >/dev/null 2>&1 && echo ssh_socket_enabled=yes || echo ssh_socket_enabled=no'
"""

    output = run_remote_script(remote_script)
    status, body = verify_http(f"http://{ansible_host}:{port}/alive")

    print(output.strip())
    print(f"vaultwarden_compose_root={compose_root}")
    print(f"vaultwarden_bind={context['compose_http_bind']}:{port}")
    print(f"vaultwarden_alive_status={status}")
    print(f"vaultwarden_alive_body={body}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
