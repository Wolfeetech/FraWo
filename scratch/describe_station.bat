ssh -i ~/.ssh/pve_ed25519 -o StrictHostKeyChecking=no root@100.69.179.87 "pct exec 130 -- bash -c \"cd /var/azuracast && docker compose exec -T web azuracast_cli dbal:run-sql 'DESCRIBE station;'\""
