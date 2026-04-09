#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "storage_optimization"
REPORT_JSON = ARTIFACT_DIR / "latest_report.json"
REPORT_MD = ARTIFACT_DIR / "latest_report.md"
ANKER = "root@100.69.179.87"
STOCK = "stock-pve"


def ssh(target: str, cmd: str, timeout: int = 60) -> str:
    result = subprocess.run(["ssh", target, cmd], capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"ssh failed: {target} {cmd}")
    return result.stdout.strip()


def gib(value: int) -> float:
    return value / (1024 ** 3)


def parse_size_listing(text: str) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for line in text.splitlines():
        parts = line.strip().split(maxsplit=1)
        if len(parts) != 2:
            continue
        try:
            rows.append((int(parts[0]), parts[1]))
        except ValueError:
            continue
    return rows


def keep_last_two_reclaim(rows: list[tuple[int, str]]) -> int:
    rows = sorted(rows, key=lambda item: item[1], reverse=True)
    if len(rows) <= 2:
        return 0
    return sum(size for size, _ in rows[2:])


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    anker_status = json.loads(ssh(ANKER, "pvesh get /nodes/proxmox-anker/status --output-format json"))
    anker_storage = json.loads(ssh(ANKER, "pvesh get /nodes/proxmox-anker/storage --output-format json"))
    anker_dump_bytes = int(ssh(ANKER, "du -sb /var/lib/vz/dump | cut -f1"))

    stock_storage = json.loads(ssh(STOCK, "pvesh get /nodes/pve/storage --output-format json"))
    stock_data_dirs_raw = ssh(STOCK, "du -x -B1 --max-depth=1 /mnt/data_family 2>/dev/null | sort -n")
    stock_library_dirs_raw = ssh(STOCK, "du -x -B1 --max-depth=1 /mnt/music_hdd/Library 2>/dev/null | sort -n | tail -15")
    inbox_bytes = int(ssh(STOCK, "du -s -B1 /mnt/music_hdd/Inbox 2>/dev/null | cut -f1 || echo 0"))
    library_bytes = int(ssh(STOCK, "du -s -B1 /mnt/music_hdd/Library 2>/dev/null | cut -f1 || echo 0"))
    yourparty_bytes = int(ssh(STOCK, "du -s -B1 /mnt/music_hdd/yourparty_Libary 2>/dev/null | cut -f1 || echo 0"))

    vm210_backups = parse_size_listing(
        ssh(STOCK, "find /mnt/data_family/proxmox_backups/dump -maxdepth 1 -name 'vzdump-qemu-210-*.vma.zst' -printf '%s %f\\n' | sort -nr")
    )
    vm360_backups = parse_size_listing(
        ssh(STOCK, "find /mnt/data_family/proxmox_backups/dump -maxdepth 1 -name 'vzdump-qemu-360-*.vma.zst' -printf '%s %f\\n' | sort -nr")
    )
    raw_images = parse_size_listing(
        ssh(STOCK, "find /mnt/data_family/proxmox_backups/images -type f -printf '%s %p\\n' 2>/dev/null | sort -nr")
    )

    vm210_reclaim = keep_last_two_reclaim(vm210_backups)
    vm360_reclaim = keep_last_two_reclaim(vm360_backups)
    raw_image_total = sum(size for size, _ in raw_images)

    anker_local = next((item for item in anker_storage if item.get("storage") == "local"), {})
    anker_local_lvm = next((item for item in anker_storage if item.get("storage") == "local-lvm"), {})
    stock_hdd_backup = next((item for item in stock_storage if item.get("storage") == "hdd-backup"), {})

    payload = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "anker": {
            "local_used_fraction": round(float(anker_local.get("used_fraction", 0)), 4),
            "local_lvm_used_fraction": round(float(anker_local_lvm.get("used_fraction", 0)), 4),
            "dump_bytes": anker_dump_bytes,
        },
        "stockenweiler": {
            "hdd_backup_used_fraction": round(float(stock_hdd_backup.get("used_fraction", 0)), 4),
            "music_library_bytes": library_bytes,
            "music_inbox_bytes": inbox_bytes,
            "yourparty_library_bytes": yourparty_bytes,
            "vm210_backup_count": len(vm210_backups),
            "vm360_backup_count": len(vm360_backups),
            "vm210_old_backup_reclaim_bytes": vm210_reclaim,
            "vm360_old_backup_reclaim_bytes": vm360_reclaim,
            "raw_image_archive_bytes": raw_image_total,
        },
        "recommendation_order": [
            "freeze_new_backup_load_on_stockenweiler",
            "prune_stockenweiler_vm210_and_vm360_backup_retention_after_verification",
            "classify_or_export_stockenweiler_raw_image_archives",
            "clean_stockenweiler_music_inbox_and_yourparty_side_payload",
            "restore_anker_pbs_before_any_broader_migration_or_backup_retargeting",
            "only_then_review_anker_local_dump_retention",
        ],
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines: list[str] = [
        "# Storage Optimization Audit",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Anker local dump: `{gib(anker_dump_bytes):.2f} GiB`",
        f"- Anker local usage: `{payload['anker']['local_used_fraction'] * 100:.1f}%` / local-lvm `{payload['anker']['local_lvm_used_fraction'] * 100:.1f}%`",
        f"- Stockenweiler hdd-backup usage: `{payload['stockenweiler']['hdd_backup_used_fraction'] * 100:.1f}%`",
        f"- Stockenweiler music library: `{gib(library_bytes):.2f} GiB`",
        f"- Stockenweiler yourparty library: `{gib(yourparty_bytes):.2f} GiB`",
        f"- Stockenweiler music inbox: `{gib(inbox_bytes):.2f} GiB`",
        "",
        "## Highest Pressure",
        "",
        f"- `stockenweiler` backup dataset is the first hard reclaim target: keep-last-2 on `VM 210` can free `{gib(vm210_reclaim):.2f} GiB`",
        f"- keep-last-2 on `VM 360` can free `{gib(vm360_reclaim):.2f} GiB`",
        f"- raw image archive review can free up to `{gib(raw_image_total):.2f} GiB` if verified obsolete or exported first",
        f"- `music_hdd` is the second hard pressure point: `Library` `{gib(library_bytes):.2f} GiB`, `yourparty_Libary` `{gib(yourparty_bytes):.2f} GiB`, `Inbox` `{gib(inbox_bytes):.2f} GiB`",
        "",
        "## Data Family Top Consumers",
        "",
    ]
    for line in stock_data_dirs_raw.splitlines()[-8:]:
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            lines.append(f"- `{parts[1]}` -> `{gib(int(parts[0])):.2f} GiB`")

    lines.extend([
        "",
        "## Library Top Consumers",
        "",
    ])
    for line in stock_library_dirs_raw.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            lines.append(f"- `{parts[1]}` -> `{gib(int(parts[0])):.2f} GiB`")

    lines.extend([
        "",
        "## Ordered Plan",
        "",
        "- Freeze new backup load on `stockenweiler` until reclaim is complete.",
        "- Keep only the last `2` verified dumps for `VM 210` and `VM 360`, but do not delete before the retained set is explicitly checked.",
        "- Review `proxmox_backups/images/*` as cold archive payload, not as invisible permanent storage.",
        "- Classify `music_hdd` into keep-local, migrate-to-Anker, or archive-offline; start with `Inbox` and `yourparty_Libary`, not the whole `Library` tree.",
        "- Restore a green PBS path on `Anker` before moving or retargeting more backup load.",
        "- Only after PBS is green: decide whether `Anker` local dump retention should be shortened or moved off root storage.",
        "",
        "## Guardrails",
        "",
        "- No blind deletes on `music_hdd`.",
        "- No backup-pruning without an explicit kept-set check.",
        "- No new Stockenweiler storage role before reclaim and PBS recovery.",
    ])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(REPORT_MD))


if __name__ == "__main__":
    main()
