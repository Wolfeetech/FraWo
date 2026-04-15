# Odoo Database Backup Report - WolfStudioPC

**Timestamp:** 2026-04-15 22:24
**Device:** WOLFSTUDIOPC

## Backup Summary
Database backups for the FraWo project were successfully completed. Since the database `odoo` was not found, both identified project databases were backed up to ensure data integrity.

### Databases Backed Up
1.  **FraWo_Live** (~8.3 MB)
2.  **FraWo_Live_V2** (~11 MB)

## Storage Location (NFS)
The files were transferred from VM 220 to the centralized NFS storage on Anker.

**Path:** `/mnt/hs27-media/backups/odoo/`

```text
-rw-r--r-- 1 root root 8.3M Apr 15 20:20 FraWo_Live_20260415_2218.sql
-rw-r--r-- 1 root root  11M Apr 15 20:22 FraWo_Live_V2_20260415_2218.sql
```

## Technical Details
- **Method:** `pg_dump` via Proxmox Guest Agent inside Docker container.
- **Transport:** Chunk-based extraction using a custom Python script on Anker to bypass QGA JSON/base64 size limitations.
- **Retention:** Per your instructions, the temporary files in VM 220's `/tmp` directory have been **KEPT**.

## Odoo Log Status
Due to binary multiplexing in Docker's log driver, the captured logs contained binary artifacts. However, the backup process completed without errors.

## Next Step
Backups are safe on NFS. Please let me know if you need any further investigation into the login issues mentioned.
