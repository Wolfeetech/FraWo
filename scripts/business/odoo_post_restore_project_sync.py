"""Odoo shell sync for the 2026-04-22 post-restore project state.

Run inside the Odoo container, for example:

    /entrypoint.sh odoo shell -d FraWo_GbR < scripts/business/odoo_post_restore_project_sync.py

This script intentionally uses the `env` object provided by `odoo shell`.
It keeps the Odoo project SSOT aligned with the repo after the CT100 restore,
Caddy upstream fixes, and security/backups follow-up planning.
"""

from __future__ import annotations


TODAY = "2026-04-22"


def find_stage(label: str):
    Stage = env["project.task.type"].sudo()
    candidates = Stage.search([], order="sequence,id")
    label_lower = label.lower()
    for stage in candidates:
        if label_lower in (stage.name or "").lower():
            return stage
    aliases = {
        "backlog": ["backlog", "inbox", "neu"],
        "planning": ["planung", "today", "this week"],
        "active": ["in arbeit", "automatisierung", "today"],
        "blocked": ["blockiert", "later"],
        "done": ["erledigt", "done"],
    }
    for needle in aliases.get(label, []):
        for stage in candidates:
            if needle in (stage.name or "").lower():
                return stage
    return candidates[:1]


def project_by_name(name: str, description: str = ""):
    Project = env["project.project"].sudo()
    project = Project.search([("name", "=", name)], limit=1)
    if not project:
        project = Project.create({"name": name, "description": description})
        print(f"created project: {name}")
    elif description and (project.description or "").strip() != description.strip():
        project.write({"description": description})
        print(f"updated project description: {name}")
    return project


def upsert_task(project, name: str, stage_key: str, description: str):
    Task = env["project.task"].sudo()
    task = Task.search([("project_id", "=", project.id), ("name", "=", name)], limit=1)
    stage = find_stage(stage_key)
    payload = {
        "project_id": project.id,
        "name": name,
        "description": description,
    }
    if stage:
        payload["stage_id"] = stage.id
    if task:
        task.write(payload)
        print(f"updated task: {project.name} / {name}")
    else:
        Task.create(payload)
        print(f"created task: {project.name} / {name}")


master = project_by_name(
    "🚀 Homeserver 2027: Masterplan",
    (
        "<p><strong>SSOT update 2026-04-22:</strong> CT100 restored, Caddy frontdoors green, "
        "security/backups/DNS/storage follow-ups tracked after restore.</p>"
    ),
)
lane_b = project_by_name(
    "Lane B: Website & Public Edge",
    "<p>Public HTTPS edge for frawo-tech.de; internal apps remain Tailscale-only.</p>",
)
lane_c = project_by_name(
    "Lane C: Security & PBS",
    "<p>Security, backup proof, DNS and storage sustainability after CT100 restore.</p>",
)
lane_e = project_by_name(
    "Lane E: Radio & Media",
    "<p>Jellyfin/media operations and future radio backend recovery.</p>",
)

runtime_status = (
    "<ul>"
    "<li>portal.hs27.internal -> HTTP 200</li>"
    "<li>odoo.hs27.internal -> HTTP 200</li>"
    "<li>vault.hs27.internal -> HTTP 200</li>"
    "<li>ha.hs27.internal -> HTTP 200</li>"
    "<li>cloud.hs27.internal -> HTTP 302 login/HTTPS redirect</li>"
    "<li>paperless.hs27.internal -> HTTP 302 login redirect</li>"
    "<li>media.hs27.internal -> HTTP 302 Jellyfin login redirect</li>"
    "<li>Root disk about 19% used; ssd2tb about 4% used; gdrive about 22% used</li>"
    "</ul>"
)

upsert_task(
    master,
    "Post-Restore Service Reachability 2026-04-22",
    "done",
    f"<p>Verified after CT100 restore and Caddy rebuild on {TODAY}.</p>{runtime_status}",
)
upsert_task(
    master,
    "Security Audit: VM Firewall Reapply",
    "blocked",
    (
        "<p>VM210 and VM220 are service-safe with net0 firewall=0. A first re-enable attempt "
        "blocked CT100 -> Odoo/HA traffic, so reapply needs packet-level validation before production.</p>"
    ),
)
upsert_task(
    master,
    "Backup Proof: Post-restore backup and rclone fallback",
    "planning",
    (
        "<p>Run a fresh backup proof after Caddy/firewall changes. rclone mount is active but Google API "
        "quota/rate limits were observed during backup traffic; add throttling or ssd2tb fallback.</p>"
    ),
)
upsert_task(
    master,
    "DNS Finalization: hs27.internal without hosts-file workaround",
    "blocked",
    (
        "<p>Move Windows clients from hosts-file workaround to UniFi/Tailscale split-DNS. Verify portal, "
        "odoo, cloud, vault, ha, paperless and media names after change.</p>"
    ),
)
upsert_task(
    master,
    "CT100 Storage Migration to ssd2tb",
    "planning",
    "<p>Prepare a maintenance-window migration of CT100 disk to ssd2tb after a fresh backup proof.</p>",
)
upsert_task(
    master,
    "Odoo App Layer: res.users.log ACL warning",
    "backlog",
    "<p>Investigate Odoo ACL warnings at app layer after infrastructure is stable.</p>",
)

upsert_task(
    lane_b,
    "Public HTTPS Edge Baseline",
    "blocked",
    (
        "<p>www.frawo-tech.de public HTTPS remains blocked by public edge/TLS path. Keep only website public; "
        "no internal apps are in public scope.</p>"
    ),
)
upsert_task(
    lane_c,
    "PVE Host Exposure Audit: NFS/RPC/SSH",
    "active",
    "<p>Review host listeners. NFS/RPC are currently observed on all interfaces and need restriction review.</p>",
)
upsert_task(
    lane_c,
    "VM210/VM220 Firewall Hardening Reapply",
    "blocked",
    (
        "<p>Design tested Proxmox firewall rules. Done only when VM firewall=1 and Caddy frontdoors still "
        "return HTTP 200 for Odoo and HA.</p>"
    ),
)
upsert_task(
    lane_c,
    "Backup Watchdog: rclone quota and ssd2tb fallback",
    "planning",
    "<p>Add rclone watchdog/rate-limit and local fallback path before the next large nightly backup run.</p>",
)
upsert_task(
    lane_c,
    "CT100 Disk Migration",
    "planning",
    "<p>Migrate toolbox disk to ssd2tb in a controlled window after fresh backup proof.</p>",
)
upsert_task(
    lane_e,
    "Jellyfin Media Frontdoor Verified",
    "done",
    "<p>media.hs27.internal routes to Jellyfin on 10.1.0.20:8096 and returns the expected login redirect.</p>",
)
upsert_task(
    lane_e,
    "Radio Frontdoor Backend",
    "blocked",
    "<p>radio.hs27.internal is not a verified product path yet; restore or redeploy a backend before enabling.</p>",
)

env.cr.commit()
print("odoo_post_restore_project_sync complete")
