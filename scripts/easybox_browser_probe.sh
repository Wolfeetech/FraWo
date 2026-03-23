#!/usr/bin/env bash
set -euo pipefail

AUTOMATION_DIR="/tmp/easybox-automation"
GECKODRIVER_BIN="${GECKODRIVER_BIN:-/snap/bin/geckodriver}"
FIREFOX_BIN="${FIREFOX_BIN:-}"
EASYBOX_BASE_URL="${EASYBOX_BASE_URL:-https://192.168.2.1}"

if ! command -v node >/dev/null 2>&1; then
  echo "error=node_not_found" >&2
  exit 1
fi

if [ ! -x "${GECKODRIVER_BIN}" ]; then
  echo "error=geckodriver_not_found path=${GECKODRIVER_BIN}" >&2
  exit 1
fi

if [ -n "${FIREFOX_BIN}" ] && [ ! -x "${FIREFOX_BIN}" ]; then
  echo "error=firefox_not_found path=${FIREFOX_BIN}" >&2
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

cd "${AUTOMATION_DIR}"

GECKODRIVER_BIN="${GECKODRIVER_BIN}" FIREFOX_BIN="${FIREFOX_BIN}" EASYBOX_BASE_URL="${EASYBOX_BASE_URL}" node <<'NODE'
const {Builder} = require('selenium-webdriver');
const firefox = require('selenium-webdriver/firefox');

function parseUserLang(raw) {
  const parsed = JSON.parse(raw);
  const flat = {};
  for (const entry of parsed) {
    const key = Object.keys(entry)[0];
    flat[key] = entry[key];
  }
  return flat;
}

(async () => {
  const options = new firefox.Options();
  if (process.env.FIREFOX_BIN) {
    options.setBinary(process.env.FIREFOX_BIN);
  }
  options.addArguments('-headless');
  options.setAcceptInsecureCerts(true);
  options.setPreference('network.dns.disableIPv6', true);

  const service = new firefox.ServiceBuilder(process.env.GECKODRIVER_BIN);
  const driver = await new Builder()
    .forBrowser('firefox')
    .setFirefoxOptions(options)
    .setFirefoxService(service)
    .build();

  try {
    const baseUrl = process.env.EASYBOX_BASE_URL.replace(/\/+$/, '');
    await driver.get(baseUrl + '/login.html');
    await driver.sleep(3000);

    const title = await driver.getTitle();
    const url = await driver.getCurrentUrl();
    const source = await driver.getPageSource();
    const result = await driver.executeAsyncScript(function(done) {
      fetch('/data/user_lang.json?_=' + Date.now() + '&csrf_token=' + (window.csrf_token || ''))
        .then(async (response) => {
          const text = await response.text();
          done(JSON.stringify({
            ok: true,
            status: response.status,
            text
          }));
        })
        .catch((error) => {
          done(JSON.stringify({
            ok: false,
            error: String(error)
          }));
        });
    });

    const probe = JSON.parse(result);
    console.log(`browser_probe_ready=${source.length > 0 ? 'yes' : 'no'}`);
    console.log(`probe_base_url=${baseUrl}`);
    console.log(`login_page_title=${title}`);
    console.log(`login_page_url=${url}`);

    if (!probe.ok) {
      console.log('user_lang_fetch_status=error');
      console.log(`user_lang_fetch_error=${probe.error}`);
      process.exit(1);
    }

    console.log(`user_lang_fetch_status=${probe.status}`);
    const data = parseUserLang(probe.text);
    const fields = [
      'fw_version',
      'lang_code',
      'trying_times',
      'delay_time',
      'already_login',
      'password_enable',
      'credential_detail',
      'wan_ip4_addr',
      'wan_ip6_addr',
      'aftr_addr'
    ];
    for (const field of fields) {
      console.log(`${field}=${data[field] ?? ''}`);
    }
  } finally {
    await driver.quit();
  }
})().catch((error) => {
  console.error(`browser_probe_error=${String(error)}`);
  process.exit(1);
});
NODE
