.PHONY: refresh-context inventory-check ansible-ping qga-check close-day start-day ansible-syntax-check ansible-syntax-check-toolbox ansible-syntax-check-toolbox-tailscale ansible-syntax-check-toolbox-mobile-firewall ansible-syntax-check-proxmox-backups ansible-syntax-check-haos ansible-syntax-check-business-hardening ansible-syntax-check-pbs ansible-syntax-check-surface-go ansible-syntax-check-rpi-radio ansible-syntax-check-rpi-radio-media ansible-syntax-check-rpi-radio-usb ansible-syntax-check-rpi-azuracast-host ansible-syntax-check-rpi-azuracast ansible-syntax-check-rpi-azuracast-tuning ansible-list-business proxmox-storage-check backup-proof backup-list business-drift-check basics-check backup-prune-dry-run backup-prune toolbox-deploy toolbox-network-check toolbox-portal-status-check toolbox-tun-prep toolbox-tailscale-prep toolbox-tailscale-check toolbox-tailscale-login-url toolbox-tailscale-join-assist toolbox-tailscale-mobile-check toolbox-mobile-firewall-deploy toolbox-media-deploy toolbox-media-check toolbox-jellyfin-ui-check toolbox-media-sync-deploy toolbox-media-sync-check toolbox-media-bootstrap-progress toolbox-music-library-report toolbox-music-scan-issues toolbox-music-curation-candidates toolbox-music-curated-layout toolbox-music-quarantine-candidates toolbox-music-selection-sync toolbox-music-selection-seed-report toolbox-music-selection-generate-starter toolbox-music-selection-promote-starter rightsize-stage-gate rightsize-plan rightsize-apply haos-preflight haos-usb-audit haos-stage-gate haos-runner-deploy haos-vm-check haos-reverse-proxy-enable haos-reverse-proxy-check gateway-cutover-stage-gate pbs-preflight pbs-stage-gate pbs-proof-check pbs-restore-proof pbs-runner-deploy pbs-vm-check pbs-guest-check pbs-iso-stage pbs-usb-interim-prepare proxmox-local-backup-deploy proxmox-local-backup-check portable-backup-usb-prepare portable-backup-usb-autoprepare portable-backup-usb-fill portable-backup-usb-check portable-backup-usb-run security-baseline-check business-hardening-deploy easybox-browser-probe easybox-authenticated-overview capacity-review plan-progress surface-go-check surface-go-bootstrap surface-go-root-sleep-harden media-fetch media-devices surface-iso-fetch surface-usb-prepare usb-stick-roles-prepare favorites-usb-prepare rpi-sd-flash rpi-firstboot-seed rpi-radio-bootstrap rpi-radio-media-prepare rpi-radio-media-check rpi-radio-usb-integrate rpi-radio-usb-check rpi-azuracast-host-prepare rpi-azuracast-deploy rpi-radio-check rpi-radio-integration-check rpi-azuracast-check rpi-azuracast-tune rpi-resource-check radio-ops-check anydesk-zenbook-install zenbook-remote-check remote-only-check operator-todos ops-brief adguard-pilot-check tailscale-split-dns-check inventory-resolution-check inventory-unknown-report

refresh-context:
	./scripts/refresh_live_context.sh

inventory-check:
	ansible-inventory --inventory ansible/inventory/hosts.yml --list >/tmp/homeserver2027_inventory.json
	@echo "inventory ok: /tmp/homeserver2027_inventory.json"

ansible-ping:
	ansible proxmox,toolbox,nextcloud_vm,odoo_vm,paperless_vm -m ping

qga-check:
	ssh proxmox 'qm agent 200 ping && echo vm200_qga_ok; qm agent 210 ping && echo vm210_qga_ok; qm agent 220 ping && echo vm220_qga_ok; qm agent 230 ping && echo vm230_qga_ok'

close-day:
	./scripts/close_day.sh

start-day:
	./scripts/start_day.sh

ansible-syntax-check:
	ansible-playbook --syntax-check ansible/playbooks/deploy_business_stacks.yml

ansible-syntax-check-toolbox:
	ansible-playbook --syntax-check ansible/playbooks/deploy_toolbox_foundation.yml

ansible-syntax-check-toolbox-tailscale:
	ansible-playbook --syntax-check ansible/playbooks/prepare_toolbox_tailscale.yml

ansible-syntax-check-toolbox-mobile-firewall:
	ansible-playbook --syntax-check ansible/playbooks/deploy_toolbox_mobile_firewall.yml

ansible-syntax-check-proxmox-backups:
	ansible-playbook --syntax-check ansible/playbooks/deploy_proxmox_local_backup_ops.yml

ansible-syntax-check-haos:
	ansible-playbook --syntax-check ansible/playbooks/deploy_haos_vm_runner.yml

ansible-syntax-check-business-hardening:
	ansible-playbook --syntax-check ansible/playbooks/harden_business_network_baseline.yml

ansible-syntax-check-pbs:
	ansible-playbook --syntax-check ansible/playbooks/deploy_pbs_vm_runner.yml

ansible-syntax-check-surface-go:
	ansible-playbook --syntax-check ansible/playbooks/bootstrap_surface_go_frontend.yml

ansible-syntax-check-rpi-radio:
	ansible-playbook --syntax-check ansible/playbooks/bootstrap_raspberry_pi_radio.yml

ansible-syntax-check-rpi-radio-media:
	ansible-playbook --syntax-check ansible/playbooks/prepare_raspberry_pi_radio_media_layout.yml

ansible-syntax-check-rpi-radio-usb:
	ansible-playbook --syntax-check ansible/playbooks/integrate_raspberry_pi_radio_usb_music.yml

ansible-syntax-check-rpi-azuracast-host:
	ansible-playbook --syntax-check ansible/playbooks/prepare_raspberry_pi_azuracast_host.yml

ansible-syntax-check-rpi-azuracast:
	ansible-playbook --syntax-check ansible/playbooks/deploy_raspberry_pi_azuracast.yml

ansible-syntax-check-rpi-azuracast-tuning:
	ansible-playbook --syntax-check ansible/playbooks/tune_raspberry_pi_azuracast_resources.yml

ansible-list-business:
	ansible-playbook ansible/playbooks/deploy_business_stacks.yml --list-hosts

toolbox-deploy:
	ansible-playbook ansible/playbooks/deploy_toolbox_foundation.yml

toolbox-tun-prep:
	./scripts/proxmox_enable_toolbox_tun.sh

toolbox-tailscale-prep:
	ansible-playbook ansible/playbooks/prepare_toolbox_tailscale.yml

proxmox-storage-check:
	ssh proxmox 'pvesm status; echo; vgs -o vg_name,vg_size,vg_free,pv_count,lv_count; echo; lvs -a -o vg_name,lv_name,lv_attr,lv_size,pool_lv,data_percent,metadata_percent,origin'

backup-list:
	ssh proxmox 'ls -lah /var/lib/vz/dump/vzdump-qemu-*.vma.zst 2>/dev/null || echo "no qemu backups present in /var/lib/vz/dump"'

backup-proof:
	./scripts/proxmox_business_backup_proof.sh

business-drift-check:
	./scripts/business_service_drift_check.sh

basics-check:
	./scripts/platform_basics_check.sh

security-baseline-check:
	./scripts/security_baseline_check.sh

business-hardening-deploy:
	ansible-playbook ansible/playbooks/harden_business_network_baseline.yml

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
	ansible-playbook ansible/playbooks/deploy_toolbox_mobile_firewall.yml

toolbox-media-deploy:
	ansible-playbook ansible/playbooks/deploy_toolbox_media_server.yml

toolbox-media-check:
	./scripts/toolbox_media_server_check.sh

toolbox-jellyfin-ui-check:
	./scripts/toolbox_jellyfin_ui_check.sh

toolbox-media-sync-deploy:
	ansible-playbook ansible/playbooks/deploy_toolbox_media_sync.yml

toolbox-media-sync-check:
	./scripts/toolbox_media_sync_check.sh

toolbox-media-bootstrap-progress:
	./scripts/toolbox_media_bootstrap_progress.sh

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
	ansible-playbook ansible/playbooks/bootstrap_surface_go_frontend.yml

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
	ansible-playbook ansible/playbooks/bootstrap_raspberry_pi_radio.yml

rpi-radio-media-prepare:
	ansible-playbook ansible/playbooks/prepare_raspberry_pi_radio_media_layout.yml

rpi-radio-media-check:
	./scripts/rpi_radio_media_layout_check.sh

rpi-radio-usb-integrate:
	ansible-playbook ansible/playbooks/integrate_raspberry_pi_radio_usb_music.yml

rpi-radio-usb-check:
	./scripts/rpi_radio_usb_music_check.sh

rpi-azuracast-host-prepare:
	ansible-playbook ansible/playbooks/prepare_raspberry_pi_azuracast_host.yml

rpi-azuracast-deploy:
	ansible-playbook ansible/playbooks/deploy_raspberry_pi_azuracast.yml

rpi-azuracast-tune:
	ansible-playbook ansible/playbooks/tune_raspberry_pi_azuracast_resources.yml

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
	ansible-playbook ansible/playbooks/deploy_haos_vm_runner.yml

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
	ansible-playbook ansible/playbooks/deploy_pbs_vm_runner.yml

pbs-vm-check:
	./scripts/proxmox_pbs_vm_check.sh

pbs-guest-check:
	./scripts/pbs_guest_postinstall_check.sh

pbs-iso-stage:
	./scripts/proxmox_stage_pbs_iso.sh

pbs-usb-interim-prepare:
	./scripts/proxmox_prepare_interim_pbs_usb_datastore.sh

proxmox-local-backup-deploy:
	ansible-playbook ansible/playbooks/deploy_proxmox_local_backup_ops.yml

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
