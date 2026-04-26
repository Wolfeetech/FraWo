#!/bin/bash
CONFIG_FILE="/var/lib/docker/volumes/nextcloud_nextcloud/_data/config/config.php"
# Add cloud.frawo-tech.de to trusted_domains
sed -i "s/1 => '192.168.2.21',/1 => '192.168.2.21',\n    2 => 'cloud.frawo-tech.de',/" "$CONFIG_FILE"
