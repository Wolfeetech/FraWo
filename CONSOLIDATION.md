# Repository Consolidation Notes - 2026-04-15

## Overview
The `wolfeetech/` ecosystem has been consolidated into the `FraWo` repository to establish a Single Source of Truth (SSOT). This migration uses Git Subtrees to maintain source history while centralizing management.

## Consolidated Projects

| App Name | Subtree Path | Source Repository |
| --- | --- | --- |
| **yourparty** | `apps/yourparty/` | `https://github.com/wolfeetech/yourparty-tech` |
| **fayanet** | `apps/fayanet/` | `https://github.com/wolfeetech/FaYa-Net` |

## Migration Details
- **Mechanism**: Git Subtree
- **Consolidation Date**: 2026-04-15
- **Milestone Tag**: `v2026-04-15-consolidated`

## Synced Components
- **Identity Standard**: Consolidated in `DOCS/Task_Archive/IDENTITY_STANDARD.md`.
- **Infrastructure Docs**: Centralized in root and `DOCS/`.
- **Scripts**: Maintenance scripts moved to `scripts/`.

## Archived Repositories
The following repositories are now archived on GitHub:
- `yourparty-tech` (moved to `apps/yourparty`)
- `FaYa-Net` (moved to `apps/fayanet`)
- `AzuraCast` (obsolete, use official upstream instead)

## Automation
Updates can be pulled using:
```bash
./scripts/sync-subtrees.sh
```
