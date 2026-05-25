scp -i ~/.ssh/pve_ed25519 -o StrictHostKeyChecking=no scratch\azuracast_update.sql root@100.69.179.87:/tmp/
ssh -i ~/.ssh/pve_ed25519 -o StrictHostKeyChecking=no root@100.69.179.87 "pct push 130 /tmp/azuracast_update.sql /var/azuracast/update.sql"
ssh -i ~/.ssh/pve_ed25519 -o StrictHostKeyChecking=no root@100.69.179.87 "pct exec 130 -- bash -c 'cd /var/azuracast && docker compose exec -T web azuracast_cli dbal:run-sql --no-interaction < update.sql'"
