#!/bin/bash
CONFIG="/var/lib/docker/volumes/nextcloud_nextcloud/_data/config/config.php"
# Add overwritehost
grep -q "overwritehost" $CONFIG || sed -i "/'overwriteprotocol'/a \  'overwritehost' => 'cloud.hs27.internal'," $CONFIG
# Ensure trusted_proxies covers the subnet
sed -i "s/'trusted_proxies' => array([^)]*)/'trusted_proxies' => array('10.1.0.0\/24', '100.64.0.0\/10', '127.0.0.1')/g" $CONFIG
# Add overwritecondaddr to avoid loops if proxy IP matches
grep -q "overwritecondaddr" $CONFIG || sed -i "/'overwritehost'/a \  'overwritecondaddr' => '^10\.1\.0\.20$'," $CONFIG
