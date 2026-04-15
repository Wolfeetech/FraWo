# SSOT Collaboration Contract: Homeserver 2027

## Goal / Zielbild
This contract defines the absolute Single Source of Truth (SSOT) for the Homeserver 2027 project. The primary objective is to eliminate "Split-Brain" scenarios and ensure a "completely clean" state where only the **FraWo** Master Repository exists locally and online.

## Core Rules

### 1. Unified Truth (Zuständige Wahrheit)
- **Infrastructure Facts**: Must be documented in `NETWORK_INVENTORY.md` and `VM_AUDIT.md`.
- **Durable Knowledge**: Must be stored in `MEMORY.md`.
- **Operational Handoff**: Must be maintained in `LIVE_CONTEXT.md`.
- **Secrets**: Solely located in `ansible/inventory/group_vars/all/vault.yml`.

### 2. Legacy Intake Protocol (Altbestand-Intake)
No legacy data or repository shall be deleted until the following "Zero-Loss" protocol is completed:
1. **Capture**: Source is listed in `REPO_CONSOLIDATION_REGISTER.md`.
2. **Triage**: Knowledge is extracted and mapped to canonical files.
3. **Preservation**: Failed missions and lessons are saved in `FAILURE_LESSONS_LOG.md`.
4. **Marking**: Repository is marked `delete_allowed=yes`.

### 3. Anti-Duplicate Rule
Duplicate notes or secondary "documentation repositories" are strictly prohibited. Information must be merged into the canonical files or discarded.

## Definition of Done (DoH) for Consolidation
A repository is considered consolidated when:
- [x] All unique technical configurations are in `FraWo`.
- [x] All project history/lessons are in the `FAILURE_LESSONS_LOG.md`.
- [x] The local and remote copies are removed, leaving only the Master `FraWo` SSOT.

## Conflicts
In case of discrepancy, **Runtime Reality** (verified state on the server nodes) takes precedence over legacy documentation or unverified Altbestände.
