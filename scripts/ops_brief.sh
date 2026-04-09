#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

brief_value() {
  local label="$1"
  local value="$2"
  printf '%s=%s\n' "$label" "$value"
}

toolbox_media_ready="$("${ROOT_DIR}/scripts/toolbox_media_server_check.sh" 2>/dev/null | awk -F= '/^toolbox_media_server_ready=/{print $2}')"
toolbox_jellyfin_ui_ready="$("${ROOT_DIR}/scripts/toolbox_jellyfin_ui_check.sh" 2>/dev/null | awk -F= '/^toolbox_jellyfin_ui_ready=/{print $2}')"
toolbox_media_sync_ready="$("${ROOT_DIR}/scripts/toolbox_media_sync_check.sh" 2>/dev/null | awk -F= '/^toolbox_media_sync_ready=/{print $2}')"
radio_ops_ready="$("${ROOT_DIR}/scripts/radio_operations_check.sh" 2>/dev/null | awk -F= '/^radio_operations_ready=/{print $2}')"
surface_remote_ready="$("${ROOT_DIR}/scripts/surface_go_frontend_check.sh" 2>/dev/null | awk -F= '/^surface_go_remote_admin_ready=/{print $2}')"
pbs_ready="$("${ROOT_DIR}/scripts/pbs_stage_gate_check.sh" 2>/dev/null | awk -F= '/^pbs_stage_gate_ready=/{print $2}')"
pbs_proof_ready="$("${ROOT_DIR}/scripts/pbs_proof_backup_check.sh" 2>/dev/null | awk -F= '/^pbs_proof_backup_exists=/{print $2}')"
security_status="$("${ROOT_DIR}/scripts/security_baseline_check.sh" 2>/dev/null | awk -F= '/^security_status=/{print $2}')"

brief_value "ops_brief_generated_at" "$(date '+%Y-%m-%d %H:%M:%S %Z')"
brief_value "radio_operations_ready" "${radio_ops_ready:-unknown}"
brief_value "toolbox_media_server_ready" "${toolbox_media_ready:-unknown}"
brief_value "toolbox_jellyfin_ui_ready" "${toolbox_jellyfin_ui_ready:-unknown}"
brief_value "toolbox_media_sync_ready" "${toolbox_media_sync_ready:-unknown}"
brief_value "surface_go_remote_admin_ready" "${surface_remote_ready:-unknown}"
brief_value "pbs_stage_gate_ready" "${pbs_ready:-unknown}"
brief_value "pbs_proof_backup_exists" "${pbs_proof_ready:-unknown}"
brief_value "security_status" "${security_status:-unknown}"

if [[ "${radio_ops_ready}" == "yes" && "${toolbox_media_ready}" == "yes" && "${toolbox_media_sync_ready}" == "yes" && "${security_status}" == "ok" ]]; then
  echo "ops_brief_platform_core=yes"
else
  echo "ops_brief_platform_core=no"
fi

if [[ "${toolbox_media_sync_ready}" != "yes" ]]; then
  echo "recommendation=allow_media_sync_to_seed_jellyfin_library_then_begin_client_rollout"
elif [[ "${toolbox_jellyfin_ui_ready}" != "yes" ]]; then
  echo "recommendation=finish_jellyfin_ui_setup_before_client_rollout"
elif [[ "${surface_remote_ready}" != "yes" ]]; then
  echo "recommendation=wake_surface_then_resume_surface_acceptance"
elif [[ "${pbs_ready}" != "yes" ]]; then
  echo "recommendation=finish_pbs_restore_drill_path_and_operationalize_backup_target"
else
  echo "recommendation=finish_ui_setup_and_client_rollout"
fi
