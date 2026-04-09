#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from export_access_register_to_vaultwarden_csv import (
    OrganizationModel,
    VaultItem,
    load_organization_model,
    parse_access_register,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a password-free Vaultwarden reference register from ACCESS_REGISTER.md."
        )
    )
    parser.add_argument(
        "--access-register",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "ACCESS_REGISTER.md",
        help="Path to ACCESS_REGISTER.md",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "manifests"
        / "vaultwarden"
        / "organization_model.json",
        help="Path to the Vaultwarden organization model JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md",
        help="Where to write the generated password-free markdown register.",
    )
    parser.add_argument(
        "--site",
        help="Only include entries matching the given site scope.",
    )
    return parser.parse_args()


def summarize_collections(items: list[VaultItem]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item.folder] = counts.get(item.folder, 0) + 1
    return dict(sorted(counts.items()))


def summarize_sites(items: list[VaultItem]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        for site in item.sites:
            counts[site] = counts.get(site, 0) + 1
    return dict(sorted(counts.items()))


def render_summary_list(lines: list[str], title: str, values: dict[str, int]) -> None:
    lines.append(f"## {title}")
    lines.append("")
    if not values:
        lines.append("- keine Eintraege")
        lines.append("")
        return
    for key, count in values.items():
        lines.append(f"- `{key}`: `{count}`")
    lines.append("")


def render_items_for_collection(
    lines: list[str],
    collection_name: str,
    items: list[VaultItem],
    model: OrganizationModel,
) -> None:
    lines.append(f"## {collection_name}")
    lines.append("")
    lines.append(
        "| Vault Item | Benutzer | URL | Standort | Vaultwarden-Referenz | Herkunft |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for item in items:
        sites = ", ".join(item.sites) if item.sites else "-"
        reference = f"{model.organization_name} / {item.folder} / {item.name}"
        source = item.notes.replace("\n", " ")
        if item.aliases:
            source = f"{source} Also listed as: {', '.join(item.aliases)}."
        lines.append(
            f"| `{item.name}` | `{item.login_username}` | `{item.login_uri}` | "
            f"`{sites}` | `{reference}` | {source} |"
        )
    lines.append("")


def build_markdown(
    items: list[VaultItem],
    duplicate_count: int,
    model: OrganizationModel,
    access_register_path: Path,
    site_filter: str | None,
) -> str:
    lines: list[str] = []
    lines.append("# Vaultwarden Reference Register")
    lines.append("")
    lines.append(f"Stand: `{date.today().isoformat()}`")
    lines.append("")
    lines.append(
        "Diese Datei ist der passwortfreie Referenzauszug nach dem Vaultwarden-Import."
    )
    lines.append(
        "Sie ersetzt keine Vaultwarden-Eintraege und ist nur fuer Betrieb, Audit und "
        "Markdown-Bereinigung gedacht."
    )
    lines.append("")
    lines.append("## Quelle")
    lines.append("")
    lines.append(f"- generiert aus `{access_register_path.name}`")
    lines.append(f"- Organisation: `{model.organization_name}`")
    if site_filter:
        lines.append(f"- Standortfilter: `{site_filter}`")
    lines.append(f"- importierbare Eintraege: `{len(items)}`")
    lines.append(f"- zusammengefuehrte Duplikate: `{duplicate_count}`")
    lines.append("")

    render_summary_list(lines, "Collection Summary", summarize_collections(items))
    render_summary_list(lines, "Site Summary", summarize_sites(items))

    grouped: dict[str, list[VaultItem]] = {}
    for item in items:
        grouped.setdefault(item.folder, []).append(item)

    for collection_name in sorted(grouped):
        render_items_for_collection(lines, collection_name, grouped[collection_name], model)

    lines.append("## Betriebsregel")
    lines.append("")
    lines.append(
        "- Klartext-Passwoerter gehoeren nach erfolgreicher Vaultwarden-Verifikation "
        "nicht mehr in Arbeitsdateien."
    )
    lines.append(
        "- Diese Referenzdatei darf bleiben, solange sie keine Passwoerter enthaelt "
        "und bei Aenderungen neu generiert wird."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    access_register = args.access_register.resolve()
    if not access_register.exists():
        raise SystemExit(f"ACCESS_REGISTER.md not found: {access_register}")

    model = load_organization_model(args.model.resolve())
    items, duplicate_count = parse_access_register(access_register, model, args.site)
    markdown = build_markdown(items, duplicate_count, model, access_register, args.site)

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"output_path={output_path}")
    print(f"items_ready={len(items)}")
    print(f"duplicates_skipped={duplicate_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
