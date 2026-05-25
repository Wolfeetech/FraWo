#!/bin/bash
pct exec 130 -- bash -c "cd /var/azuracast && docker compose exec -T web azuracast_cli dbal:run-sql \"DESCRIBE station;\""
