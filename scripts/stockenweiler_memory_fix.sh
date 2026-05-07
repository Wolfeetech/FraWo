#!/bin/bash
#
# Stockenweiler Memory Crisis Fix
# Critical: Swap 99% (7.9Gi/8.0Gi)
# Affected: PBS (109), n8n (110), Vaultwarden (108), AdGuard (101)
#
# Run on: root@100.91.20.116 (Stockenweiler PVE)
# Date: 2026-05-05
#

set -e

echo "========================================="
echo "STOCKENWEILER MEMORY DIAGNOSTIC & FIX"
echo "========================================="
echo ""

# === PHASE 1: DIAGNOSTICS ===
echo "[PHASE 1] Collecting System Memory Status..."
echo ""

echo "--- Host Memory ---"
free -h
echo ""

echo "--- Swap Details ---"
swapon --show
echo ""

echo "--- Top Memory Consumers (Host) ---"
ps aux --sort=-%mem | head -20
echo ""

echo "--- Container/VM Memory Allocation ---"
pct list
qm list
echo ""

# === PHASE 2: CONTAINER ANALYSIS ===
echo ""
echo "[PHASE 2] Analyzing Container Memory Usage..."
echo ""

declare -A CONTAINERS=(
    [101]="AdGuard"
    [108]="Vaultwarden"
    [109]="PBS"
    [110]="n8n"
)

for CT_ID in "${!CONTAINERS[@]}"; do
    CT_NAME="${CONTAINERS[$CT_ID]}"
    echo "--- CT $CT_ID ($CT_NAME) ---"

    # Get current config
    echo "Current RAM config:"
    pct config $CT_ID | grep -E "memory|swap"

    # Get actual usage (if running)
    if pct status $CT_ID | grep -q running; then
        echo "Actual usage:"
        pct exec $CT_ID -- free -h 2>/dev/null || echo "Could not retrieve usage"

        echo "Top processes:"
        pct exec $CT_ID -- ps aux --sort=-%mem | head -10 2>/dev/null || echo "Could not retrieve processes"
    else
        echo "Status: NOT RUNNING"
    fi
    echo ""
done

# === PHASE 3: RECOMMENDATIONS ===
echo ""
echo "[PHASE 3] Memory Optimization Recommendations..."
echo ""

# Function to get current memory value
get_mem() {
    pct config $1 | grep "^memory:" | awk '{print $2}'
}

echo "Current Allocations:"
echo "-------------------"
for CT_ID in "${!CONTAINERS[@]}"; do
    CT_NAME="${CONTAINERS[$CT_ID]}"
    MEM=$(get_mem $CT_ID)
    echo "CT $CT_ID ($CT_NAME): ${MEM}MB"
done
echo ""

echo "Recommended Allocations:"
echo "-----------------------"
echo "CT 101 (AdGuard):    512MB  (lightweight DNS service)"
echo "CT 108 (Vaultwarden): 1024MB (password vault)"
echo "CT 109 (PBS):        2048MB (backup server - reduce from current)"
echo "CT 110 (n8n):        1024MB (workflow automation - reduce from current)"
echo ""

# === PHASE 4: OPTIONAL FIX ===
read -p "Apply recommended memory settings? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "[PHASE 4] Applying Memory Optimization..."
    echo ""

    # Stop containers before resizing
    echo "Stopping containers..."
    for CT_ID in "${!CONTAINERS[@]}"; do
        if pct status $CT_ID | grep -q running; then
            echo "Stopping CT $CT_ID..."
            pct stop $CT_ID
        fi
    done

    echo ""
    echo "Applying new memory limits..."

    # Apply new limits
    pct set 101 --memory 512 --swap 512
    echo "[OK] CT 101 (AdGuard): 512MB RAM + 512MB Swap"

    pct set 108 --memory 1024 --swap 1024
    echo "[OK] CT 108 (Vaultwarden): 1024MB RAM + 1024MB Swap"

    pct set 109 --memory 2048 --swap 2048
    echo "[OK] CT 109 (PBS): 2048MB RAM + 2048MB Swap"

    pct set 110 --memory 1024 --swap 1024
    echo "[OK] CT 110 (n8n): 1024MB RAM + 1024MB Swap"

    echo ""
    echo "Starting containers..."
    for CT_ID in "${!CONTAINERS[@]}"; do
        echo "Starting CT $CT_ID..."
        pct start $CT_ID
        sleep 2
    done

    echo ""
    echo "[SUCCESS] Memory optimization complete!"
    echo ""

    # Wait for services to stabilize
    echo "Waiting 30s for services to stabilize..."
    sleep 30

    # Show new status
    echo ""
    echo "New Memory Status:"
    free -h
    echo ""
    swapon --show

else
    echo ""
    echo "[SKIPPED] No changes applied. Manual commands:"
    echo ""
    echo "# Stop containers:"
    echo "pct stop 101 && pct stop 108 && pct stop 109 && pct stop 110"
    echo ""
    echo "# Apply new limits:"
    echo "pct set 101 --memory 512 --swap 512"
    echo "pct set 108 --memory 1024 --swap 1024"
    echo "pct set 109 --memory 2048 --swap 2048"
    echo "pct set 110 --memory 1024 --swap 1024"
    echo ""
    echo "# Start containers:"
    echo "pct start 101 && pct start 108 && pct start 109 && pct start 110"
    echo ""
fi

echo ""
echo "========================================="
echo "DIAGNOSTIC COMPLETE"
echo "========================================="
