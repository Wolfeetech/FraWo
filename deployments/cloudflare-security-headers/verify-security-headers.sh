#!/bin/bash
# Security Headers Verification Script für frawo-tech.de
# Prüft alle implementierten Security Headers und gibt einen Report aus

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Domain als Parameter (Standard: frawo-tech.de)
DOMAIN="${1:-frawo-tech.de}"
URL="https://${DOMAIN}"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Security Headers Test für ${DOMAIN}${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Funktion zum Prüfen eines Headers
check_header() {
    local header_name="$1"
    local expected_value="$2"
    local priority="$3"

    # Header abrufen
    actual_value=$(curl -s -I "${URL}" | grep -i "^${header_name}:" | cut -d: -f2- | sed 's/^[[:space:]]*//' | tr -d '\r\n')

    if [ -n "${actual_value}" ]; then
        echo -e "${GREEN}✅ ${header_name}${NC}"
        echo -e "   Wert: ${actual_value}"

        # Wenn ein erwarteter Wert angegeben ist, prüfen
        if [ -n "${expected_value}" ]; then
            if echo "${actual_value}" | grep -q "${expected_value}"; then
                echo -e "   ${GREEN}Entspricht Empfehlung${NC}"
            else
                echo -e "   ${YELLOW}⚠️  Weicht von Empfehlung ab${NC}"
                echo -e "   Empfohlen: ${expected_value}"
            fi
        fi
    else
        if [ "${priority}" == "HIGH" ]; then
            echo -e "${RED}❌ ${header_name} - FEHLT (PRIORITÄT: HOCH)${NC}"
        elif [ "${priority}" == "MEDIUM" ]; then
            echo -e "${YELLOW}⚠️  ${header_name} - FEHLT (PRIORITÄT: MITTEL)${NC}"
        else
            echo -e "${YELLOW}ℹ️  ${header_name} - FEHLT (PRIORITÄT: NIEDRIG)${NC}"
        fi
    fi
    echo ""
}

echo -e "${YELLOW}Testing ${URL}...${NC}"
echo ""

# Prüfe jeden Security Header
echo -e "${BLUE}=== KRITISCHE SECURITY HEADERS ===${NC}"
echo ""

check_header "Strict-Transport-Security" "max-age=31536000" "HIGH"
check_header "X-Frame-Options" "SAMEORIGIN" "HIGH"
check_header "Content-Security-Policy" "default-src" "HIGH"

echo -e "${BLUE}=== WICHTIGE SECURITY HEADERS ===${NC}"
echo ""

check_header "X-Content-Type-Options" "nosniff" "MEDIUM"
check_header "Referrer-Policy" "strict-origin-when-cross-origin" "MEDIUM"
check_header "Permissions-Policy" "" "MEDIUM"

echo -e "${BLUE}=== ZUSÄTZLICHE HEADERS ===${NC}"
echo ""

check_header "X-XSS-Protection" "" "LOW"
check_header "Server" "" "LOW"

# Cookie-Sicherheit prüfen
echo -e "${BLUE}=== COOKIE SECURITY ===${NC}"
echo ""

cookies=$(curl -s -I "${URL}" | grep -i "^set-cookie:")

if [ -n "${cookies}" ]; then
    echo -e "${GREEN}✅ Cookies gefunden${NC}"
    echo "${cookies}" | while IFS= read -r cookie; do
        echo ""
        echo "Cookie: $(echo ${cookie} | cut -d: -f2- | cut -d';' -f1)"

        # Prüfe Secure Flag
        if echo "${cookie}" | grep -q "Secure"; then
            echo -e "  ${GREEN}✅ Secure Flag vorhanden${NC}"
        else
            echo -e "  ${RED}❌ Secure Flag FEHLT${NC}"
        fi

        # Prüfe HttpOnly Flag
        if echo "${cookie}" | grep -q "HttpOnly"; then
            echo -e "  ${GREEN}✅ HttpOnly Flag vorhanden${NC}"
        else
            echo -e "  ${YELLOW}⚠️  HttpOnly Flag fehlt${NC}"
        fi

        # Prüfe SameSite Flag
        if echo "${cookie}" | grep -q "SameSite"; then
            samesite=$(echo "${cookie}" | grep -o "SameSite=[^;]*")
            echo -e "  ${GREEN}✅ ${samesite}${NC}"
        else
            echo -e "  ${RED}❌ SameSite Attribut FEHLT${NC}"
        fi
    done
else
    echo -e "${YELLOW}ℹ️  Keine Cookies im Response (normal für Startseite)${NC}"
fi

echo ""

# SSL/TLS Test
echo -e "${BLUE}=== SSL/TLS CONFIGURATION ===${NC}"
echo ""

ssl_info=$(echo | openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" 2>/dev/null)

# TLS Version
tls_version=$(echo "${ssl_info}" | grep "Protocol" | awk '{print $3}')
if [ -n "${tls_version}" ]; then
    if [ "${tls_version}" == "TLSv1.3" ]; then
        echo -e "${GREEN}✅ TLS Version: ${tls_version}${NC}"
    elif [ "${tls_version}" == "TLSv1.2" ]; then
        echo -e "${YELLOW}⚠️  TLS Version: ${tls_version} (TLSv1.3 empfohlen)${NC}"
    else
        echo -e "${RED}❌ TLS Version: ${tls_version} (VERALTET!)${NC}"
    fi
fi

# Cipher
cipher=$(echo "${ssl_info}" | grep "Cipher" | awk '{print $3}')
if [ -n "${cipher}" ]; then
    echo -e "${GREEN}✅ Cipher: ${cipher}${NC}"
fi

# Zertifikat Gültigkeit
cert_dates=$(echo "${ssl_info}" | openssl x509 -noout -dates 2>/dev/null)
if [ -n "${cert_dates}" ]; then
    echo -e "${GREEN}✅ Zertifikat:${NC}"
    echo "${cert_dates}" | sed 's/^/   /'
fi

echo ""

# DNS Check
echo -e "${BLUE}=== DNS CONFIGURATION ===${NC}"
echo ""

ipv4=$(nslookup "${DOMAIN}" 2>/dev/null | grep "Address:" | tail -1 | awk '{print $2}')
if [ -n "${ipv4}" ]; then
    echo -e "${GREEN}✅ IPv4: ${ipv4}${NC}"
fi

ipv6=$(nslookup "${DOMAIN}" 2>/dev/null | grep "Address:" | grep ":" | head -1 | awk '{print $2}')
if [ -n "${ipv6}" ]; then
    echo -e "${GREEN}✅ IPv6: ${ipv6}${NC}"
fi

# Cloudflare Detection
cf_ray=$(curl -s -I "${URL}" | grep -i "cf-ray:" | cut -d: -f2-)
if [ -n "${cf_ray}" ]; then
    echo -e "${GREEN}✅ Cloudflare aktiv (CF-RAY:${cf_ray})${NC}"
fi

echo ""

# Gesamtbewertung
echo -e "${BLUE}=== GESAMTBEWERTUNG ===${NC}"
echo ""

# Zähle vorhandene kritische Header
critical_count=0
critical_total=3

# HSTS
if curl -s -I "${URL}" | grep -qi "Strict-Transport-Security"; then
    ((critical_count++))
fi

# X-Frame-Options
if curl -s -I "${URL}" | grep -qi "X-Frame-Options"; then
    ((critical_count++))
fi

# CSP
if curl -s -I "${URL}" | grep -qi "Content-Security-Policy"; then
    ((critical_count++))
fi

echo -e "Kritische Security Headers: ${critical_count}/${critical_total}"

if [ ${critical_count} -eq ${critical_total} ]; then
    echo -e "${GREEN}✅ AUSGEZEICHNET - Alle kritischen Header vorhanden${NC}"
    grade="A"
elif [ ${critical_count} -eq 2 ]; then
    echo -e "${YELLOW}⚠️  GUT - 1 kritischer Header fehlt${NC}"
    grade="B"
elif [ ${critical_count} -eq 1 ]; then
    echo -e "${YELLOW}⚠️  BEFRIEDIGEND - 2 kritische Header fehlen${NC}"
    grade="C"
else
    echo -e "${RED}❌ MANGELHAFT - Alle kritischen Header fehlen${NC}"
    grade="D"
fi

echo ""
echo -e "${BLUE}Security Grade: ${grade}${NC}"
echo ""

# Online Tests empfehlen
echo -e "${BLUE}=== EMPFOHLENE ONLINE-TESTS ===${NC}"
echo ""
echo "1. Security Headers: https://securityheaders.com/?q=${URL}"
echo "2. Mozilla Observatory: https://observatory.mozilla.org/analyze/${DOMAIN}"
echo "3. SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=${DOMAIN}"
echo ""

# Zusammenfassung ausgeben
echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Test abgeschlossen für ${DOMAIN}${NC}"
echo -e "${BLUE}======================================${NC}"

# Exit Code basierend auf Grade
case ${grade} in
    A) exit 0 ;;
    B) exit 0 ;;
    C) exit 1 ;;
    D) exit 1 ;;
    *) exit 2 ;;
esac
