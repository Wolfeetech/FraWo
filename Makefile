.PHONY: help repo-sync repo-status lint ansible-check docs refresh-context ai-server-handoff estate-census platform-health-audit cicd-delivery-factory-preflight cicd-delivery-factory-report portal-ucg-pilot-preflight inventory-check ansible-ping qga-check close-day start-day repo-sync repo-status stress-test release-mvp-audit release-mvp-gate website-release-audit website-release-gate production-gate document-ownership-check document-ownership-report stockenweiler-inventory-check stockenweiler-inventory-report stockenweiler-support-brief stockenweiler-public-truth-check stockenweiler-remote-path-probe stockenweiler-toolbox-access stockenweiler-wireguard-refresh stockenweiler-wireguard-reapply stockenweiler-tailscale-bridge-prepare stockenweiler-tailscale-bridge-check wireguard-legacy-cleanup control-surface-actions-check control-surface-actions-report ansible-syntax-check ansible-syntax-check-toolbox ansible-syntax-check-toolbox-tailscale ansible-syntax-check-toolbox-mobile-firewall ansible-syntax-check-proxmox-backups ansible-syntax-check-haos ansible-syntax-check-business-hardening ansible-syntax-check-pbs ansible-syntax-check-surface-go ansible-syntax-check-rpi-radio ansible-syntax-check-rpi-radio-media ansible-syntax-check-rpi-radio-usb ansible-syntax-check-rpi-radio-network ansible-syntax-check-rpi-azuracast-host ansible-syntax-check-rpi-azuracast ansible-syntax-check-rpi-azuracast-tuning ansible-syntax-check-paperless-nextcloud-bridge ansible-syntax-check-app-smtp ansible-list-business proxmox-storage-check backup-proof backup-list business-drift-check basics-check backup-prune-dry-run backup-prune toolbox-deploy toolbox-network-check toolbox-portal-status-check toolbox-tun-prep toolbox-tailscale-prep toolbox-tailscale-check toolbox-tailscale-login-url toolbox-tailscale-join-assist toolbox-tailscale-mobile-check toolbox-mobile-firewall-deploy toolbox-media-deploy toolbox-media-storage-integrate toolbox-media-check toolbox-jellyfin-ui-check toolbox-media-sync-deploy toolbox-media-sync-check toolbox-media-bootstrap-progress media-migration-status toolbox-music-library-report toolbox-music-scan-issues toolbox-music-curation-candidates toolbox-music-curated-layout toolbox-music-quarantine-candidates toolbox-music-selection-sync toolbox-music-selection-seed-report toolbox-music-selection-generate-starter toolbox-music-selection-promote-starter rightsize-stage-gate rightsize-plan rightsize-apply haos-preflight haos-usb-audit haos-stage-gate haos-runner-deploy haos-vm-check haos-reverse-proxy-enable haos-reverse-proxy-check gateway-cutover-stage-gate pbs-preflight pbs-stage-gate pbs-proof-check pbs-restore-proof pbs-runner-deploy pbs-vm-check pbs-guest-check pbs-iso-stage pbs-usb-interim-prepare pbs-rebuild-storage-audit pbs-rebuild-contract-check pbs-device-inventory pbs-contract-prefill pbs-datastore-prepare pbs-vm240-reconcile pbs-guarded-rebuild app-smtp-deploy app-smtp-check vaultwarden-smtp-deploy vaultwarden-smtp-check vaultwarden-admin-token-check vaultwarden-network-baseline storage-node-network-baseline public-ipv6-exposure-audit proxmox-local-backup-deploy proxmox-local-backup-check portable-backup-usb-prepare portable-backup-usb-autoprepare portable-backup-usb-fill portable-backup-usb-check portable-backup-usb-run security-baseline-check business-hardening-deploy easybox-browser-probe easybox-authenticated-overview capacity-review plan-progress surface-go-check surface-go-bootstrap surface-go-root-sleep-harden media-fetch media-devices surface-iso-fetch surface-usb-prepare usb-stick-roles-prepare favorites-usb-prepare rpi-sd-flash rpi-firstboot-seed rpi-radio-bootstrap rpi-radio-media-prepare rpi-radio-media-check rpi-radio-usb-integrate rpi-radio-usb-check rpi-radio-network-integrate rpi-radio-network-check rpi-azuracast-host-prepare rpi-azuracast-deploy rpi-radio-check rpi-radio-integration-check rpi-azuracast-check rpi-azuracast-tune rpi-resource-check radio-ops-check anydesk-zenbook-install zenbook-remote-check remote-only-check operator-todos ops-brief adguard-pilot-check tailscale-split-dns-check inventory-resolution-check inventory-unknown-report paperless-nextcloud-bridge-deploy paperless-nextcloud-bridge-check public-dns-check public-http-redirect-check public-https-check public-mail-dns-check prove-strato-mail-model


ROOT_DIR := $(CURDIR)
ANSIBLE_CONFIG_PATH := $(ROOT_DIR)/ansible.cfg
ANSIBLE_INVENTORY_PATH := $(ROOT_DIR)/ansible/inventory/hosts.yml
ANSIBLE_ENV = ANSIBLE_CONFIG="$(ANSIBLE_CONFIG_PATH)"
ANSIBLE_CMD = $(ANSIBLE_ENV) ansible --inventory "$(ANSIBLE_INVENTORY_PATH)"
ANSIBLE_PLAYBOOK_CMD = $(ANSIBLE_ENV) ansible-playbook --inventory "$(ANSIBLE_INVENTORY_PATH)"
ANSIBLE_INVENTORY_CMD = $(ANSIBLE_ENV) ansible-inventory --inventory "$(ANSIBLE_INVENTORY_PATH)"
PROXMOX_REMOTE = bash ./scripts/proxmox_remote_exec.sh

# ─── Solo Operator Entry Points ─────────────────────────────────────────────

# --- REPOSITORY -------------------------------------------------------------

## repo-sync: Synchronize local workspace with canonical GitHub SSOT
repo-sync:
	@bash scripts/repo_sync.sh

## repo-status: Show synchronization status of the workspace
repo-status:
	@git status
	@git remote -v
	@echo ""
	@echo "--- Local commits not reached GitHub ---"
	@git log origin/main..main --oneline
	@echo ""
	@echo "--- Remote commits not in Workspace ---"
	@git log main..origin/main --oneline

# --- HELP --------------------------------------------------------------------

## help: Show this help message
help:
	@echo ""
	@echo "Homeserver 2027 Ops Workspace – Common Make Targets"
	@echo "====================================================="
	@echo ""
	@echo "DAILY OPERATIONS:"
	@echo "  make start-day              Morning routine (context refresh + status)"
	@echo "  make ops-brief              3-line platform summary"
	@echo "  make operator-todos         Show open manual tasks"
	@echo "  make close-day              Evening routine (snapshot + handoff)"
	@echo ""
	@echo "REPOSITORY:"
	@echo "  make repo-sync              Synchronize with GitHub SSOT"
	@echo "  make repo-status            Show sync status"
	@echo ""
	@echo "HEALTH CHECKS:"
	@echo "  make basics-check           Ping all VMs + toolbox"
	@echo "  make security-baseline-check  Verify security posture"
	@echo "  make business-drift-check   Check business services for drift"
	@echo "  make backup-proof           Verify last backup"
	@echo ""
	@echo "LINTING / VALIDATION:"
	@echo "  make lint                   Run all local lint checks"
	@echo "  make ansible-check          Ansible syntax check (all playbooks)"
	@echo "  make docs                   Validate key documentation files exist"
	@echo ""
	@echo "ANSIBLE:"
	@echo "  make ansible-ping           Ping all managed hosts"
	@echo "  make ansible-syntax-check   Syntax check all playbooks"
	@echo "  make toolbox-deploy         Deploy toolbox configuration"
	@echo ""
	@echo "BACKUP / PBS:"
	@echo "  make backup-list            List current backups"
	@echo "  make pbs-restore-proof      Run monthly PBS restore drill"
	@echo ""
	@echo "CONTEXT:"
	@echo "  make refresh-context        Refresh LIVE_CONTEXT.md"
	@echo "  make plan-progress          Show masterplan progress percentage"
	@echo ""
	@echo "Run 'make <target>' for any target above."
	@echo "Full target list: see Makefile or README.md Quick Commands section."
	@echo ""

## lint: Run local lint checks (ansible syntax, yaml, python)
lint: ansible-check
	@echo "[lint] Checking for obvious plaintext secrets in non-vault yml files..."
	@if grep -rn --include="*.yml" --include="*.yaml" \
		-E "(password|passwd|secret|token)\s*[:=]\s*['\"][A-Za-z0-9+/]{8,}" \
		--exclude-dir=.git --exclude="*/vault.yml" \
		. 2>/dev/null | grep -v "vault_password_file\|example\|placeholder"; then \
		echo "[WARN] Potential plaintext secrets found above. Move them to ansible-vault."; \
	fi
	@if [ -f .vault_pass ] && grep -q "your-vault-password-here" .vault_pass 2>/dev/null; then \
		echo "[WARN] .vault_pass still contains the example placeholder"; \
	fi
	@echo "[lint] Done."

## ansible-check: Syntax-check all Ansible playbooks
ansible-check: ansible-syntax-check

## docs: Verify key SSOT documentation files are present
docs:
	@echo "[docs] Checking required SSOT files..."
	@for f in README.md MASTERPLAN.md OPERATOR_TODO_QUEUE.md OPS_HOME.md LIVE_CONTEXT.md SECURITY.md SECURITY_BASELINE.md MEMORY.md NETWORK_INVENTORY.md VM_AUDIT.md; do \
		if [ -f "$$f" ]; then echo "  ✓ $$f"; else echo "  ✗ MISSING: $$f"; fi; \
	done
	@echo "[docs] Done."

## ai-status: Check health of local brains (Ollama) and MCP bridge
ai-status:
	@"C:\Users\StudioPC\AppData\Local\Programs\Ollama\ollama.exe" list
	@python scripts/business/mcp_odoo_pro_server.py --help > /dev/null && echo "[ai] Odoo MCP Bridge: OK" || echo "[ai] Odoo MCP Bridge: ERROR"

## ai-odoo-sync: Fully synchronize Odoo mission lanes and reclaim tasks
ai-odoo-sync:
	python scripts/business/mcp_odoo_pro_server.py ensure_lanes
	python scripts/business/mcp_odoo_pro_server.py reclaim_tasks

ai-preflight:
	@"C:\Users\StudioPC\AppData\Local\Programs\Ollama\ollama.exe" run frawo-pro "Analysiere den aktuellen Status von LIVE_CONTEXT.md und MASTERPLAN.md. Liste die nächsten 3 Prioritäten auf."

## ai-emergency-audit: Autonomous disaster recovery analysis for the Anker site
ai-emergency-audit:
	@"C:\Users\StudioPC\AppData\Local\Programs\Ollama\ollama.exe" run frawo-pro "Die Anker-Site (100.69.179.87) ist seit 2 Stunden offline. Basierend auf dem MASTERPLAN und LIVE_CONTEXT: Was sind die kritischen Risiken und welche 3 Schritte muss der Operator jetzt physisch prüfen? Antworte kurz und präzise."

# --- OPENCLAW AGENT ---------------------------------------------------------

## openclaw-provision: Install and configure the local high-performance runtime
openclaw-provision:
	powershell -ExecutionPolicy Bypass -Command "mkdir C:\WORKSPACE\OPERATIONS\OpenClaw\bin -Force; mkdir C:\WORKSPACE\OPERATIONS\OpenClaw\config -Force; mkdir C:\WORKSPACE\OPERATIONS\OpenClaw\logs -Force"
	cmd /c "copy DOCS\Task_Archive\OPENCLAW_SYSTEM_PROMPT.md C:\WORKSPACE\OPERATIONS\OpenClaw\config\system_prompt.md && copy Codex\openclaw_id_ed25519 C:\WORKSPACE\OPERATIONS\OpenClaw\config\id_ed25519"

## openclaw-shell: Start the specialized OpenClaw agent session
openclaw-shell:
	powershell -ExecutionPolicy Bypass -File C:\WORKSPACE\OPERATIONS\OpenClaw\start_openclaw.ps1

# ─────────────────────────────────────────────────────────────────────────────

refresh-context:
	./scripts/refresh_live_context.sh

ai-server-handoff:
	python ./scripts/generate_ai_server_handoff.py

estate-census:
	python ./scripts/estate_census_audit.py

platform-health-audit:
	python ./scripts/platform_health_audit.py

cicd-delivery-factory-preflight:
	python ./scripts/cicd_delivery_factory_preflight.py

cicd-delivery-factory-report:
	python ./scripts/cicd_delivery_factory_report.py

portal-ucg-pilot-preflight:
	python ./scripts/portal_ucg_pilot_preflight.py

prove-strato-mail-model:
	powershell -ExecutionPolicy Bypass -File .\scripts\prove_strato_mail_model.ps1

inventory-check:
	bash ./scripts/inventory_check.sh

ansible-ping:
	$(ANSIBLE_CMD) proxmox,toolbox,nextcloud_vm,odoo_vm,paperless_vm -m ping

qga-check:
	$(PROXMOX_REMOTE) 'qm agent 200 ping && echo vm200_qga_ok; qm agent 210 ping && echo vm210_qga_ok; qm agent 220 ping && echo vm220_qga_ok; qm agent 230 ping && echo vm230_qga_ok'

close-day:
	./scripts/close_day.sh

start-day:
	./scripts/start_day.sh

stress-test:
	bash ./scripts/run_internal_stress_test.sh

release-mvp-audit:
	bash ./scripts/run_release_mvp_audit.sh

release-mvp-gate:
	python ./scripts/release_mvp_gate.py

website-release-audit:
	python ./scripts/run_website_release_audit.py

website-release-gate:
	python ./scripts/website_release_gate.py

production-gate:
	bash ./scripts/production_readiness_gate.sh

document-ownership-check:
	python3 ./scripts/document_ownership_check.py

document-ownership-report:
	python3 ./scripts/document_ownership_check.py --report artifacts/document_ownership/report.md

stockenweiler-inventory-check:
	python3 ./scripts/stockenweiler_inventory_check.py

stockenweiler-inventory-report:
	python3 ./scripts/stockenweiler_inventory_check.py --report artifacts/stockenweiler_inventory/report.md

stockenweiler-support-brief:
	python3 ./scripts/stockenweiler_support_brief.py

stockenweiler-public-truth-check:
	python3 ./scripts/stockenweiler_public_truth_check.py

stockenweiler-remote-path-probe:
	python3 ./scripts/stockenweiler_remote_path_probe.py

stockenweiler-toolbox-access:
	powershell -ExecutionPolicy Bypass -File .\scripts\ensure_stockenweiler_toolbox_access.ps1

stockenweiler-wireguard-refresh:
	powershell -ExecutionPolicy Bypass -File .\scripts\refresh_stockenweiler_wireguard_profile.ps1

stockenweiler-wireguard-reapply:
	powershell -ExecutionPolicy Bypass -File .\scripts\reapply_stockenweiler_wireguard_service.ps1

stockenweiler-tailscale-bridge-prepare:
	python3 ./scripts/prepare_stockenweiler_tailscale_bridge.py

stockenweiler-tailscale-bridge-check:
	python3 ./scripts/check_stockenweiler_tailscale_bridge.py

wireguard-legacy-cleanup:
	powershell -ExecutionPolicy Bypass -File .\scripts\clean_local_wireguard_legacy.ps1

control-surface-actions-check:
	python3 ./scripts/control_surface_actions_check.py

control-surface-actions-report:
	python3 ./scripts/control_surface_actions_check.py --report artifacts/control_surface/actions_report.md

public-dns-check:
	python3 ./scripts/public_dns_check.py

public-http-redirect-check:
	python3 ./scripts/public_http_redirect_check.py

public-https-check:
	python3 ./scripts/public_https_check.py

public-mail-dns-check:
	python3 ./scripts/public_mail_dns_check.py

ansible-syntax-check:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/deploy_business_stacks.yml

ansible-syntax-check-toolbox:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/deploy_toolbox_foundation.yml

ansible-syntax-check-toolbox-tailscale:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/prepare_toolbox_tailscale.yml

ansible-syntax-check-toolbox-mobile-firewall:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/deploy_toolbox_mobile_firewall.yml

ansible-syntax-check-proxmox-backups:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/deploy_proxmox_local_backup_ops.yml

ansible-syntax-check-haos:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/deploy_haos_vm_runner.yml

ansible-syntax-check-business-hardening:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/harden_business_network_baseline.yml

ansible-syntax-check-app-smtp:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/deploy_app_smtp_baseline.yml

ansible-syntax-check-pbs:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/deploy_pbs_vm_runner.yml

ansible-syntax-check-surface-go:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/bootstrap_surface_go_frontend.yml

ansible-syntax-check-rpi-radio:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/bootstrap_raspberry_pi_radio.yml

ansible-syntax-check-rpi-radio-media:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/prepare_raspberry_pi_radio_media_layout.yml

ansible-syntax-check-rpi-radio-usb:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/integrate_raspberry_pi_radio_usb_music.yml

ansible-syntax-check-rpi-radio-network:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/integrate_raspberry_pi_radio_network_music.yml

ansible-syntax-check-rpi-azuracast-host:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/prepare_raspberry_pi_azuracast_host.yml

ansible-syntax-check-rpi-azuracast:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/deploy_raspberry_pi_azuracast.yml

ansible-syntax-check-rpi-azuracast-tuning:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/tune_raspberry_pi_azuracast_resources.yml

ansible-syntax-check-paperless-nextcloud-bridge:
	$(ANSIBLE_PLAYBOOK_CMD) --syntax-check ansible/playbooks/deploy_paperless_nextcloud_bridge.yml

ansible-list-business:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_business_stacks.yml --list-hosts

toolbox-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_toolbox_foundation.yml

toolbox-tun-prep:
	./scripts/proxmox_enable_toolbox_tun.sh

toolbox-tailscale-prep:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/prepare_toolbox_tailscale.yml

proxmox-storage-check:
	$(PROXMOX_REMOTE) 'pvesm status; echo; vgs -o vg_name,vg_size,vg_free,pv_count,lv_count; echo; lvs -a -o vg_name,lv_name,lv_attr,lv_size,pool_lv,data_percent,metadata_percent,origin'

backup-list:
	$(PROXMOX_REMOTE) 'ls -lah /var/lib/vz/dump/vzdump-qemu-*.vma.zst 2>/dev/null || echo "no qemu backups present in /var/lib/vz/dump"; echo'

backup-proof:
	./scripts/proxmox_business_backup_proof.sh

business-drift-check:
	./scripts/business_service_drift_check.sh

basics-check:
	./scripts/platform_basics_check.sh

security-baseline-check:
	./scripts/security_baseline_check.sh

business-hardening-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/harden_business_network_baseline.yml

paperless-nextcloud-bridge-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_paperless_nextcloud_bridge.yml

paperless-nextcloud-bridge-check:
	./scripts/paperless_nextcloud_bridge_check.sh

toolbox-network-check:
	./scripts/toolbox_network_check.sh

toolbox-portal-status-check:
	./scripts/toolbox_portal_status_check.sh

toolbox-tailscale-check:
	./scripts/toolbox_tailscale_check.sh

toolbox-tailscale-login-url:
	./scripts/toolbox_tailscale_login_url.sh

toolbox-tailscale-join-assist:
	./scripts/toolbox_tailscale_join_assist.sh

toolbox-tailscale-mobile-check:
	./scripts/toolbox_tailscale_mobile_check.sh

toolbox-mobile-firewall-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_toolbox_mobile_firewall.yml

toolbox-media-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_toolbox_media_server.yml

toolbox-media-storage-integrate:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/integrate_toolbox_media_storage.yml

toolbox-media-check:
	./scripts/toolbox_media_server_check.sh

toolbox-jellyfin-ui-check:
	./scripts/toolbox_jellyfin_ui_check.sh

toolbox-media-sync-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_toolbox_media_sync.yml

toolbox-media-sync-check:
	./scripts/toolbox_media_sync_check.sh

toolbox-media-bootstrap-progress:
	./scripts/toolbox_media_bootstrap_progress.sh

media-migration-status:
	./scripts/media_migration_status.sh

toolbox-music-library-report:
	./scripts/toolbox_music_library_report.sh

toolbox-music-scan-issues:
	./scripts/toolbox_music_scan_issue_report.sh

toolbox-music-curation-candidates:
	./scripts/toolbox_music_curation_candidates.sh

toolbox-music-curated-layout:
	./scripts/toolbox_music_curated_layout_check.sh

toolbox-music-quarantine-candidates:
	./scripts/toolbox_quarantine_music_candidates.sh

toolbox-music-selection-sync:
	./scripts/toolbox_music_selection_sync.sh

toolbox-music-selection-seed-report:
	./scripts/toolbox_music_selection_seed_report.sh

toolbox-music-selection-generate-starter:
	./scripts/toolbox_music_selection_generate_starter.sh

toolbox-music-selection-promote-starter:
	./scripts/toolbox_music_selection_promote_starter.sh

rightsize-stage-gate:
	./scripts/rightsize_stage_gate_check.sh

rightsize-plan:
	./scripts/proxmox_rightsize_business_vms.sh

rightsize-apply:
	APPLY=1 ./scripts/proxmox_rightsize_business_vms.sh

easybox-browser-probe:
	./scripts/easybox_browser_probe.sh

easybox-authenticated-overview:
	./scripts/easybox_authenticated_overview_dump.sh

capacity-review:
	./scripts/capacity_review_check.sh

plan-progress:
	./scripts/plan_progress_check.sh

surface-go-check:
	./scripts/surface_go_frontend_check.sh

surface-go-bootstrap:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/bootstrap_surface_go_frontend.yml

surface-go-root-sleep-harden:
	./scripts/surface_go_root_sleep_hardening.sh

media-fetch:
	./scripts/fetch_install_media.sh

media-devices:
	./scripts/check_install_media_devices.sh

surface-iso-fetch:
	./scripts/fetch_surface_iso.sh

surface-usb-prepare:
	./scripts/prepare_surface_usb_ventoy.sh

usb-stick-roles-prepare:
	./scripts/prepare_usb_stick_roles.sh

favorites-usb-prepare:
	./scripts/prepare_kingston_favorites_usb.sh

rpi-sd-flash:
	./scripts/flash_rpi_sd_card.sh

rpi-firstboot-seed:
	./scripts/prepare_rpi_firstboot_seed.sh

rpi-radio-bootstrap:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/bootstrap_raspberry_pi_radio.yml

rpi-radio-media-prepare:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/prepare_raspberry_pi_radio_media_layout.yml

rpi-radio-media-check:
	./scripts/rpi_radio_media_layout_check.sh

rpi-radio-usb-integrate:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/integrate_raspberry_pi_radio_usb_music.yml

rpi-radio-network-integrate:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/integrate_raspberry_pi_radio_network_music.yml

rpi-radio-usb-check:
	./scripts/rpi_radio_usb_music_check.sh

rpi-radio-network-check:
	./scripts/rpi_radio_network_music_check.sh

rpi-azuracast-host-prepare:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/prepare_raspberry_pi_azuracast_host.yml

rpi-azuracast-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_raspberry_pi_azuracast.yml

rpi-azuracast-tune:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/tune_raspberry_pi_azuracast_resources.yml

rpi-radio-check:
	./scripts/rpi_radio_readiness_check.sh

rpi-radio-integration-check:
	./scripts/rpi_radio_integration_check.sh

rpi-azuracast-check:
	./scripts/rpi_azuracast_service_check.sh

rpi-resource-check:
	./scripts/rpi_resource_budget_check.sh

radio-ops-check:
	./scripts/radio_operations_check.sh

anydesk-zenbook-install:
	./scripts/install_anydesk_zenbook.sh

zenbook-remote-check:
	./scripts/zenbook_remote_access_check.sh

remote-only-check:
	./scripts/remote_only_stage_gate_check.sh

operator-todos:
	./scripts/operator_todo_queue.sh

ops-brief:
	./scripts/ops_brief.sh

adguard-pilot-check:
	./scripts/adguard_pilot_readiness_check.sh

tailscale-split-dns-check:
	./scripts/tailscale_split_dns_readiness_check.sh

inventory-resolution-check:
	./scripts/inventory_resolution_check.sh

inventory-unknown-report:
	./scripts/inventory_unknown_review_report.sh

haos-preflight:
	./scripts/haos_preflight_check.sh

haos-usb-audit:
	./scripts/haos_usb_audit_report.sh

haos-stage-gate:
	./scripts/haos_stage_gate_check.sh

haos-runner-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_haos_vm_runner.yml

haos-vm-check:
	./scripts/proxmox_haos_vm_check.sh

haos-reverse-proxy-enable:
	./scripts/haos_enable_reverse_proxy.sh

haos-reverse-proxy-check:
	./scripts/haos_reverse_proxy_check.sh

gateway-cutover-stage-gate:
	./scripts/gateway_cutover_stage_gate_check.sh

pbs-preflight:
	./scripts/pbs_preflight_check.sh

pbs-stage-gate:
	./scripts/pbs_stage_gate_check.sh

pbs-proof-check:
	./scripts/pbs_proof_backup_check.sh

pbs-restore-proof:
	./scripts/proxmox_pbs_restore_proof.sh

pbs-runner-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_pbs_vm_runner.yml

pbs-vm-check:
	./scripts/proxmox_pbs_vm_check.sh

pbs-guest-check:
	./scripts/pbs_guest_postinstall_check.sh

pbs-iso-stage:
	./scripts/proxmox_stage_pbs_iso.sh

pbs-usb-interim-prepare:
	./scripts/proxmox_prepare_interim_pbs_usb_datastore.sh $(DEV)

pbs-rebuild-storage-audit:
	./scripts/pbs_rebuild_storage_audit.sh

pbs-rebuild-contract-check:
	./scripts/pbs_rebuild_contract_check.sh

pbs-device-inventory:
	./scripts/pbs_device_inventory.sh

pbs-contract-prefill:
	python3 ./scripts/pbs_contract_prefill.py --boot-serial "$(BOOT_SERIAL)" --datastore-serial "$(DATASTORE_SERIAL)" --approved-by "$(APPROVED_BY)" --change-ticket "$(CHANGE_TICKET)" --write

pbs-datastore-prepare:
	./scripts/proxmox_prepare_pbs_datastore_device.sh $(DEV)

pbs-vm240-reconcile:
	./scripts/pbs_vm240_reconcile.sh

pbs-guarded-rebuild:
	./scripts/pbs_guarded_rebuild.sh

app-smtp-deploy:
	bash ./scripts/app_smtp_deploy.sh

app-smtp-check:
	bash ./scripts/app_smtp_check.sh

vaultwarden-smtp-deploy:
	bash ./scripts/vaultwarden_smtp_deploy.sh

vaultwarden-smtp-check:
	bash ./scripts/vaultwarden_smtp_check.sh

vaultwarden-admin-token-check:
	bash ./scripts/vaultwarden_admin_token_check.sh

vaultwarden-network-baseline:
	python ./scripts/apply_vaultwarden_network_baseline.py

storage-node-network-baseline:
	python ./scripts/apply_storage_node_network_baseline.py

public-ipv6-exposure-audit:
	python ./scripts/public_ipv6_exposure_audit.py

proxmox-local-backup-deploy:
	$(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_proxmox_local_backup_ops.yml

proxmox-local-backup-check:
	./scripts/proxmox_local_backup_ops_check.sh

portable-backup-usb-prepare:
	./scripts/proxmox_portable_backup_usb_prepare.sh $(DEV)

portable-backup-usb-autoprepare:
	./scripts/proxmox_portable_backup_usb_autoprepare.sh $(DEV)

portable-backup-usb-fill:
	./scripts/proxmox_portable_backup_usb_fill.sh

portable-backup-usb-check:
	./scripts/proxmox_portable_backup_usb_check.sh

portable-backup-usb-run:
	./scripts/proxmox_portable_backup_usb_run.sh $(DEV)

backup-prune-dry-run:
	./scripts/proxmox_prune_local_backups.sh

backup-prune:
	APPLY=1 ./scripts/proxmox_prune_local_backups.sh
