param(
    [string]$WebsiteHost = "www.frawo-tech.de",
    [string]$WebsiteTitle = "FraWo",
    [string]$RadioPath = "/radio/"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$homepageXml = @"
<t name="Home" t-name="website.homepage">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'homepage'"/>
    <div id="wrap" class="oe_structure">
      <section class="s_cover pt96 pb96 o_colored_level o_cc o_cc1">
        <div class="container">
          <div class="row align-items-center">
            <div class="col-lg-8">
              <h1>$WebsiteTitle</h1>
              <p class="lead">Digitale Arbeitsprozesse, klare Betriebsablaeufe und ein eigener Radiopfad fuer die GbR.</p>
              <p class="mb-0">
                <a class="btn btn-primary btn-lg me-2" href="/contactus">Kontakt</a>
                <a class="btn btn-outline-primary btn-lg" href="$RadioPath">Radio hoeren</a>
              </p>
            </div>
          </div>
        </div>
      </section>
      <section class="s_text_image pt64 pb64">
        <div class="container">
          <div class="row align-items-center g-4">
            <div class="col-lg-7">
              <h2>Klarer digitaler Kern</h2>
              <p>FraWo arbeitet mit einem kleinen, kontrollierten Open-Source-Stack aus Odoo, Nextcloud, Paperless und einem eigenen Radio-Pfad.</p>
              <p>Die Website bleibt bewusst schlank: Kontakt, Orientierung und der direkte Einstieg ins Radio.</p>
            </div>
            <div class="col-lg-5">
              <div class="card shadow-sm border-0">
                <div class="card-body p-4">
                  <h3 class="h4">Radio</h3>
                  <p class="mb-3">Der direkte Player-Pfad liegt unter <a href="$RadioPath">$RadioPath</a>.</p>
                  <a class="btn btn-outline-primary" href="$RadioPath">Zum Player</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>
"@

$homepageJson = @{
    en_US = $homepageXml
    de_DE = $homepageXml
} | ConvertTo-Json -Compress -Depth 5

$baseUrl = "https://$WebsiteHost"
$sql = @"
begin;

update website
set name = '$WebsiteTitle',
    domain = '$WebsiteHost'
where id = 1;

insert into ir_config_parameter (key, value, create_uid, write_uid, create_date, write_date)
values ('web.base.url', '$baseUrl', 1, 1, now(), now())
on conflict (key) do update
set value = excluded.value,
    write_uid = 1,
    write_date = now();

insert into ir_config_parameter (key, value, create_uid, write_uid, create_date, write_date)
values ('web.base.url.freeze', 'True', 1, 1, now(), now())
on conflict (key) do update
set value = excluded.value,
    write_uid = 1,
    write_date = now();

update ir_ui_view
set arch_db = `$JSON`$$homepageJson`$JSON`$::jsonb
where key = 'website.homepage';

with homepage_view as (
    select id from ir_ui_view where key = 'website.homepage'
),
homepage_keep as (
    select coalesce(
        min(wp.id) filter (where v.website_id = 1),
        min(wp.id)
    ) as keep_id
    from website_page wp
    join ir_ui_view v on v.id = wp.view_id
    join homepage_view hv on hv.id = wp.view_id
)
update website_page wp
set url = '/',
    is_published = case when wp.id = hk.keep_id then true else false end
from homepage_view hv, homepage_keep hk
where wp.view_id = hv.id;

commit;
"@
$sqlBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($sql))

$remote = @"
qm guest exec 220 -- bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
import base64
Path("/tmp/frawo_site.sql").write_bytes(base64.b64decode("$sqlBase64"))
PY
cd /opt/homeserver2027/stacks/odoo
docker-compose exec -T db psql -U odoo -d FraWo_GbR < /tmp/frawo_site.sql
docker-compose restart web'
"@

& $proxmoxExec -RemoteCommand $remote
