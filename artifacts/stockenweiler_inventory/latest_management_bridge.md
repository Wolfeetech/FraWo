# Stockenweiler Management Bridge

- generated_at: `2026-03-31 16:16:26`
- bridge_state: `pending_login`
- ensure_access_returncode: `0`
- prepare_bridge_returncode: `999`
- check_bridge_returncode: `999`

## Summary

- Bridge is prepared and waiting only for Tailscale login approval.
- current_auth_url: `https://login.tailscale.com/a/14bca4f701de61`
- next_action: Open https://login.tailscale.com/a/14bca4f701de61 in a browser and complete the Tailscale login for stockenweiler-pve.

## Notes

- Primary target bridge: Tailscale subnet-router on stockenweiler-pve for 192.168.178.0/24.
- Current safe fallback: stock-pve SSH over toolbox-backed userspace WireGuard.
- Do not enable a blind site marriage or service migration from this script.
