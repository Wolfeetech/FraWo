# Monitoring Stack — frawo-docker-1
**Stand: 2026-05-30 | Alle 6 Targets UP**

## Prometheus Targets

| Job | Host | Status |
|-----|------|--------|
| node-frawo-docker-1 | node-exporter:9100 | ✅ |
| node-pve-anker | 100.69.179.87:9100 | ✅ |
| node-radio | 100.78.88.33:9100 | ✅ |
| node-studiopc | 100.98.31.60:9182 | ✅ |
| pve-anker | pve-exporter:9221 | ✅ VM/CT Metriken |
| azuracast-stats | 100.78.88.33:9100 | ✅ |

## Services

- **Prometheus**: Port 9091, Config: `~/stacks/monitoring/prometheus.yml`
- **Grafana**: Port 3001, Login: admin / (Vault: Grafana — Admin)
- **pve-exporter**: monitoring_default Netz (172.20.0.5:9221)
  - PVE API Token: `root@pam!prometheus-exporter` (Vault speichern!)
  - Config: `~/stacks/monitoring/pve-exporter.yml`

## Grafana Dashboards (noch zu importieren)

1. Node Exporter Full: ID **1860** (Grafana.com)
2. Proxmox VE: ID **10347** (Grafana.com)

Import: Grafana → Dashboards → Import → ID eingeben → Datasource: Prometheus

## Nächste Schritte (T329)

- Alerting: Node down → Telegram @ServAssi_bot
- Backup-Alert: n8n Workflow (T324, bereits gebaut)
