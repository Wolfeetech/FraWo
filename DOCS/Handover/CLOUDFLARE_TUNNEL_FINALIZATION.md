# Handover Guide: Cloudflare Tunnel Production Deployment

This guide describes the final steps to transition the FraWo Public Edge from the ephemeral verification tunnel ("Alpha") to a permanent, production-grade service on VM 220.

## Preparation Status

- [x] Odoo service verified reachable via local tunnel.
- [x] Odoo hardened: the master password was set outside the repository and is intentionally not documented here.
- [x] Edge VM (220) staged with `docker-compose.public-edge.yml`.

---

## Final Activation Steps

### 1. Close the Alpha Tunnel
On your workstation, terminate the ephemeral tunnel process:
- Stop the running PowerShell script (`start_alpha_tunnel_local.ps1`) or close the terminal window where `cloudflared` is running.

### 2. Inject Production Token
Once you have the `TunnelToken` from the Cloudflare Dashboard:
1. SSH into the Proxmox host or VM 220.
2. Navigate to: `/opt/homeserver2027/stacks/odoo/`
3. Edit `docker-compose.public-edge.yml`.
4. Replace the template token with your actual value:

```yaml
services:
  tunnel:
    image: cloudflare/cloudflared:latest
    command: tunnel --no-autoupdate run
    environment:
      - TUNNEL_TOKEN=YOUR_PRODUCTION_TOKEN_HERE
```

### 3. Deploy Persistent Service
Run the following command within the `/opt/homeserver2027/stacks/odoo/` directory:

```bash
docker compose -f docker-compose.yml -f docker-compose.public-edge.yml up -d
```

### 4. Finalize DNS (Cloudflare Dashboard)
1. Ensure your Cloudflare Tunnel is configured to route traffic for `frawo-tech.de` to `http://odoo:8069`.
2. Verify that the DNS records in Cloudflare point `frawo-tech.de` to your tunnel CNAME.

---

## Security Check
The Odoo instance is protected with the operator-held master password that was set manually outside the repository.
Any database operations such as restore, delete, or backup require that secret.

Do not document the password in Markdown, scripts, or handover notes.

> [!TIP]
> You can safely archive `artifacts/repo_consolidation/` after confirming the migrated reports are no longer needed locally.
