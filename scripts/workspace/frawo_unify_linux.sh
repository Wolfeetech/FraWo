#!/bin/bash
# frawo_unify_linux.sh - Unify FraWo workspace paths on Linux nodes

CANONICAL_ROOT="/srv/FraWo"
LEGACY_ROOT="/root/FraWo"

echo "========================================="
echo "   FRAWO WORKSPACE UNIFICATION (Linux)"
echo "========================================="

# 1. Ensure Canonical Root exists
if [ ! -d "$CANONICAL_ROOT" ]; then
    echo "[1/2] Creating canonical root: $CANONICAL_ROOT"
    mkdir -p "$CANONICAL_ROOT"
fi

# 2. Link Legacy/Root path
echo "[2/2] Establishing Link: $LEGACY_ROOT -> $CANONICAL_ROOT"
if [ -L "$LEGACY_ROOT" ]; then
    rm "$LEGACY_ROOT"
elif [ -d "$LEGACY_ROOT" ]; then
    mv "$LEGACY_ROOT" "${LEGACY_ROOT}.old.$(date +%Y%m%d)"
fi

ln -sfn "$CANONICAL_ROOT" "$LEGACY_ROOT"

echo "DONE. Canonical path is $CANONICAL_ROOT"
