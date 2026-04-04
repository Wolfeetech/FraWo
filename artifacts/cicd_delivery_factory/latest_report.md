# CI/CD Delivery Factory Report

- Generated at: `2026-04-04T01:55:32+02:00`
- Status: `defined_not_deployed`
- Preferred CD controller: `coolify`
- Platform-independence rule: `build_once_deploy_anywhere_via_oci`
- Safe scope now: `repo_side_factory_only`

## Verified Start State

- Git remote is configured: `https://github.com/Wolfeetech/FraWo.git`.
- Current repo host is GitHub, so a thin GitHub Actions wrapper is a factual option.
- Anker DMZ target subnets are already canonical in UCG_NETWORK_ARCHITECTURE.md: VLAN 102 `10.2.0.0/24`, VLAN 103 `10.3.0.0/24`.
- Repo already contains `6` stack compose templates, but they are runtime templates, not standalone OCI app definitions.
- GHCR registry contract and env/secret contract docs now exist for the first reference app.
- A neutral compose deploy bundle now exists for the first reference app.
- Coolify host selection contract now exists and keeps the controller out of the DMZ and off the hypervisor host itself.
- Repo now contains `1` verified Dockerfile/Containerfile artifact for factory build work.
- App catalog now contains `1` factory-deploy-ready reference app candidate.

## Open Prerequisites

- OCI registry is still undecided.
- Coolify management host is still undecided.
- Stockenweiler secondary DMZ subnet and runtime node are not yet fixed facts.
- Prod secret distribution model for dev/prod is not yet encoded in the repo.

## Branch Model

- `feature` -> `ci_only`
- `develop` -> `auto_deploy_dev`
- `main` -> `promotion_only`
- `tags` -> `immutable_prod_release`

## Environments

- `dev`: exposure `internal_or_allowlisted`, trigger `merge_to_develop`
- `prod`: exposure `public_dmz`, trigger `daily_promotion_or_release_tag`

## Topology

- `anker_dmz` -> subnet `10.2.0.0/24`, role `primary_public_webnode_zone`
- `anker_dmz_radio` -> subnet `10.3.0.0/24`, role `radio_public_zone`
- `stockenweiler_dmz` -> subnet `tbd`, role `secondary_public_webnode_zone`

## Service Classes

- `stateless_public` -> HA `active_active_possible` / examples `landing_pages, player_frontends, small_public_apis`
- `stateful_public` -> HA `external_state_required` / examples `cms, db_backed_public_apps`
- `internal_business` -> HA `primary_plus_dr` / examples `odoo, nextcloud, paperless, vaultwarden`
- `smart_home` -> HA `separate_per_household` / examples `ha_rothkreuz, ha_stockenweiler`
- `hobby_media` -> HA `separate_release_track` / examples `azuracast, radio_side_projects`

## App Catalog

- Factory-ready now: `1` / `10`
- `frawo_public_website` -> class `stateful_public`, wave `3`, ready `false`
- `portal_frontdoor` -> class `stateless_public`, wave `2`, ready `false`
- `radio_player_frontend` -> class `stateless_public`, wave `1`, ready `true`
- `odoo` -> class `internal_business`, wave `4`, ready `false`
- `nextcloud` -> class `internal_business`, wave `4`, ready `false`
- `paperless` -> class `internal_business`, wave `4`, ready `false`
- `vaultwarden` -> class `internal_business`, wave `4`, ready `false`
- `home_assistant_rothkreuz` -> class `smart_home`, wave `5`, ready `false`
- `home_assistant_stockenweiler` -> class `smart_home`, wave `5`, ready `false`
- `azuracast` -> class `hobby_media`, wave `3`, ready `false`

## Registry Contract

- Preferred registry: `ghcr`
- Namespace: `ghcr.io/wolfeetech/frawo`
- First reference image: `ghcr.io/wolfeetech/frawo/radio-player-frontend`
- `develop` tags -> `dev-latest, sha-<gitsha>`
- `main` tags -> `main-latest, sha-<gitsha>`
- `release_tags` tags -> `v*`

## Env And Secret Contract

- env example: `apps/radio-player-frontend/env/dev.env.example`
- env example: `apps/radio-player-frontend/env/prod.env.example`
- contract doc: `deployment/factory/contracts/GHCR_CONTRACT.md`
- contract doc: `deployment/factory/contracts/SECRET_ENV_CONTRACT.md`
- future controller secret: `COOLIFY_DEV_WEBHOOK_RADIO_PLAYER_FRONTEND`
- future controller secret: `COOLIFY_PROD_PRIMARY_WEBHOOK_RADIO_PLAYER_FRONTEND`
- future controller secret: `COOLIFY_PROD_SECONDARY_WEBHOOK_RADIO_PLAYER_FRONTEND`

## Secret Distribution Model

- doc: `deployment/factory/contracts/SECRET_DISTRIBUTION_MODEL.md`
- GitHub environments: `dev, prod`
- Package push auth: `github_token_when_possible`
- Runtime secret plane: `coolify_per_environment_later`

## Coolify Host Contract

- Preferred target: `new_dedicated_internal_management_ct_or_vm_on_anker`
- Temporary fallback: `toolbox_only_if_no_dedicated_node_exists`
- rejected target: `proxmox_anker_host_itself`
- rejected target: `stock_pve`
- rejected target: `dmz_nodes`
- rejected target: `surface_go_frontend_while_unstable`
- contract doc: `deployment/coolify/COOLIFY_HOST_SELECTION.md`
- node spec doc: `deployment/coolify/COOLIFY_MANAGEMENT_NODE_SPEC.md`

## First Deploy Bundle

- app id: `radio_player_frontend`
- bundle: `deployment/factory/apps/radio-player-frontend/compose.yaml`
- readme: `deployment/factory/apps/radio-player-frontend/README.md`
- compose env example: `deployment/factory/apps/radio-player-frontend/compose.dev.env.example`
- compose env example: `deployment/factory/apps/radio-player-frontend/compose.prod.env.example`

## Release Train

- `dev_policy` -> `every_green_merge_to_develop_deploys_to_dev`
- `prod_policy` -> `daily_promote_last_green_dev_candidate_or_release_tag`
- `rollback_policy` -> `redeploy_last_known_good_immutable_tag`

## Backup Strategy

- layer: `git_iac_delivery_config`
- layer: `immutable_oci_artifacts`
- layer: `stateful_runtime_data`
- OCI retention: dev `20` / prod `10` / keep last good tag `True`
- Backup retention v1: daily `7` / weekly `4` / monthly `6`
- `stateless_public` -> `repo_plus_image_plus_config_then_redeploy`
- `stateful_public` -> `db_plus_volume_or_object_storage_backup`
- `internal_business` -> `pbs_or_proxmox_vm_backup_plus_app_native_consistency_backup`
- `smart_home` -> `per_household_full_backup_or_snapshot`
- `hobby_media` -> `db_plus_station_config_plus_media_source_truth`
- preserve first: `VM 210 azuracast-vm`
- preserve first: `CT 207 radio-wordpress-prod`
- preserve first: `CT 208 mariadb-server`
- preserve first: `CT 211 radio-api`
- Offsite rule: `rothkreuz_primary_stockenweiler_dr_or_secondary_not_dual_write_v1`

## Restore Strategy

- restore type: `redeploy_restore`
- restore type: `node_or_vm_restore`
- restore type: `app_or_data_restore`
- Drill policy: `monthly_visible_restore_drill_for_one_stateful_core_service_rotating_odoo_nextcloud_paperless_home_assistant`
- Promotion rule: `stateful_prod_changes_require_known_rollback_tag_and_visible_restore_path`
- `stateless_public` -> RTO `minutes` / RPO `near_zero`
- `internal_business` -> RTO `hours` / RPO `last_successful_backup_or_dump`
- `smart_home` -> RTO `hours` / RPO `last_household_backup`

## Non-Goals V1

- `dual_writing_odoo_across_sites`
- `dual_writing_nextcloud_across_sites`
- `dual_writing_paperless_across_sites`
- `wan_proxmox_cluster_as_delivery_foundation`
- `public_dev_without_restrictions`
