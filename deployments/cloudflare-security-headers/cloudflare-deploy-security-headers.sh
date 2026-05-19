#!/bin/bash
# Cloudflare Security Headers Deployment Script
# Verwendet Cloudflare API um Transform Rules automatisch zu erstellen

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cloudflare Security Headers Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# API Credentials abfragen
echo -e "${YELLOW}Cloudflare API Credentials benötigt:${NC}"
echo ""
echo "1. Login zu Cloudflare Dashboard: https://dash.cloudflare.com/"
echo "2. My Profile → API Tokens → Create Token"
echo "3. Template: Edit zone DNS + Transform Rules"
echo "4. Zone Resources: Include → Specific zone → frawo-tech.de"
echo ""

read -p "Cloudflare API Token: " CF_API_TOKEN
read -p "Cloudflare Zone ID (Dashboard → Overview → Zone ID): " CF_ZONE_ID
read -p "Cloudflare Account Email: " CF_EMAIL

echo ""
echo -e "${BLUE}Testing API Connection...${NC}"

# Test API Connection
ZONE_INFO=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json")

ZONE_NAME=$(echo $ZONE_INFO | grep -o '"name":"[^"]*"' | cut -d'"' -f4)

if [ "$ZONE_NAME" == "frawo-tech.de" ]; then
    echo -e "${GREEN}✅ API Connection successful - Zone: ${ZONE_NAME}${NC}"
else
    echo -e "${RED}❌ API Connection failed or wrong Zone${NC}"
    echo "Response: $ZONE_INFO"
    exit 1
fi

echo ""
echo -e "${BLUE}Creating Transform Rule for Security Headers...${NC}"

# Create Transform Rule
RULE_PAYLOAD=$(cat <<'EOF'
{
  "description": "Add Security Headers for frawo-tech.de",
  "action": "execute",
  "expression": "true",
  "action_parameters": {
    "headers": {
      "Strict-Transport-Security": {
        "operation": "set",
        "value": "max-age=31536000; includeSubDomains; preload"
      },
      "X-Frame-Options": {
        "operation": "set",
        "value": "SAMEORIGIN"
      },
      "X-Content-Type-Options": {
        "operation": "set",
        "value": "nosniff"
      },
      "Referrer-Policy": {
        "operation": "set",
        "value": "strict-origin-when-cross-origin"
      },
      "Permissions-Policy": {
        "operation": "set",
        "value": "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()"
      },
      "Content-Security-Policy": {
        "operation": "set",
        "value": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' wss: https:; frame-src 'self' https://challenges.cloudflare.com; frame-ancestors 'self';"
      }
    }
  },
  "enabled": true
}
EOF
)

# Get existing ruleset ID for http_response_headers_transform phase
RULESET_RESPONSE=$(curl -s -X GET \
  "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/rulesets/phases/http_response_headers_transform/entrypoint" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json")

RULESET_ID=$(echo $RULESET_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$RULESET_ID" ]; then
    echo -e "${YELLOW}Creating new ruleset...${NC}"

    # Create new ruleset
    CREATE_RESPONSE=$(curl -s -X POST \
      "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/rulesets" \
      -H "Authorization: Bearer ${CF_API_TOKEN}" \
      -H "Content-Type: application/json" \
      --data "{
        \"name\": \"Security Headers Transform Rules\",
        \"kind\": \"zone\",
        \"phase\": \"http_response_headers_transform\",
        \"rules\": [${RULE_PAYLOAD}]
      }")

    SUCCESS=$(echo $CREATE_RESPONSE | grep -o '"success":true')

    if [ -n "$SUCCESS" ]; then
        echo -e "${GREEN}✅ Security Headers Rule created successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to create rule${NC}"
        echo "Response: $CREATE_RESPONSE"
        exit 1
    fi
else
    echo -e "${YELLOW}Adding rule to existing ruleset: ${RULESET_ID}${NC}"

    # Add rule to existing ruleset
    UPDATE_RESPONSE=$(curl -s -X POST \
      "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/rulesets/${RULESET_ID}/rules" \
      -H "Authorization: Bearer ${CF_API_TOKEN}" \
      -H "Content-Type: application/json" \
      --data "${RULE_PAYLOAD}")

    SUCCESS=$(echo $UPDATE_RESPONSE | grep -o '"success":true')

    if [ -n "$SUCCESS" ]; then
        echo -e "${GREEN}✅ Security Headers Rule added successfully!${NC}"
    else
        echo -e "${RED}❌ Failed to add rule${NC}"
        echo "Response: $UPDATE_RESPONSE"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}Purging Cloudflare Cache...${NC}"

# Purge cache
PURGE_RESPONSE=$(curl -s -X POST \
  "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}')

SUCCESS=$(echo $PURGE_RESPONSE | grep -o '"success":true')

if [ -n "$SUCCESS" ]; then
    echo -e "${GREEN}✅ Cache purged successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Cache purge may have failed (check manually)${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Wait 5-10 minutes for changes to propagate"
echo "2. Test headers: curl -I https://frawo-tech.de"
echo "3. Verify online: https://securityheaders.com/?q=https://frawo-tech.de"
echo "4. Check website functionality (login, navigation, etc.)"
echo ""
echo -e "${BLUE}Monitor for 24-48 hours:${NC}"
echo "- Cloudflare Dashboard → Analytics → Security"
echo "- Browser Console (F12) for CSP errors"
echo ""
echo -e "${RED}Rollback if needed:${NC}"
echo "- Dashboard → Rules → Transform Rules → Disable rule"
echo "- Or delete rule via API"
echo ""
