#!/bin/bash
CSS_URL=$(qm guest exec 220 -- bash -c "curl -s http://localhost:8069 | grep -oE '/web/assets/[^\"]*web.assets_frontend.min.css'" | grep -oE '/web/assets/.*\.css' | head -n 1)
echo "CSS URL: $CSS_URL"
if [ -n "$CSS_URL" ]; then
    HAS_FW=$(qm guest exec 220 -- bash -c "curl -s http://localhost:8069$CSS_URL | grep -o 'fw-hero'")
    if [[ "$HAS_FW" == *"fw-hero"* ]]; then
        echo "CSS contains fw-hero"
    else
        echo "CSS DOES NOT contain fw-hero"
    fi
else
    echo "No CSS URL found."
fi
