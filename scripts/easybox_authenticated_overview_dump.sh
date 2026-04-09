#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUTOMATION_DIR="/tmp/easybox-automation"
GECKODRIVER_BIN="${GECKODRIVER_BIN:-/snap/bin/geckodriver}"
EASYBOX_BASE_URL="${EASYBOX_BASE_URL:-https://192.168.2.1}"

get_ansible_var() {
  local var_name="$1"
  local vars_file="$2"
  ansible localhost -m debug -a "msg={{ ${var_name} | trim }}" -e "@${vars_file}" -c local 2>/dev/null \
    | awk -F'"' '/"msg":/ {print $4; exit}'
}

if ! command -v node >/dev/null 2>&1; then
  echo "error=node_not_found" >&2
  exit 1
fi

if ! command -v ansible >/dev/null 2>&1; then
  echo "error=ansible_not_found" >&2
  exit 1
fi

if [ ! -x "${GECKODRIVER_BIN}" ]; then
  echo "error=geckodriver_not_found path=${GECKODRIVER_BIN}" >&2
  exit 1
fi

mkdir -p "${AUTOMATION_DIR}"

if [ ! -f "${AUTOMATION_DIR}/package.json" ]; then
  (
    cd "${AUTOMATION_DIR}"
    npm init -y >/dev/null 2>&1
  )
fi

if [ ! -d "${AUTOMATION_DIR}/node_modules/selenium-webdriver" ]; then
  (
    cd "${AUTOMATION_DIR}"
    npm install --silent selenium-webdriver
  )
fi

ROUTER_USERNAME="$(get_ansible_var homeserver_router_login_username "${ROOT_DIR}/ansible/inventory/group_vars/all/main.yml")"
ROUTER_PASSWORD="$(get_ansible_var homeserver_vault_easybox_password "${ROOT_DIR}/ansible/inventory/group_vars/all/vault.yml")"

if [ -z "${ROUTER_PASSWORD}" ]; then
  echo "error=easybox_password_not_available" >&2
  exit 1
fi

cd "${AUTOMATION_DIR}"

GECKODRIVER_BIN="${GECKODRIVER_BIN}" \
EASYBOX_BASE_URL="${EASYBOX_BASE_URL}" \
ROUTER_USERNAME="${ROUTER_USERNAME}" \
ROUTER_PASSWORD="${ROUTER_PASSWORD}" \
node <<'NODE'
const {Builder, By} = require('selenium-webdriver');
const firefox = require('selenium-webdriver/firefox');

function decodeBase64Safe(value) {
  try {
    return Buffer.from(value, 'base64').toString('utf8');
  } catch {
    return value;
  }
}

function parseWifiUsers(raw) {
  return raw
    .split(';')
    .filter(Boolean)
    .map((record) => {
      const parts = record.split('|');
      return {
        transport: 'wifi',
        state: parts[0] || '',
        icon: parts[1] || '',
        name: decodeBase64Safe(parts[2] || ''),
        mac: (parts[3] || '').toLowerCase(),
        ip: parts[4] || '',
        ipv6: parts[5] || '',
        link_speed: parts[6] || '',
        phy: parts[7] || '',
        band: parts[8] || '',
      };
    });
}

function parseEthernetUsers(raw) {
  return raw
    .split(';')
    .filter(Boolean)
    .map((record) => {
      const parts = record.split('|');
      return {
        transport: 'ethernet',
        state: 'wired',
        icon: parts[0] || '',
        name: decodeBase64Safe(parts[1] || ''),
        mac: (parts[2] || '').toLowerCase(),
        ip: parts[3] || '',
        ipv6: parts[4] || '',
        link_speed: parts[5] || '',
        phy: 'ethernet',
        band: '',
      };
    });
}

function ipSortValue(ip) {
  return ip.split('.').reduce((acc, part) => (acc * 256) + Number(part), 0);
}

(async () => {
  const options = new firefox.Options();
  options.addArguments('-headless');
  options.setAcceptInsecureCerts(true);

  const service = new firefox.ServiceBuilder(process.env.GECKODRIVER_BIN);
  const driver = await new Builder()
    .forBrowser('firefox')
    .setFirefoxOptions(options)
    .setFirefoxService(service)
    .build();

  try {
    const baseUrl = process.env.EASYBOX_BASE_URL.replace(/\/+$/, '');
    await driver.get(baseUrl + '/login.html');
    await driver.sleep(2500);

    const pwd = await driver.findElement(By.css('#password-field'));
    await pwd.clear();
    await pwd.sendKeys(process.env.ROUTER_PASSWORD);
    await driver.findElement(By.css('.login-apply')).click();
    await driver.sleep(4500);

    const currentUrl = await driver.getCurrentUrl();
    const payload = await driver.executeAsyncScript(function(done) {
      fetch('/data/overview.json?_=' + Date.now() + '&csrf_token=' + (window.csrf_token || ''))
        .then(async (response) => {
          done(JSON.stringify({
            status: response.status,
            text: await response.text(),
          }));
        })
        .catch((error) => {
          done(JSON.stringify({
            error: String(error),
          }));
        });
    });

    const result = JSON.parse(payload);
    if (result.error) {
      console.log('authenticated_overview_ready=no');
      console.log(`login_result_url=${currentUrl}`);
      console.log(`overview_fetch_error=${result.error}`);
      process.exit(1);
    }

    const overview = JSON.parse(result.text);
    const wifiRaw = (overview.find((entry) => entry.wifi_user !== undefined) || {}).wifi_user || '';
    const ethernetRaw = (overview.find((entry) => entry.ethernet !== undefined) || {}).ethernet || '';
    const wifiDevices = parseWifiUsers(wifiRaw);
    const ethernetDevices = parseEthernetUsers(ethernetRaw);
    const allDevices = wifiDevices.concat(ethernetDevices).sort((a, b) => ipSortValue(a.ip) - ipSortValue(b.ip));

    console.log('authenticated_overview_ready=yes');
    console.log(`login_result_url=${currentUrl}`);
    console.log(`overview_status=${result.status}`);
    console.log(`wifi_device_count=${wifiDevices.length}`);
    console.log(`ethernet_device_count=${ethernetDevices.length}`);

    for (const device of allDevices) {
      const parts = [
        device.transport,
        device.ip,
        device.name,
        device.mac,
        device.icon,
        device.phy,
        device.band,
        device.link_speed,
        device.ipv6,
      ].map((value) => String(value).replace(/\|/g, '/'));
      console.log(`device_record=${parts.join('|')}`);
    }
  } finally {
    await driver.quit();
  }
})().catch((error) => {
  console.error(`authenticated_overview_error=${String(error)}`);
  process.exit(1);
});
NODE
