# CI/CD Delivery Factory Preflight

- Generated at: `2026-04-04T01:55:32+02:00`
- Git origin: `https://github.com/Wolfeetech/FraWo.git`
- Existing workflow files: `3`
- Dockerfiles/Containerfiles: `1`
- Stack compose templates: `6`
- Factory-ready apps now: `1` / `10`

## Verified Facts

- Git remote is configured: `https://github.com/Wolfeetech/FraWo.git`.
- Current repo host is GitHub, so a thin GitHub Actions wrapper is a factual option.
- Anker DMZ target subnets are already canonical in UCG_NETWORK_ARCHITECTURE.md: VLAN 102 `10.2.0.0/24`, VLAN 103 `10.3.0.0/24`.
- Repo already contains `6` stack compose templates, but they are runtime templates, not standalone OCI app definitions.
- GHCR registry contract and env/secret contract docs now exist for the first reference app.
- A neutral compose deploy bundle now exists for the first reference app.
- Coolify host selection contract now exists and keeps the controller out of the DMZ and off the hypervisor host itself.
- Repo now contains `1` verified Dockerfile/Containerfile artifact for factory build work.
- App catalog now contains `1` factory-deploy-ready reference app candidate.

## Rejected Assumptions


## Open Prerequisites

- OCI registry is still undecided.
- Coolify management host is still undecided.
- Stockenweiler secondary DMZ subnet and runtime node are not yet fixed facts.
- Prod secret distribution model for dev/prod is not yet encoded in the repo.

## Safe Scope Now

- Repo-side factory scaffolding is in scope now.
- A thin GitHub Actions validation workflow is in scope because GitHub origin is verified.
- Actual Coolify deployment, registry setup, DMZ node provisioning, and public cutover remain gated infra and are not in scope now.

