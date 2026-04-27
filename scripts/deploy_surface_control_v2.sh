#!/bin/bash
# Deploy Surface Control V2 to Surface Go Frontend
# Usage: ./scripts/deploy_surface_control_v2.sh [--check|--deploy]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLAYBOOK="${ROOT_DIR}/ansible/playbooks/deploy_surface_control_v2.yml"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Surface Control V2 - Deployment Script${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if ansible-playbook is available
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${RED}❌ Error: ansible-playbook not found${NC}"
    echo -e "${YELLOW}Please install Ansible:${NC}"
    echo "  Ubuntu/Debian: sudo apt install ansible"
    echo "  macOS: brew install ansible"
    exit 1
fi

# Check if playbook exists
if [ ! -f "${PLAYBOOK}" ]; then
    echo -e "${RED}❌ Error: Playbook not found at ${PLAYBOOK}${NC}"
    exit 1
fi

# Parse arguments
MODE="deploy"
if [ "$1" = "--check" ]; then
    MODE="check"
elif [ "$1" = "--syntax" ]; then
    MODE="syntax"
fi

echo -e "${GREEN}📋 Configuration:${NC}"
echo "  Playbook: ${PLAYBOOK}"
echo "  Mode: ${MODE}"
echo ""

case "${MODE}" in
    syntax)
        echo -e "${BLUE}🔍 Running syntax check...${NC}"
        ansible-playbook "${PLAYBOOK}" --syntax-check
        echo -e "${GREEN}✅ Syntax check passed!${NC}"
        ;;

    check)
        echo -e "${BLUE}🔍 Running dry-run (check mode)...${NC}"
        ansible-playbook "${PLAYBOOK}" --check --diff
        echo ""
        echo -e "${YELLOW}ℹ️  This was a dry-run. No changes were made.${NC}"
        echo -e "${YELLOW}   Run without --check to deploy for real.${NC}"
        ;;

    deploy)
        echo -e "${YELLOW}⚠️  About to deploy Surface Control V2 to Surface Go Frontend${NC}"
        echo -e "${YELLOW}   This will:${NC}"
        echo "     - Deploy new HTML file"
        echo "     - Configure systemd services"
        echo "     - Restart Firefox Kiosk"
        echo "     - Enable auto-update timer"
        echo ""
        read -p "Continue? (yes/no): " -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
            echo -e "${YELLOW}❌ Deployment cancelled.${NC}"
            exit 0
        fi

        echo -e "${BLUE}🚀 Deploying Surface Control V2...${NC}"
        echo ""
        ansible-playbook "${PLAYBOOK}"

        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${GREEN}  ✅ Deployment Successful!${NC}"
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${BLUE}📦 What was deployed:${NC}"
            echo "  ✅ Surface Control V2 HTML (Multi-Node Architecture)"
            echo "  ✅ HTTP Server systemd service"
            echo "  ✅ Firefox Kiosk systemd service"
            echo "  ✅ Auto-update timer (6h intervals)"
            echo ""
            echo -e "${BLUE}🎯 Features:${NC}"
            echo "  • Site Auto-Detection (Anker/Stock/Mobile)"
            echo "  • Intelligent Radio Failover"
            echo "  • Now-Playing Widget with source indicator"
            echo "  • Production Odoo Integration"
            echo "  • Service Health Monitoring"
            echo ""
            echo -e "${BLUE}🔍 Verify deployment:${NC}"
            echo "  ssh frontend@surface-go"
            echo "  systemctl --user status firefox-kiosk"
            echo "  systemctl --user status surface-http-server"
            echo "  journalctl --user -u firefox-kiosk -f"
            echo ""
            echo -e "${BLUE}🌐 Access:${NC}"
            echo "  URL: http://127.0.0.1:17827"
            echo "  Opens automatically in Firefox Kiosk"
            echo ""
        else
            echo ""
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${RED}  ❌ Deployment Failed!${NC}"
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo ""
            echo -e "${YELLOW}Check the error messages above for details.${NC}"
            exit 1
        fi
        ;;
esac

echo ""
echo -e "${GREEN}Done!${NC}"
