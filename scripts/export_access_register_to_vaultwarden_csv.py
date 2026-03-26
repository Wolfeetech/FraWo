#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


CSV_HEADERS = [
    "folder",
    "favorite",
    "type",
    "name",
    "notes",
    "fields",
    "reprompt",
    "login_uri",
    "login_username",
    "login_password",
    "login_totp",
]

SECTION_LABELS = {
    "## Aktuelle Admin- und Bootstrap-Logins": "Admin and bootstrap logins",
    "## Personenbasierte Konten live": "Named user logins",
}

FOLDER_RULES = (
    ("nextcloud", "Business Apps"),
    ("paperless", "Business Apps"),
    ("odoo", "Business Apps"),
    ("home assistant", "Core Infra"),
    ("adguard", "Core Infra"),
    ("jellyfin", "Media"),
    ("azuracast", "Media"),
    ("strato", "Mail & Domains"),
)


@dataclass
class OrganizationModel:
    organization_name: str = "FraWo"
    organization_legal_name: str = "FraWo GbR"
    organization_purpose: str = ""
    collections: list[str] = field(default_factory=list)
    sites: dict[str, str] = field(default_factory=dict)
    default_sites: list[str] = field(default_factory=lambda: ["Anker"])
    service_rules: list[dict[str, object]] = field(default_factory=list)


@dataclass
class VaultItem:
    folder: str
    favorite: str
    item_type: str
    name: str
    notes: str
    fields: str
    reprompt: str
    login_uri: str
    login_username: str
    login_password: str
    login_totp: str
    organization_name: str
    sites: list[str]
    aliases: list[str] = field(default_factory=list)

    def as_csv_row(self) -> list[str]:
        alias_note = ""
        if self.aliases:
            alias_note = "\nAlso listed as: " + ", ".join(self.aliases)
        site_note = ""
        if self.sites:
            site_note = "\nSite scope: " + ", ".join(self.sites)
        org_note = ""
        if self.organization_name:
            org_note = f"\nOrganization: {self.organization_name}"
        return [
            self.folder,
            self.favorite,
            self.item_type,
            self.name,
            self.notes + org_note + site_note + alias_note,
            self.fields,
            self.reprompt,
            self.login_uri,
            self.login_username,
            self.login_password,
            self.login_totp,
        ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export login rows from ACCESS_REGISTER.md into a Bitwarden/Vaultwarden "
            "compatible CSV outside the repo."
        )
    )
    parser.add_argument(
        "--access-register",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "ACCESS_REGISTER.md",
        help="Path to ACCESS_REGISTER.md",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output CSV path. Defaults to a timestamped file in a local app-data directory.",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "manifests" / "vaultwarden" / "organization_model.json",
        help="Path to the Vaultwarden organization model JSON.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and summarize items without writing a CSV file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )
    parser.add_argument(
        "--split-by-collection",
        action="store_true",
        help="Write one CSV per resolved collection instead of a single combined CSV.",
    )
    parser.add_argument(
        "--site",
        help="Only export items that match the given site scope, for example Anker, Villa or Stockenweiler.",
    )
    return parser.parse_args()


def default_output_path() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        base = Path(local_appdata) / "Homeserver2027" / "vaultwarden_imports"
    else:
        base = Path.home() / ".local" / "share" / "Homeserver2027" / "vaultwarden_imports"
    return base / f"access_register_vaultwarden_import_{timestamp}.csv"


def default_split_output_dir() -> Path:
    return default_output_path().with_suffix("")


def clean_markdown_cell(value: str) -> str:
    value = value.strip()
    value = value.strip("`")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_url(url: str) -> str:
    url = clean_markdown_cell(url)
    if not url:
        return url
    # Some markdown cells include a URL-like token followed by a location note.
    # Vaultwarden needs only the actual login URI.
    candidate = url.split()[0].rstrip("`")
    if re.match(r"^[a-z]+://", candidate):
        return candidate
    return f"http://{candidate}"


def resolve_folder(service_name: str) -> str:
    service_name = service_name.lower()
    for needle, folder in FOLDER_RULES:
        if needle in service_name:
            return folder
    return "Imported"


def load_organization_model(model_path: Path) -> OrganizationModel:
    if not model_path.exists():
        return OrganizationModel()
    data = json.loads(model_path.read_text(encoding="utf-8"))
    return OrganizationModel(
        organization_name=data.get("organization_name", "FraWo"),
        organization_legal_name=data.get("organization_legal_name", "FraWo GbR"),
        organization_purpose=data.get("organization_purpose", ""),
        collections=data.get("collections", []),
        sites=data.get("sites", {}),
        default_sites=data.get("default_sites", ["Anker"]),
        service_rules=data.get("service_rules", []),
    )


def resolve_rule(service_name: str, model: OrganizationModel) -> dict[str, object] | None:
    lowered = service_name.lower()
    for rule in model.service_rules:
        match = str(rule.get("match", ""))
        match_type = str(rule.get("match_type", "contains"))
        match_lowered = match.lower()
        if match_type == "exact" and lowered == match_lowered:
            return rule
        if match_type == "contains" and match_lowered in lowered:
            return rule
        if match_type == "regex" and re.search(match, service_name):
            return rule
    return None


def resolve_collection_and_sites(service_name: str, model: OrganizationModel) -> tuple[str, list[str]]:
    rule = resolve_rule(service_name, model)
    if rule:
        collection = str(rule.get("collection", resolve_folder(service_name)))
        sites = [str(site) for site in rule.get("sites", model.default_sites)]
        return collection, sites
    return resolve_folder(service_name), list(model.default_sites)


def resolve_item_name(service_name: str, username: str) -> str:
    lowered = service_name.lower()
    if lowered.endswith(" admin"):
        return service_name
    if username.lower() in {"root", "admin", "frawoadmin"}:
        return f"{service_name} ({username})"
    return f"{service_name} - {username}"


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def parse_access_register(
    markdown_path: Path,
    model: OrganizationModel,
    site_filter: str | None,
) -> tuple[list[VaultItem], int]:
    text = markdown_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    active_section = ""
    items_by_key: dict[tuple[str, str, str], VaultItem] = {}
    duplicate_count = 0
    normalized_site_filter = site_filter.lower() if site_filter else None

    for line in lines:
        if line.startswith("## "):
            active_section = line.strip()
            continue

        if active_section not in SECTION_LABELS:
            continue
        if not line.startswith("|"):
            continue

        raw_cells = [cell.strip() for cell in line.split("|")[1:-1]]
        cells = [clean_markdown_cell(cell) for cell in raw_cells]
        if not cells or cells[0] == "Service" or is_separator_row(cells):
            continue
        if len(cells) < 5:
            continue

        service_name, login_uri, username, password, state = cells[:5]
        if not username or not password:
            continue
        collection, sites = resolve_collection_and_sites(service_name, model)
        if normalized_site_filter and normalized_site_filter not in {site.lower() for site in sites}:
            continue

        item = VaultItem(
            folder=collection,
            favorite="",
            item_type="login",
            name=resolve_item_name(service_name, username),
            notes=(
                f"Imported from ACCESS_REGISTER.md ({SECTION_LABELS[active_section]}). "
                f"Original status: {state}."
            ),
            fields="",
            reprompt="0",
            login_uri=normalize_url(login_uri),
            login_username=username,
            login_password=password,
            login_totp="",
            organization_name=model.organization_name,
            sites=sites,
        )
        key = (item.login_uri, item.login_username, item.login_password)
        existing = items_by_key.get(key)
        if existing:
            duplicate_count += 1
            if service_name not in existing.aliases and service_name != existing.name:
                existing.aliases.append(service_name)
            continue
        items_by_key[key] = item

    items = sorted(items_by_key.values(), key=lambda item: (item.folder, item.name.lower()))
    return items, duplicate_count


def write_csv(output_path: Path, items: list[VaultItem], force: bool) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not force:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use --force to overwrite."
        )

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADERS)
        for item in items:
            writer.writerow(item.as_csv_row())


def write_split_csv(output_dir: Path, items: list[VaultItem], force: bool) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written_paths: list[Path] = []
    grouped: dict[str, list[VaultItem]] = {}
    for item in items:
        grouped.setdefault(item.folder, []).append(item)

    for collection_name, collection_items in grouped.items():
        safe_name = re.sub(r"[^a-z0-9]+", "_", collection_name.lower()).strip("_")
        output_path = output_dir / f"{safe_name}.csv"
        write_csv(output_path, collection_items, force)
        written_paths.append(output_path)
    return sorted(written_paths)


def print_summary(
    items: list[VaultItem],
    duplicate_count: int,
    model: OrganizationModel,
    output_path: Path | None,
    site_filter: str | None,
    split_paths: list[Path] | None = None,
) -> None:
    print(f"organization_name={model.organization_name}")
    print(f"items_ready={len(items)}")
    print(f"duplicates_skipped={duplicate_count}")
    if site_filter:
        print(f"site_filter={site_filter}")
    folders: dict[str, int] = {}
    sites: dict[str, int] = {}
    for item in items:
        folders[item.folder] = folders.get(item.folder, 0) + 1
        for site in item.sites:
            sites[site] = sites.get(site, 0) + 1
    for folder_name in sorted(folders):
        normalized = re.sub(r"[^a-z0-9]+", "_", folder_name.lower()).strip("_")
        print(f"collection_{normalized}={folders[folder_name]}")
    for site_name in sorted(sites):
        normalized = re.sub(r"[^a-z0-9]+", "_", site_name.lower()).strip("_")
        print(f"site_{normalized}={sites[site_name]}")
    if output_path:
        print(f"output_path={output_path}")
        print("next_step=import_csv_into_vaultwarden_and_delete_local_csv_after_success")
    if split_paths:
        print(f"output_dir={split_paths[0].parent}")
        for path in split_paths:
            print(f"collection_file={path}")
        print("next_step=import_each_collection_csv_into_the_matching_frawo_collection_and_delete_local_csvs_after_success")


def main() -> int:
    args = parse_args()
    access_register = args.access_register.resolve()
    if not access_register.exists():
        print(f"ACCESS_REGISTER.md not found: {access_register}", file=sys.stderr)
        return 1

    model = load_organization_model(args.model.resolve())
    items, duplicate_count = parse_access_register(access_register, model, args.site)
    output_path = args.output.resolve() if args.output else default_output_path()

    if args.dry_run:
        print_summary(items, duplicate_count, model, None, args.site)
        return 0

    if args.split_by_collection:
        output_dir = args.output.resolve() if args.output else default_split_output_dir()
        try:
            split_paths = write_split_csv(output_dir, items, args.force)
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print_summary(items, duplicate_count, model, None, args.site, split_paths)
        return 0

    try:
        write_csv(output_path, items, args.force)
    except FileExistsError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print_summary(items, duplicate_count, model, output_path, args.site)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
