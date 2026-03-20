# Morning Routine

## Goal

Start the day with one repeatable control path that verifies runtime health, security baseline and the next execution order before any new change is made.

## Start Sequence

1. Read:
   - `LIVE_CONTEXT.md`
   - `MORNING_ROUTINE.md`
   - `SESSION_CLOSEOUT.md`
2. Run the operational start routine:
   - `make start-day`
3. Review the generated status:
   - runtime health
   - security baseline
   - current blockers
4. Only then begin the first change of the day.

## What `make start-day` Verifies

1. Inventory and reachability:
   - `make inventory-check`
   - `make ansible-ping`
2. Runtime health:
   - `make qga-check`
   - `make business-drift-check`
   - `make toolbox-network-check`
   - `make backup-list`
   - `make proxmox-local-backup-check`
3. Network and rollout gates:
   - `make toolbox-tailscale-check`
   - `make pbs-stage-gate`
   - `make haos-stage-gate`
   - `make surface-go-check`
4. Security baseline:
   - `make security-baseline-check`
5. Shared handoff refresh:
   - `make refresh-context`

## Remote-Only Mode

Wenn der Arbeitstag ueber `AnyDesk` auf dem `ZenBook` laeuft und keine physischen Schritte moeglich sind:

1. zusaetzlich `make zenbook-remote-check` ausfuehren
2. danach `make remote-only-check`
3. fuer die Reihenfolge und Stop-Conditions dann `REMOTE_ONLY_WORK_WINDOW.md` verwenden

## Current Execution Order

Use this order unless a morning check comes back red:

1. Finish the `toolbox` Tailnet join and route approval for `192.168.2.0/24`.
   Use `make toolbox-tailscale-join-assist` when you are ready to complete the interactive Tailnet login.
2. Reconcile the Easy Box lease view against `NETWORK_INVENTORY.md`, starting with `make easybox-browser-probe` as the non-destructive router reachability check.
3. Keep AdGuard Home in opt-in mode and only roll pilot clients after Tailnet is stable.
4. Turn the PBS path from prepared to build-ready by adding separate backup storage; the installer ISO is already staged on Proxmox.
5. Prepare the Surface Go clean rebuild path so the shared frontend node can move from unmanaged discovery to managed baseline.

## Stop Conditions

Do not continue into new implementation work when one of these is true:

- `make ansible-ping` is red
- `make business-drift-check` is red
- `make proxmox-local-backup-check` is red
- `make security-baseline-check` reports unexpected secrets or unexpected ports
- `make haos-stage-gate` is red and the planned task is HAOS-related

## Daily Security Focus

The morning routine is intentionally opinionated:

- verify that no plaintext secrets are present outside Vault
- verify that business services expose only their intended app ports
- verify that local backup protection is still alive
- verify that public exposure remains disabled
- verify that Tailscale, PBS and HAOS gates are still in the expected state
