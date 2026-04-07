#!/bin/bash
for ip in 10.1.0.20 10.1.0.21 10.1.0.22 10.1.0.23 10.1.0.26; do
  echo "=== $ip ==="
  ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=5 root@$ip 'grep nameserver /etc/resolv.conf && ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "[INTERNET OK]" || echo "[NO INTERNET]"'
done
