# Device Rollout Preflight

Decision: `ready_for_manual_device_acceptance`

## Start Paths

- `surface_laptop_start`: `passed` - url=`http://portal.hs27.internal/franz/` status=`200` final_url=`http://portal.hs27.internal/franz/` title=``
- `iphone_mobile_start`: `passed` - url=`http://100.99.206.128:8447/franz/` status=`200` final_url=`http://100.99.206.128:8447/franz/` title=`Arbeitsplatz Franz`

## Core Targets

- `nextcloud`: `passed` - url=`http://cloud.hs27.internal/` status=`200` final_url=`http://cloud.hs27.internal/login` title=`Login – Nextcloud`
- `paperless`: `passed` - url=`http://paperless.hs27.internal/accounts/login/` status=`200` final_url=`http://paperless.hs27.internal/accounts/login/` title=`Paperless-ngx sign in`
- `odoo`: `passed` - url=`http://odoo.hs27.internal/web/login` status=`200` final_url=`http://odoo.hs27.internal/web/login` title=`Login | FraWo`
- `vaultwarden`: `passed` - url=`https://vault.hs27.internal/` status=`200` final_url=`https://vault.hs27.internal/` title=`Vaultwarden Web`

## Expected Franz Start Links

- `Nextcloud` -> `http://cloud.hs27.internal/`
- `Paperless` -> `http://paperless.hs27.internal/accounts/login/`
- `Odoo` -> `http://odoo.hs27.internal/web/login`
- `Vault` -> `https://vault.hs27.internal/`
- `Franz Mobil Start` -> `http://100.99.206.128:8447/franz/`
