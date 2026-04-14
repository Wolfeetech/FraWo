# FAILURE LESSONS LOG

This document preserves wisdom from "failed missions", abandoned experiments, and legacy configurations to ensure that mistakes are not repeated and valuable edge-case knowledge is retained.

## Logged Lessons

### Entry 01: Legacy Network Bridge Conflict
- **Source**: `Anker-Legacy-Bridge` / `192.168.2.10`
- **What happened**: Concurrent gateways (EasyBox and UCG-Ultra) caused internet routing loops and unreachable admin interfaces.
- **The Lesson**: Do not mix L3 gateways on a flat L2 segment. The migration must use clear VLAN boundaries (VLAN 101) or explicit routing priorities.
- **Consolidated To**: `VM_AUDIT.md` (Remediation section).

### Entry 02: Odoo Version Drift
- **Source**: `Odoo 17 Docker Migration`
- **What happened**: Attempting to restore Odoo 16 volumes into an Odoo 17 image without database migration scripts resulted in crashed containers.
- **The Lesson**: Version-pin Docker images in the `docker-compose.yml` file and always verify the database schema version before upgrading the image.
- **Consolidated To**: `VM_AUDIT.md`.

### Entry 03: Radio Monorepo Over-Complexity (yourparty-tech)
- **Source**: `Wolfeetech/yourparty-tech`
- **What happened**: Maintaining a split monorepo with FastAPI and WordPress in a single lifecycle proved brittle for radio station metadata sync.
- **The Lesson**: Decouple the metadata harvester (Live data) from the CMS (Web presence). Use the dedicated `AzuraCast` stack for automation rather than custom-built monorepos for baseline FM/Web operations.
- **Consolidated To**: `MEMORY.md` (Radio Architecture section).

### Entry 04: "Network God" Scope Creep (FaYa-Net)
- **Source**: `Wolfeetech/FaYa-Net`
- **What happened**: Focusing on broad "Network God" infra-experiments diverted resources from core business uptime.
- **The Lesson**: Professional infra must follow a "Service-First" approach. Networking serves the Applications (Odoo, Nextcloud), not vice versa. All NetOps must now be integrated directly into the `FraWo` Master repo as IaC (Ansible/Caddy).

---
*Note: Every consolidated repository with "failed" components must log at least one entry here before deletion.*
