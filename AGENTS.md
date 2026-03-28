# Agent Collaboration Rules

This workspace is designed for shared operation between Codex, Gemini and human operators.

## Shared Truth

- `AI_BOOTSTRAP_CONTEXT.md` is the read-first AI bootstrap file.
- `LIVE_CONTEXT.md` is the first-stop handoff file.
- `MEMORY.md` is the durable knowledge base.
- `NETWORK_INVENTORY.md` is the network source of truth.
- `VM_AUDIT.md` is the verified runtime and remediation record.
- `ansible/inventory/hosts.yml` is the machine-readable estate inventory.
- `ansible/inventory/group_vars/all/vault.yml` is the only allowed in-repo secrets file and must stay encrypted.

## Required Behavior

1. Read `AI_BOOTSTRAP_CONTEXT.md` and `LIVE_CONTEXT.md` before making decisions.
2. Read `SESSION_CLOSEOUT.md` when resuming after a pause or the next day.
3. Update the canonical file instead of creating duplicate notes.
4. After meaningful changes, refresh the live context:
   - automatic path unit should do it
   - fallback: run `make refresh-context`
5. Do not store plaintext credentials in markdown or ad hoc notes.
6. Keep the workspace clean. No throwaway files unless explicitly needed.
7. If progress is blocked by a manual, physical or account-bound dependency, state it explicitly with the prefix `AKTION VON DIR ERFORDERLICH:`.
8. Mirror open operator dependencies in `MEMORY.md` under `## Aktive Operator-Aktionen`.

## Change Discipline

- Use `MEMORY.md` for long-lived facts and project direction.
- Use `NETWORK_INVENTORY.md` when device state, IPs, zones or ownership change.
- Use `VM_AUDIT.md` when runtime validation or remediation changes.
- Keep `GEMINI.md` aligned with the current collaboration contract for Gemini.
