/**
 * FraWo Vaultwarden Setup Script v2
 * Uses new Vaultwarden 1.35.x registration API:
 *   POST /identity/accounts/register/send-verification-email -> JWT token
 *   POST /identity/accounts/register/finish -> complete registration
 * Then logs in and stores all infrastructure credentials.
 */

import crypto from 'crypto';
import http from 'http';

const VAULT_URL = 'http://127.0.0.1:8080';
const AGENT_EMAIL = 'agent@frawo-tech.de';
const AGENT_NAME = 'FraWo Agent';
const AGENT_PASSWORD = 'FrawoAgent2026!';
const KDF_ITERATIONS = 600000;

// ---- Crypto Helpers ----

function pbkdf2(password, salt, iterations, keylen) {
  return crypto.pbkdf2Sync(
    typeof password === 'string' ? Buffer.from(password, 'utf8') : password,
    typeof salt === 'string' ? Buffer.from(salt, 'utf8') : salt,
    iterations, keylen, 'sha256'
  );
}

function hkdfExpand(prk, info, length) {
  const hashLen = 32;
  const n = Math.ceil(length / hashLen);
  const blocks = [];
  let t = Buffer.alloc(0);
  for (let i = 1; i <= n; i++) {
    const hmac = crypto.createHmac('sha256', prk);
    hmac.update(t);
    hmac.update(info);
    hmac.update(Buffer.from([i]));
    t = hmac.digest();
    blocks.push(t);
  }
  return Buffer.concat(blocks).slice(0, length);
}

function encryptAesCbc256B64(plaintext, encKey, macKey) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', encKey, iv);
  const ct = Buffer.concat([cipher.update(Buffer.from(plaintext, 'utf8')), cipher.final()]);
  const hmac = crypto.createHmac('sha256', macKey);
  hmac.update(iv);
  hmac.update(ct);
  const mac = hmac.digest();
  return `2.${iv.toString('base64')}|${ct.toString('base64')}|${mac.toString('base64')}`;
}

function encryptBytes(data, encKey, macKey) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', encKey, iv);
  const ct = Buffer.concat([cipher.update(data), cipher.final()]);
  const hmac = crypto.createHmac('sha256', macKey);
  hmac.update(iv);
  hmac.update(ct);
  const mac = hmac.digest();
  return `2.${iv.toString('base64')}|${ct.toString('base64')}|${mac.toString('base64')}`;
}

async function apiRequest(method, path, body, token) {
  return new Promise((resolve, reject) => {
    const url = new URL(VAULT_URL + path);
    const options = {
      hostname: url.hostname,
      port: url.port || 80,
      path: url.pathname + url.search,
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    if (token) options.headers['Authorization'] = `Bearer ${token}`;
    const bodyStr = body ? JSON.stringify(body) : null;
    if (bodyStr) options.headers['Content-Length'] = Buffer.byteLength(bodyStr);

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = data ? JSON.parse(data) : {};
          resolve({ status: res.statusCode, body: parsed });
        } catch {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });
    req.on('error', reject);
    if (bodyStr) req.write(bodyStr);
    req.end();
  });
}

async function tokenRequest(formData) {
  return new Promise((resolve, reject) => {
    const url = new URL(VAULT_URL + '/identity/connect/token');
    const body = Object.entries(formData).map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&');
    const options = {
      hostname: url.hostname,
      port: url.port || 80,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(body)
      }
    };
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, body: data }); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ---- Main Setup ----

async function main() {
  console.log('=== FraWo Vaultwarden Setup v2 ===\n');

  // 1. Derive keys
  console.log('Deriving master key...');
  const masterKey = pbkdf2(AGENT_PASSWORD, AGENT_EMAIL.toLowerCase(), KDF_ITERATIONS, 32);
  const stretchedMasterKey = Buffer.concat([
    hkdfExpand(masterKey, Buffer.from('enc'), 32),
    hkdfExpand(masterKey, Buffer.from('mac'), 32)
  ]);
  const encKey = stretchedMasterKey.slice(0, 32);
  const macKey = stretchedMasterKey.slice(32, 64);

  // Master password hash (sent to server)
  const masterPasswordHash = pbkdf2(masterKey, AGENT_PASSWORD, 1, 32).toString('base64');

  // Generate random symmetric key (64 bytes = 32 AES + 32 MAC)
  const symKey = crypto.randomBytes(64);
  const protectedSymKey = encryptBytes(symKey, encKey, macKey);

  // Generate RSA key pair for Bitwarden (4096-bit)
  console.log('Generating RSA key pair...');
  const { privateKey: rsaPrivate, publicKey: rsaPublic } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'der' },
    privateKeyEncoding: { type: 'pkcs8', format: 'der' }
  });

  const symEncKey = symKey.slice(0, 32);
  const symMacKey = symKey.slice(32, 64);
  const encryptedPrivateKey = encryptBytes(rsaPrivate, symEncKey, symMacKey);
  const publicKeyB64 = rsaPublic.toString('base64');

  // 2. Get verification token (new Vaultwarden 1.35.x flow)
  console.log('Getting registration token...');
  const tokenRes = await apiRequest('POST', '/identity/accounts/register/send-verification-email', {
    email: AGENT_EMAIL,
    name: AGENT_NAME,
    receiveMarketingEmails: false
  });
  console.log(`Token response: ${tokenRes.status}`);

  if (tokenRes.status !== 200) {
    console.error('Failed to get token:', tokenRes.body);
    process.exit(1);
  }

  const emailVerificationToken = typeof tokenRes.body === 'string'
    ? tokenRes.body.replace(/^"|"$/g, '')
    : tokenRes.body;
  console.log('Got verification token ✅');

  // 3. Complete registration
  console.log('Completing registration...');
  const regRes = await apiRequest('POST', '/identity/accounts/register/finish', {
    email: AGENT_EMAIL,
    emailVerificationToken,
    masterPasswordHash,
    masterPasswordHint: '',
    name: AGENT_NAME,
    userSymmetricKey: protectedSymKey,
    userAsymmetricKeys: {
      encryptedPrivateKey,
      publicKey: publicKeyB64
    },
    kdfType: 0,
    kdfIterations: KDF_ITERATIONS,
    kdfMemory: null,
    kdfParallelism: null,
    captchaResponse: null,
    organizationUserId: null
  });

  console.log(`Registration finish: ${regRes.status}`);
  if (regRes.status !== 200 && regRes.status !== 204) {
    console.error('Registration failed:', JSON.stringify(regRes.body).slice(0, 300));
    // If user already has password set, try login anyway
    if (regRes.status !== 400) process.exit(1);
  } else {
    console.log('Registration complete ✅');
  }

  // 4. Login
  console.log('Logging in...');
  const loginRes = await tokenRequest({
    grant_type: 'password',
    username: AGENT_EMAIL,
    password: masterPasswordHash,
    scope: 'api offline_access',
    client_id: 'cli',
    device_type: 9,
    device_identifier: crypto.randomUUID(),
    device_name: 'frawo-ops-script'
  });

  if (loginRes.status !== 200 || !loginRes.body.access_token) {
    console.error('Login failed:', JSON.stringify(loginRes.body).slice(0, 200));
    process.exit(1);
  }
  const token = loginRes.body.access_token;
  console.log('Login ✅');

  // Confirm who we are
  const syncRes = await apiRequest('GET', '/api/sync?excludeDomains=true', null, token);
  console.log(`Logged in as: ${syncRes.body?.Profile?.Email}`);

  function enc(text) {
    if (!text) return null;
    return encryptAesCbc256B64(text, symEncKey, symMacKey);
  }

  // 5. Create all credential items
  const credentials = [
    {
      name: 'AdGuard Home - CT 100',
      username: 'admin',
      password: 'FrawoAdGuard2026!',
      url: 'http://adguard.hs27.internal',
      notes: 'AdGuard Home DNS Server auf CT 100. Auth heute aktiviert (war vorher offen!).'
    },
    {
      name: 'Portainer CE - frawo-docker-1',
      username: 'admin',
      password: 'FrawoPortainer2026!',
      url: 'http://portainer.hs27.internal',
      notes: 'Portainer Docker Management auf frawo-docker-1. Heute repariert (war nie initialisiert).'
    },
    {
      name: 'Grafana - frawo-docker-1',
      username: 'admin',
      password: 'FrawoGrafana2026!',
      url: 'http://grafana.hs27.internal',
      notes: 'Grafana Monitoring Dashboard auf frawo-docker-1.'
    },
    {
      name: 'Prometheus - frawo-docker-1',
      username: '',
      password: '',
      url: 'http://prometheus.hs27.internal',
      notes: 'Prometheus Metrics. Kein Login erforderlich (intern). Port 9091.'
    },
    {
      name: 'Odoo 17 ERP - VM 220',
      username: 'admin',
      password: 'AuditTemp2026!',
      url: 'http://odoo.hs27.internal',
      notes: 'ACHTUNG: Temporaeres Passwort! Sofort aendern unter Einstellungen -> Passwort. VM 220 (10.4.0.22).'
    },
    {
      name: 'Nextcloud - VM 300',
      username: 'frawoadmin',
      password: 'D6V/HDBoI3Y9DqkVw8O6NiNj',
      url: 'https://cloud.frawo-tech.de',
      notes: 'Nextcloud Admin. VM 300 (10.4.0.21). Intern: cloud.hs27.internal'
    },
    {
      name: 'Paperless-ngx - VM 330',
      username: 'frawoadmin',
      password: 'n82DMJKSAydZqeKF8/BxTq08',
      url: 'http://paperless.hs27.internal',
      notes: 'Paperless Dokumentenverwaltung. VM 330 (10.4.0.23).'
    },
    {
      name: 'n8n Automation - frawo-docker-1',
      username: '',
      password: '',
      url: 'http://n8n.hs27.internal',
      notes: 'n8n Workflow Automation. frawo-docker-1 (100.94.32.41). Port 5678. Eigene Nutzerkonten in n8n erstellen.'
    },
    {
      name: 'Navidrome - CT 130',
      username: '',
      password: '',
      url: 'http://navidrome.hs27.internal',
      notes: 'Navidrome Music Server. CT 130 (10.4.0.28). Port 4533. Nutzerkonten in Navidrome verwalten.'
    },
    {
      name: 'AzuraCast - CT 130 (FraWo Funk Radio)',
      username: '',
      password: '',
      url: 'https://funk.frawo-tech.de',
      notes: 'AzuraCast Radio Server. CT 130 (10.4.0.28). Intern: radio.hs27.internal. Login in AzuraCast selbst.'
    },
    {
      name: 'Home Assistant - VM 210',
      username: '',
      password: '',
      url: 'https://home.frawo-tech.de',
      notes: 'Home Assistant OS. VM 210 (10.4.0.24). Intern: ha.hs27.internal:8123.'
    },
    {
      name: 'PVE Proxmox Web UI - ANKER',
      username: 'root',
      password: '',
      url: 'https://pve.hs27.internal:8006',
      notes: 'Proxmox VE Web UI. 10.4.0.99, Tailscale: 100.69.179.87. SSH via pve_ed25519 Key.'
    },
    {
      name: 'frawo-docker-1 SSH',
      username: 'wolf',
      password: '1Vaudeville! (ALT - PasswordAuth deaktiviert!)',
      url: 'ssh://100.94.32.41',
      notes: 'SSH nur via Key! hs27_ops_ed25519. Debian 13 Trixie, 188G. Tailscale: 100.94.32.41. PasswordAuth deaktiviert.'
    },
    {
      name: 'SMTP - Strato Webmaster',
      username: 'webmaster@frawo-tech.de',
      password: 'Frawo0426!!',
      url: 'smtp://smtp.strato.de:587',
      notes: 'SMTP fuer alle Server-Benachrichtigungen (Vaultwarden, Paperless, etc.). STARTTLS Port 587.'
    },
    {
      name: 'Odoo PostgreSQL DB - VM 220',
      username: 'odoo',
      password: 'odoo_db_pass_final_v1',
      url: 'postgresql://10.4.0.22:5432/odoo',
      notes: 'Odoo Datenbank. Schwaches Passwort -> nach Odoo-Admin-PW-Aenderung auch DB-PW aendern.'
    },
    {
      name: 'Nextcloud MariaDB - VM 300',
      username: 'nextcloud',
      password: 'GEfM5UJ7o7rRWLv2',
      url: 'mysql://10.4.0.21:3306/nextcloud',
      notes: 'Nextcloud Datenbank. Root-PW: O55MCbOa6VM2yR2c'
    },
    {
      name: 'Paperless PostgreSQL - VM 330',
      username: 'paperless',
      password: 'wFtCudp+4kH6fDqg',
      url: 'postgresql://10.4.0.23:5432/paperless',
      notes: 'Paperless Datenbank.'
    },
    {
      name: 'Vaultwarden Agent Account',
      username: AGENT_EMAIL,
      password: AGENT_PASSWORD,
      url: 'http://vault.hs27.internal',
      notes: 'Dieses Konto! Erstellt von FraWo Agent Script. Fuer automatisierte Credential-Verwaltung.'
    },
    {
      name: 'Vaultwarden Admin Panel',
      username: 'admin',
      password: 'FrawoAdminVault2026!',
      url: 'http://vault.hs27.internal/admin',
      notes: 'Vaultwarden Admin Panel. Plain-text token (temporaer, argon2id Hash kaputt durch sed). Bitte sichern!'
    }
  ];

  console.log(`\nCreating ${credentials.length} credential items...`);
  let created = 0;
  for (const cred of credentials) {
    const item = {
      type: 1,
      name: enc(cred.name),
      notes: cred.notes ? enc(cred.notes) : null,
      login: {
        uris: cred.url ? [{ match: null, uri: enc(cred.url) }] : null,
        username: cred.username ? enc(cred.username) : null,
        password: cred.password ? enc(cred.password) : null,
        totp: null
      },
      favorite: false,
      reprompt: 0,
      fields: [],
      folderId: null,
      collectionIds: []
    };

    const res = await apiRequest('POST', '/api/ciphers', item, token);
    if (res.status === 200 || res.status === 201) {
      console.log(`  OK: ${cred.name}`);
      created++;
    } else {
      console.log(`  FAIL: ${cred.name}: ${res.status} ${JSON.stringify(res.body).slice(0, 100)}`);
    }
  }

  console.log(`\n=== FERTIG ===`);
  console.log(`${created}/${credentials.length} Items gespeichert`);
  console.log(`\nZugang zum Agent-Vault:`);
  console.log(`  URL:      http://vault.hs27.internal`);
  console.log(`  Email:    ${AGENT_EMAIL}`);
  console.log(`  Passwort: ${AGENT_PASSWORD}`);
  console.log(`\nWICHTIG: Odoo Admin-Passwort noch aendern! (AuditTemp2026!)`);
}

main().catch(console.error);
