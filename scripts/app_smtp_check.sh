#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

read_effective_var() {
  local key="$1"
  python3 "${ROOT_DIR}/scripts/app_smtp_runtime_vars.py" --get "${key}"
}

remote_guest() {
  local host_key="$1"
  local command="$2"
  run_inventory_guest_remote "${host_key}" "${command}" "wolf" 2>/dev/null || true
}

remote_radio() {
  local command="$1"
  run_inventory_remote "raspberry_pi_radio" "${command}" "wolf" 2>/dev/null || true
}

SMTP_ENABLED="$(read_effective_var homeserver_mail_app_smtp_enabled)"
SMTP_HOST="$(read_effective_var homeserver_mail_smtp_host)"
SMTP_PORT="$(read_effective_var homeserver_mail_smtp_port)"
SMTP_SECURE="$(read_effective_var homeserver_mail_smtp_secure)"
SMTP_FROM="$(read_effective_var homeserver_mail_sender_email)"
SMTP_USER="$(read_effective_var homeserver_mail_smtp_auth_username)"
SMTP_PASSWORD="$(read_effective_var homeserver_vault_mail_smtp_password)"

app_smtp_policy_ready="yes"
if [[ "${SMTP_ENABLED}" != "true" || -z "${SMTP_HOST}" || -z "${SMTP_PORT}" || -z "${SMTP_FROM}" || -z "${SMTP_USER}" || -z "${SMTP_PASSWORD}" ]]; then
  app_smtp_policy_ready="no"
fi

NEXTCLOUD_CONFIG_DUMP="$(
  ANSIBLE_CONFIG="${ROOT_DIR}/ansible.cfg" \
  ansible nextcloud_vm \
    -i "${ROOT_DIR}/ansible/inventory/hosts.yml" \
    -b \
    -m shell \
    -a 'grep -n "mail_" /var/lib/docker/volumes/nextcloud_nextcloud/_data/config/config.php || true' \
    2>/dev/null || true
)"

nextcloud_config_value() {
  local key="$1"
  printf '%s\n' "${NEXTCLOUD_CONFIG_DUMP}" | awk -v key="${key}" -F"'" '$2 == key {print $4; exit}'
}

NEXTCLOUD_HOST="$(nextcloud_config_value mail_smtphost)"
NEXTCLOUD_PORT="$(nextcloud_config_value mail_smtpport)"
NEXTCLOUD_MODE="$(nextcloud_config_value mail_smtpmode)"
NEXTCLOUD_USER="$(nextcloud_config_value mail_smtpname)"
NEXTCLOUD_SECURE="$(nextcloud_config_value mail_smtpsecure)"
NEXTCLOUD_FROM_LOCALPART="$(nextcloud_config_value mail_from_address)"
NEXTCLOUD_FROM_DOMAIN="$(nextcloud_config_value mail_domain)"

PAPERLESS_ENV="$(remote_guest paperless_vm "sudo test -f /opt/homeserver2027/stacks/paperless/stack.env && sudo cat /opt/homeserver2027/stacks/paperless/stack.env")"
PAPERLESS_HOST="$(printf '%s\n' "${PAPERLESS_ENV}" | awk -F= '/^PAPERLESS_EMAIL_HOST=/{print $2; exit}')"
PAPERLESS_PORT="$(printf '%s\n' "${PAPERLESS_ENV}" | awk -F= '/^PAPERLESS_EMAIL_PORT=/{print $2; exit}')"
PAPERLESS_FROM="$(printf '%s\n' "${PAPERLESS_ENV}" | awk -F= '/^PAPERLESS_EMAIL_FROM=/{print $2; exit}')"
PAPERLESS_USER="$(printf '%s\n' "${PAPERLESS_ENV}" | awk -F= '/^PAPERLESS_EMAIL_HOST_USER=/{print $2; exit}')"

ODOO_CONF="$(remote_guest odoo_vm "sudo test -f /opt/homeserver2027/stacks/odoo/odoo.conf && sudo cat /opt/homeserver2027/stacks/odoo/odoo.conf")"
ODOO_HOST="$(printf '%s\n' "${ODOO_CONF}" | awk -F= '/^smtp_server[[:space:]]*=/{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2; exit}')"
ODOO_PORT="$(printf '%s\n' "${ODOO_CONF}" | awk -F= '/^smtp_port[[:space:]]*=/{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2; exit}')"
ODOO_FROM="$(printf '%s\n' "${ODOO_CONF}" | awk -F= '/^email_from[[:space:]]*=/{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2; exit}')"
ODOO_USER="$(printf '%s\n' "${ODOO_CONF}" | awk -F= '/^smtp_user[[:space:]]*=/{gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2; exit}')"

AZURACAST_SETTINGS="$(remote_radio "cd /var/azuracast && docker exec azuracast azuracast_cli azuracast:settings:list")"
azuracast_host_ok="no"
azuracast_port_ok="no"
azuracast_from_ok="no"
azuracast_user_ok="no"
azuracast_secure_ok="no"

if grep -Eiq "mail_smtp_host.*${SMTP_HOST}" <<<"${AZURACAST_SETTINGS}"; then
  azuracast_host_ok="yes"
fi
if grep -Eiq "mail_smtp_port.*${SMTP_PORT}" <<<"${AZURACAST_SETTINGS}"; then
  azuracast_port_ok="yes"
fi
if grep -Eiq "mail_sender_email.*${SMTP_FROM}" <<<"${AZURACAST_SETTINGS}"; then
  azuracast_from_ok="yes"
fi
if grep -Eiq "mail_smtp_username.*${SMTP_USER}" <<<"${AZURACAST_SETTINGS}"; then
  azuracast_user_ok="yes"
fi
if grep -Eiq "mail_smtp_secure.*${SMTP_SECURE}" <<<"${AZURACAST_SETTINGS}"; then
  azuracast_secure_ok="yes"
fi

nextcloud_expected_localpart="${SMTP_FROM%@*}"
nextcloud_expected_domain="${SMTP_FROM#*@}"

nextcloud_app_smtp_ready="no"
if [[ "${NEXTCLOUD_HOST}" == "${SMTP_HOST}" && "${NEXTCLOUD_PORT}" == "${SMTP_PORT}" && "${NEXTCLOUD_MODE}" == "smtp" && "${NEXTCLOUD_USER}" == "${SMTP_USER}" && "${NEXTCLOUD_SECURE}" == "${SMTP_SECURE}" && "${NEXTCLOUD_FROM_LOCALPART}" == "${nextcloud_expected_localpart}" && "${NEXTCLOUD_FROM_DOMAIN}" == "${nextcloud_expected_domain}" ]]; then
  nextcloud_app_smtp_ready="yes"
fi

paperless_app_smtp_ready="no"
if [[ "${PAPERLESS_HOST}" == "${SMTP_HOST}" && "${PAPERLESS_PORT}" == "${SMTP_PORT}" && "${PAPERLESS_FROM}" == "${SMTP_FROM}" && "${PAPERLESS_USER}" == "${SMTP_USER}" ]]; then
  paperless_app_smtp_ready="yes"
fi

odoo_app_smtp_ready="no"
if [[ "${ODOO_HOST}" == "${SMTP_HOST}" && "${ODOO_PORT}" == "${SMTP_PORT}" && "${ODOO_FROM}" == "${SMTP_FROM}" && "${ODOO_USER}" == "${SMTP_USER}" ]]; then
  odoo_app_smtp_ready="yes"
fi

azuracast_app_smtp_ready="no"
if [[ "${azuracast_host_ok}" == "yes" && "${azuracast_port_ok}" == "yes" && "${azuracast_from_ok}" == "yes" && "${azuracast_user_ok}" == "yes" && "${azuracast_secure_ok}" == "yes" ]]; then
  azuracast_app_smtp_ready="yes"
fi

core_business_app_smtp_ready="no"
if [[ "${nextcloud_app_smtp_ready}" == "yes" && "${paperless_app_smtp_ready}" == "yes" && "${odoo_app_smtp_ready}" == "yes" ]]; then
  core_business_app_smtp_ready="yes"
fi

app_smtp_redeploy_ready="${app_smtp_policy_ready}"
app_smtp_ready="no"
if [[ "${app_smtp_policy_ready}" == "yes" && "${nextcloud_app_smtp_ready}" == "yes" && "${paperless_app_smtp_ready}" == "yes" && "${odoo_app_smtp_ready}" == "yes" && "${azuracast_app_smtp_ready}" == "yes" ]]; then
  app_smtp_ready="yes"
fi

echo "app_smtp_policy_ready=${app_smtp_policy_ready}"
echo "app_smtp_redeploy_ready=${app_smtp_redeploy_ready}"
echo "nextcloud_app_smtp_ready=${nextcloud_app_smtp_ready}"
echo "paperless_app_smtp_ready=${paperless_app_smtp_ready}"
echo "odoo_app_smtp_ready=${odoo_app_smtp_ready}"
echo "core_business_app_smtp_ready=${core_business_app_smtp_ready}"
echo "azuracast_app_smtp_ready=${azuracast_app_smtp_ready}"
echo "app_smtp_ready=${app_smtp_ready}"

if [[ "${app_smtp_policy_ready}" != "yes" ]]; then
  if [[ "${core_business_app_smtp_ready}" == "yes" && "${azuracast_app_smtp_ready}" != "yes" ]]; then
    echo "recommendation=core_business_apps_live_but_redeploy_secret_missing_and_azuracast_not_finished"
  elif [[ "${SMTP_ENABLED}" == "true" && -n "${SMTP_HOST}" && -n "${SMTP_PORT}" && -n "${SMTP_FROM}" && -n "${SMTP_USER}" && -z "${SMTP_PASSWORD}" ]]; then
    echo "recommendation=inject_runtime_smtp_password_then_deploy"
  else
    echo "recommendation=finalize_mail_model_and_enable_app_smtp_baseline"
  fi
elif [[ "${app_smtp_ready}" == "yes" ]]; then
  echo "recommendation=run_visible_app_smtp_test_mail_acceptance"
elif [[ "${nextcloud_app_smtp_ready}" == "yes" && "${paperless_app_smtp_ready}" == "yes" && "${odoo_app_smtp_ready}" == "yes" && "${azuracast_app_smtp_ready}" != "yes" ]]; then
  echo "recommendation=repair_raspberry_pi_radio_ssh_then_finish_azuracast_smtp"
else
  echo "recommendation=deploy_or_repair_app_smtp_baseline"
fi
