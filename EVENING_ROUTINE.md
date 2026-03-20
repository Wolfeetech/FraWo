# Evening Routine

## Goal

Close the day in a way that lets Codex, Gemini and the human operator resume tomorrow without re-discovering context.

## Daily Close Checklist

1. Run validation:
   - `make inventory-check`
   - `make ansible-ping`
   - `make qga-check`
   - `make business-drift-check`
   - `make backup-list`
   - `make backup-prune-dry-run`
2. Review current risks:
   - unresolved unknown devices in `NETWORK_INVENTORY.md`
   - EasyBox lease reconciliation still incomplete
   - PBS operating model still not live
   - retention for local proof backups must stay tidy until PBS takes over
   - legacy snapshot on `VM 100` remains intentionally untouched
   - Surface Go frontend node is still pre-rebuild until `SSH`, Tailscale and kiosk baseline are live
3. Update handoff files:
   - `SESSION_CLOSEOUT.md`
   - `MEMORY.md` if durable facts changed
   - `VM_AUDIT.md` if runtime state changed
4. Refresh live context:
   - `make refresh-context`
5. Leave the next-start path explicit:
   - first task tomorrow
   - blockers
   - exact commands to resume

## Morning Resume Checklist

1. Read `LIVE_CONTEXT.md`
2. Read `MORNING_ROUTINE.md`
3. Read `SECURITY_BASELINE.md`
4. Read `SESSION_CLOSEOUT.md`
5. Run:
   - `make start-day`
6. Resume the first unfinished priority from `SESSION_CLOSEOUT.md`

## Close Criteria

The day is considered cleanly closed when:

- current runtime state is verified
- no new scratch files exist
- next actions are explicit
- handoff is understandable without chat history
