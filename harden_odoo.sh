qm guest exec 220 -- bash -c "echo 'proxy_mode = True' >> /opt/homeserver2027/stacks/odoo/odoo.conf"
qm guest exec 220 -- docker restart odoo_web_1

pct exec 100 -- bash -c "cat << 'CADDY' >> /opt/homeserver2027/stacks/toolbox-network/Caddyfile

# --- SECURE PUBLIC ODOO WEBSITE ---
http://frawo-tech.de, https://frawo-tech.de {
  redir https://www.frawo-tech.de{uri} 301
}

http://www.frawo-tech.de, https://www.frawo-tech.de {
  @blocked path /web/login /web/database/* /web/session/logout
  respond @blocked \"403 Forbidden - Zero Trust Security\" 403

  reverse_proxy 10.1.0.22:8069 {
    header_up X-Forwarded-Proto https
  }
}
CADDY"
pct exec 100 -- docker restart toolbox-network-caddy-1
