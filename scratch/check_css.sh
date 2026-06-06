#!/bin/bash
CSS_URL=$(qm guest exec 220 -- bash -c "curl -s http://localhost:8069 | grep -oE '/web/assets/[^\"]*web.assets_frontend.min.css'" | grep -oE '/web/assets/.*\.css' | head -n 1)
echo "CSS URL: $CSS_URL"
if [ -n "$CSS_URL" ]; then
    qm guest exec 220 -- bash -c "curl -s http://localhost:8069$CSS_URL | grep -o 'fw-'"
else
    echo "No CSS URL found."
fi
