echo "--- Checking running containers for Prometheus, Grafana, InfluxDB ---"
docker ps -a | grep -E "grafana|prometheus|influx|telegraf|exporter"
for ct in $(pct list | awk '{print $1}' | tail -n +2); do
    echo "--- CT $ct ---"
    pct exec $ct -- docker ps -a | grep -E "grafana|prometheus|influx|telegraf|exporter" 2>/dev/null || true
done

echo "--- Checking systemd services for monitoring ---"
systemctl list-units --type=service | grep -E "telegraf|prometheus|grafana|influx"
