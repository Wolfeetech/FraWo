#!/usr/bin/env bash
set -euo pipefail

PROXMOX_HOST="${PROXMOX_HOST:-proxmox}"
VM_IDS=(200 210 220 230)
CT_IDS=(100)

ssh "$PROXMOX_HOST" 'bash -s' <<'EOF'
set -euo pipefail

to_mb() {
  awk -v bytes="$1" 'BEGIN { printf "%.0f", bytes / 1024 / 1024 }'
}

host_total_mb=$(free -m | awk '/^Mem:/ {print $2}')
host_used_mb=$(free -m | awk '/^Mem:/ {print $3}')
host_avail_mb=$(free -m | awk '/^Mem:/ {print $7}')
host_cpu_count=$(nproc)

echo "host_total_mb=${host_total_mb}"
echo "host_used_mb=${host_used_mb}"
echo "host_available_mb=${host_avail_mb}"
echo "host_cpu_count=${host_cpu_count}"
echo

configured_total_mb=0

for id in 200 210 220 230; do
  cfg=$(qm config "$id")
  runtime=$(qm status "$id" --verbose)
  name=$(printf '%s\n' "$cfg" | awk -F': ' '/^name:/ {print $2}')
  cores=$(printf '%s\n' "$cfg" | awk -F': ' '/^cores:/ {print $2}')
  memory_mb=$(printf '%s\n' "$cfg" | awk -F': ' '/^memory:/ {print $2}')
  disk_gb=$(printf '%s\n' "$cfg" | awk -F'size=' '/^scsi0:/ {print $2}' | cut -d',' -f1)
  runtime_used_mb=$(to_mb "$(printf '%s\n' "$runtime" | awk -F': ' '/^mem:/ {print $2}')")
  runtime_free_mb=$(to_mb "$(printf '%s\n' "$runtime" | awk -F': ' '/^freemem:/ {print $2}')")
  used_pct=$(awk -v used="$runtime_used_mb" -v total="$memory_mb" 'BEGIN { if (total == 0) print 0; else printf "%.0f", used * 100 / total }')

  configured_total_mb=$((configured_total_mb + memory_mb))

  if [ "$used_pct" -ge 85 ]; then
    recommendation="keep_or_increase"
  elif [ "$used_pct" -le 45 ] && [ "$runtime_free_mb" -ge 1024 ]; then
    recommendation="downsize_candidate"
  else
    recommendation="keep_current"
  fi

  echo "vm_id=${id}"
  echo "vm_name=${name}"
  echo "vm_cores=${cores}"
  echo "vm_memory_mb=${memory_mb}"
  echo "vm_disk=${disk_gb}"
  echo "vm_runtime_used_mb=${runtime_used_mb}"
  echo "vm_runtime_free_mb=${runtime_free_mb}"
  echo "vm_used_pct=${used_pct}"
  echo "vm_recommendation=${recommendation}"
  echo
done

for id in 100; do
  cfg=$(pct config "$id")
  name=$(printf '%s\n' "$cfg" | awk -F': ' '/^hostname:/ {print $2}')
  cores=$(printf '%s\n' "$cfg" | awk -F': ' '/^cores:/ {print $2}')
  memory_mb=$(printf '%s\n' "$cfg" | awk -F': ' '/^memory:/ {print $2}')
  rootfs_size=$(printf '%s\n' "$cfg" | awk -F'size=' '/^rootfs:/ {print $2}')
  runtime_free_mb=$(pct exec "$id" -- free -m | awk '/^Mem:/ {print $4}')
  runtime_used_mb=$(pct exec "$id" -- free -m | awk '/^Mem:/ {print $3}')
  used_pct=$(awk -v used="$runtime_used_mb" -v total="$memory_mb" 'BEGIN { if (total == 0) print 0; else printf "%.0f", used * 100 / total }')

  configured_total_mb=$((configured_total_mb + memory_mb))

  if [ "$used_pct" -ge 85 ]; then
    recommendation="keep_or_increase"
  elif [ "$used_pct" -le 45 ] && [ "$runtime_free_mb" -ge 512 ]; then
    recommendation="downsize_candidate"
  else
    recommendation="keep_current"
  fi

  echo "ct_id=${id}"
  echo "ct_name=${name}"
  echo "ct_cores=${cores}"
  echo "ct_memory_mb=${memory_mb}"
  echo "ct_rootfs=${rootfs_size}"
  echo "ct_runtime_used_mb=${runtime_used_mb}"
  echo "ct_runtime_free_mb=${runtime_free_mb}"
  echo "ct_used_pct=${used_pct}"
  echo "ct_recommendation=${recommendation}"
  echo
done

echo "configured_guest_memory_mb=${configured_total_mb}"
echo "configured_guest_memory_pct_of_host=$(awk -v cfg="$configured_total_mb" -v host="$host_total_mb" 'BEGIN { if (host == 0) print 0; else printf "%.0f", cfg * 100 / host }')"

if [ "$configured_total_mb" -gt "$host_total_mb" ]; then
  echo "capacity_risk=overcommitted"
else
  echo "capacity_risk=within_host_ram"
fi
EOF
