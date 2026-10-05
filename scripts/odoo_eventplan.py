from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import html
import http.client
import ipaddress
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
import xmlrpc.client
import zlib
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlsplit

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "deployments/frawotech-web/templates"
TEMPLATES = (
    "01_dmx_signalplan.drawio",
    "02_audio_signalfluss.drawio",
    "03_event_strom_und_netzwerk.drawio",
    "04_buehne_und_raumplan.drawio",
)
DEVICE_TARGETS = (
    (r"\bmoving\s*head\b", "dmx_plan", "mh1"),
    (r"\b(?:led\s*par|par\s*led)\b", "dmx_plan", "par1"),
    (r"\bhazer\b", "dmx_plan", "haz"),
    (r"\bwolfmix\b", "dmx_plan", "ctrl"),
    (r"\bdmx\s*(?:splitter|booster)\b", "dmx_plan", "spl"),
    (r"\b(?:cx2|lautsprecher.top|topteil)\b", "audio_routing", "spk_top_l"),
    (r"\b(?:subwoofer|subbass)\b", "audio_routing", "spk_subs"),
    (r"\bmischpult\b", "audio_routing", "foh_mixer"),
    (r"\b(?:funkmikrofon|funkstrecke)\b", "audio_routing", "in_mic"),
    (r"\b(?:dsp|dxo.26)\b", "audio_routing", "dsp"),
    (r"\bendstufe\b", "audio_routing", "amp_tops"),
    (r"\bcee.verteil", "power_network", "pwr_dist"),
    (r"\b(?:poe.*switch|switch.*poe)\b", "power_network", "net_sw"),
    (r"\baccess\s*point\b", "power_network", "net_ap"),
    (r"\b(?:router|gateway)\b", "power_network", "net_gw"),
)


class DescriptionText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_endtag(self, tag):
        if tag in {"p", "div", "li", "tr", "h3"}:
            self.parts.append("\n")

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.parts.append("\n")


class RpcTransport(xmlrpc.client.Transport):
    def __init__(self, secure):
        super().__init__()
        self.secure = secure

    def make_connection(self, host):
        if self._connection and self._connection[0] == host:
            return self._connection[1]
        connection_type = http.client.HTTPSConnection if self.secure else http.client.HTTPConnection
        self._connection = (host, connection_type(host, timeout=20))
        return self._connection[1]


class OdooRpc:
    def __init__(self):
        endpoint = os.environ.get("ODOO_RPC_URL", "http://10.1.0.112:8069").rstrip("/")
        parsed = urlsplit(endpoint)
        if parsed.scheme not in {"https", "http"} or not parsed.hostname or parsed.username or parsed.query or parsed.fragment:
            raise ValueError("Ungültige Odoo-URL")
        if parsed.scheme == "http":
            try:
                private = ipaddress.ip_address(parsed.hostname).is_private
            except ValueError:
                private = parsed.hostname == "localhost"
            if not private:
                raise ValueError("Öffentliche Odoo-Verbindungen benötigen HTTPS")
        self.database = os.environ.get("ODOO_RPC_DB", "FraWo_GbR")
        self.key = os.environ.get("ODOO_RPC_API_KEY") or os.environ.get("ODOO_API_KEY")
        if not self.key:
            raise ValueError("Odoo-API-Key aus Vaultwarden in ODOO_RPC_API_KEY bereitstellen")
        login = os.environ.get("ODOO_RPC_USER", "agent@frawo.tech")
        common = xmlrpc.client.ServerProxy(endpoint + "/xmlrpc/2/common", transport=RpcTransport(parsed.scheme == "https"))
        self.uid = common.authenticate(self.database, login, self.key, {})
        if not self.uid:
            raise ValueError("Odoo-Anmeldung fehlgeschlagen")
        self.models = xmlrpc.client.ServerProxy(endpoint + "/xmlrpc/2/object", transport=RpcTransport(parsed.scheme == "https"))

    def call(self, model, method, args=None, kwargs=None):
        return self.models.execute_kw(self.database, self.uid, self.key, model, method, args or [], kwargs or {})


def collect_snapshot(rpc, task_id):
    tasks = rpc.call("project.task", "read", [[task_id]], {"fields": ["name", "description", "project_id", "sale_order_id", "user_ids"]})
    if len(tasks) != 1:
        raise ValueError("Event-Aufgabe nicht lesbar")
    task = tasks[0]
    parser = DescriptionText()
    parser.feed(task.get("description") or "")
    description = "".join(parser.parts)
    dated = re.search(r"\bDatum:\s*[^\d·\n]*(\d{2}\.\d{2}\.\d{4})", description)
    located = re.search(r"\bOrt:\s*([^·\n]+)", description)
    event_date = date.fromisoformat("-".join(reversed(dated.group(1).split(".")))).isoformat() if dated else None
    users = rpc.call("res.users", "read", [task["user_ids"]], {"fields": ["name"]}) if task["user_ids"] else []
    snapshot = {
        "task_id": task_id,
        "project_name": task["project_id"][1] if task["project_id"] else task["name"],
        "event_date": event_date,
        "location": located.group(1).strip() if located else None,
        "technicians": [user["name"] for user in users if not user["name"].startswith("🤖")],
        "order_name": None,
        "order_state": None,
        "items": [],
    }
    if not task["sale_order_id"]:
        return snapshot
    order = rpc.call("sale.order", "read", [[task["sale_order_id"][0]]], {"fields": ["name", "state", "order_line"]})[0]
    snapshot.update(order_name=order["name"], order_state=order["state"])
    if not order["order_line"]:
        return snapshot
    lines = rpc.call("sale.order.line", "read", [order["order_line"]], {"fields": ["product_id", "product_uom_qty", "product_uom_id", "display_type", "is_downpayment"]})
    lines = [line for line in lines if line["product_id"] and not line["display_type"] and not line["is_downpayment"]]
    product_ids = sorted({line["product_id"][0] for line in lines})
    products = rpc.call("product.product", "read", [product_ids], {"fields": ["name", "type"]}) if product_ids else []
    products = {product["id"]: product for product in products}
    for line in lines:
        product = products[line["product_id"][0]]
        snapshot["items"].append({
            "product_id": product["id"], "name": product["name"], "type": product["type"],
            "quantity": line["product_uom_qty"], "uom": line["product_uom_id"][1],
        })
    return snapshot


def validate_snapshot(snapshot):
    if type(snapshot.get("task_id")) is not int or snapshot["task_id"] <= 0:
        raise ValueError("Eine positive Odoo-Aufgaben-ID ist erforderlich")
    if snapshot.get("event_date"):
        date.fromisoformat(snapshot["event_date"])
    ranges = []
    for item in snapshot.get("items", []):
        quantity = item.get("quantity")
        if isinstance(quantity, bool) or not isinstance(quantity, (float, int)) or not math.isfinite(quantity) or quantity < 0:
            raise ValueError("Ungültige Menge im Auftrag")
        if item.get("type") not in {"service", "consu", "product", "combo"}:
            raise ValueError("Unbekannter Produkt-Typ")
        if not item.get("dmx"):
            continue
        dmx = item["dmx"]
        values = [dmx.get(field) for field in ("universe", "start", "channels")]
        if any(type(value) is not int for value in values):
            raise ValueError("DMX benötigt ganzzahlige Angaben")
        universe, start, channels = values
        if quantity != 1 or universe < 1 or start < 1 or channels < 1 or start + channels - 1 > 512:
            raise ValueError("DMX-Adresse/Modus ungültig oder Menge nicht einzeln aufgelöst")
        end = start + channels - 1
        if any(universe == prior[0] and start <= prior[2] and end >= prior[1] for prior in ranges):
            raise ValueError("DMX-Adressen überlappen")
        ranges.append((universe, start, end))


def set_style(cell, **changes):
    parts = [part for part in cell.get("style", "").split(";") if part and part.split("=", 1)[0] not in changes]
    parts.extend(f"{name}={value}" for name, value in changes.items())
    cell.set("style", ";".join(parts) + ";")


def metadata(snapshot):
    event_date = date.fromisoformat(snapshot["event_date"]).strftime("%d.%m.%Y") if snapshot.get("event_date") else "offen"
    technicians = ", ".join(snapshot.get("technicians") or []) or "offen"
    return f"Event: {snapshot['project_name']} | Datum: {event_date}\nOrt: {snapshot.get('location') or 'offen'} | Techniker: {technicians}\nQuelle: Odoo Aufgabe #{snapshot['task_id']} / {snapshot.get('order_name') or 'kein Auftrag'}"


def item_label(item):
    label = f"{item['quantity']:g} {item['uom']} · {item['name']}"
    if item.get("dmx"):
        dmx = item["dmx"]
        label += f"\nU{dmx['universe']} / Start {dmx['start']} / {dmx['channels']} Kanäle"
    return label


def add_cell(root, cell_id, value, position, **styles):
    cell = ET.SubElement(root, "mxCell", id=cell_id, value=value, vertex="1", parent="1")
    set_style(cell, html=0, whiteSpace="wrap", fontSize=12, align="left", **styles)
    horizontal, vertical, width, height = position
    ET.SubElement(cell, "mxGeometry", x=str(horizontal), y=str(vertical), width=str(width), height=str(height), **{"as": "geometry"})
    return cell


def generate_plan(snapshot, template_dir=TEMPLATE_DIR):
    validate_snapshot(snapshot)
    goods = [item for item in snapshot.get("items", []) if item["type"] in {"consu", "product"} and item["quantity"] > 0]
    document = ET.Element("mxfile", host="frawo.tech", agent="FraWo Eventplan", version="24.0.0", frawo_task_id=str(snapshot["task_id"]))
    for filename in TEMPLATES:
        source = ET.parse(template_dir / filename).getroot()
        diagram = copy.deepcopy(source.find("diagram"))
        model = diagram.find("mxGraphModel")
        root = model.find("root")
        original_height = int(model.get("pageHeight"))
        model.set("pageHeight", str(original_height + 270))
        for cell in root.findall("mxCell"):
            if cell.get("vertex") == "1":
                set_style(cell, html=0)
                if cell.get("id") == "title":
                    continue
                if cell.get("id") == "meta":
                    cell.set("value", metadata(snapshot))
                    cell.find("mxGeometry").set("width", "1080")
                    cell.find("mxGeometry").set("height", "55")
                    continue
                label = re.sub(r"\([^)]*\)", "", cell.get("value", "").split("\n")[0]).strip()
                cell.set("value", f"Vorlage: {label}\nZuordnung / technische Daten offen")
                set_style(cell, fillColor="#f1f5f9", strokeColor="#94a3b8", fontColor="#64748b", dashed=1)
                geometry = cell.find("mxGeometry")
                geometry.set("y", str(float(geometry.get("y", "0")) + 70))
            elif cell.get("edge") == "1":
                cell.set("value", "Verbindung offen")
                set_style(cell, html=0, dashed=1, strokeColor="#94a3b8", fontColor="#64748b")
        grouped = {}
        for item in goods:
            for pattern, diagram_id, cell_id in DEVICE_TARGETS:
                if diagram.get("id") == diagram_id and re.search(pattern, item["name"], re.IGNORECASE):
                    grouped.setdefault(cell_id, []).append(item)
                    break
        for cell_id, items in grouped.items():
            cell = root.find(f"mxCell[@id='{cell_id}']")
            if cell is None:
                raise ValueError(f"Vorlagen-Ziel fehlt: {diagram.get('id')}/{cell_id}")
            label = "\n".join(item_label(item) for item in items)
            label += "\nAdresse / Modus: offen" if diagram.get("id") == "dmx_plan" and any(not item.get("dmx") for item in items) else "\nAufteilung / Anschluss: offen"
            cell.set("value", label)
            cell.set("frawo_product_ids", ",".join(str(item["product_id"]) for item in items))
            set_style(cell, fillColor="#dcfce7", strokeColor="#16a34a", fontColor="#14532d", dashed=0)
            cell.find("mxGeometry").set("height", str(max(90, 30 + len(items) * 45)))
        add_cell(root, "source_note", "Grün: Sachartikel aus Auftrag, Mengen als Gruppe. Grau: Vorlage, nicht belegt.\nPositionen und Verbindungen sind schematisch und offen. Keine technische Freigabe.", (40, original_height + 90, 1080, 80), fillColor="#fef3c7", strokeColor="#d97706")
        document.append(diagram)
    packlist = ET.SubElement(document, "diagram", id="packlist", name="Packliste aus Odoo")
    model = ET.SubElement(packlist, "mxGraphModel", page="1", pageWidth="1169", pageHeight=str(max(827, 230 + len(goods) * 90)))
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    add_cell(root, "title", "Packliste · Sachartikel aus dem Odoo-Auftrag", (40, 30, 1080, 30), fontStyle=1, fontColor="#0f172a")
    add_cell(root, "meta", metadata(snapshot), (40, 70, 1080, 60), fontColor="#475569")
    for index, item in enumerate(goods):
        add_cell(root, f"item_{index}", item_label(item) + f"\nOdoo Produkt #{item['product_id']}", (40, 155 + index * 90, 1080, 75), fillColor="#dcfce7", strokeColor="#16a34a")
    if not goods:
        add_cell(root, "empty", "Keine Sachartikel im Auftrag. Technik / Material des Auftraggebers klären.", (40, 155, 1080, 75), fillColor="#fef3c7", strokeColor="#d97706")
    combos = [item["name"] for item in snapshot.get("items", []) if item["type"] == "combo" and item["quantity"] > 0]
    if combos:
        add_cell(root, "unresolved_combos", "Kombi-Produkte nicht aufgelöst: " + ", ".join(combos), (40, 250 + len(goods) * 90, 1080, 75), fillColor="#fef3c7", strokeColor="#d97706")
    if snapshot.get("order_state") not in {"sale", "done"}:
        add_cell(root, "unconfirmed_order", "Auftrag nicht bestätigt oder nicht verknüpft. Positionen sind keine Buchungs-/Lieferbestätigung.", (40, 250 + len(goods) * 90 + bool(combos) * 90, 1080, 75), fillColor="#fee2e2", strokeColor="#ef4444")
    model.set("pageHeight", str(max(827, 350 + len(goods) * 90 + bool(combos) * 90)))
    ET.indent(document, space="  ")
    return ET.tostring(document, encoding="unicode")


def editor_link(xml):
    compressor = zlib.compressobj(wbits=-15)
    compressed = compressor.compress(quote(xml, safe="~()*!.'-").encode("utf-8")) + compressor.flush()
    return "https://frawo.tech/draw/#R" + quote(base64.b64encode(compressed).decode("ascii"), safe="")


def publish_plan(rpc, task_id, xml):
    if ET.fromstring(xml).get("frawo_task_id") != str(task_id):
        raise ValueError("Eventplan gehört nicht zur Zielaufgabe")
    if not rpc.call("project.task", "read", [[task_id]], {"fields": ["id"]}):
        raise ValueError("Zielaufgabe ist nicht lesbar")
    name = f"FraWo_Eventplan_{task_id}.auto.drawio"
    identity = [["res_model", "=", "project.task"], ["res_id", "=", task_id], ["name", "=", name]]
    existing = rpc.call("ir.attachment", "search_read", [identity], {"fields": ["name", "datas", "public"], "limit": 2})
    if len(existing) > 1:
        raise ValueError("Mehrere gleichnamige Anhänge: manuelle Klärung erforderlich")
    content = xml.encode("utf-8")
    values = {"name": name, "datas": base64.b64encode(content).decode("ascii"), "mimetype": "application/xml", "type": "binary", "res_model": "project.task", "res_id": task_id, "public": False}
    unchanged = bool(existing and not existing[0]["public"] and base64.b64decode(existing[0]["datas"] or "") == content)
    if existing:
        attachment_id = existing[0]["id"]
        if not unchanged:
            rpc.call("ir.attachment", "write", [[attachment_id], values])
    else:
        attachment_id = rpc.call("ir.attachment", "create", [values])
    verified = rpc.call("ir.attachment", "read", [[attachment_id]], {"fields": ["name", "datas", "res_model", "res_id", "public"]})
    if len(verified) != 1 or any(verified[0].get(field) != values[field] for field in ("name", "res_model", "res_id", "public")) or base64.b64decode(verified[0].get("datas") or "") != content:
        raise ValueError("Anhang am Ziel nicht unverändert/private bestätigt")
    marker = "FraWo Eventplan SHA256:" + hashlib.sha256(content).hexdigest()
    delivered = rpc.call("mail.message", "search_read", [[["model", "=", "project.task"], ["res_id", "=", task_id], ["body", "ilike", marker]]], {"fields": ["id"], "limit": 1})
    if not delivered:
        body = f'<p>🤖 [Codex] Eventplan aus Odoo erzeugt. <a href="{html.escape(editor_link(xml), quote=True)}">In Draw.io öffnen</a>. Grün: Auftragsmaterial; grau: offene Vorlagenposition. Technische Freigabe ausstehend. Bearbeitete Pläne separat speichern; .auto.drawio wird bei neuer Befüllung ersetzt.</p><p><code>{marker}</code></p>'
        rpc.call("project.task", "message_post", [[task_id]], {"body": body, "body_is_html": True, "subtype_xmlid": "mail.mt_note", "partner_ids": [], "attachment_ids": [attachment_id]})
    return attachment_id


def main(argv=None):
    parser = argparse.ArgumentParser(description="Odoo-Event als vorbefüllten Draw.io-Plan erzeugen")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--task", type=int)
    source.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args(argv)
    rpc = OdooRpc() if args.task is not None or args.publish else None
    snapshot = collect_snapshot(rpc, args.task) if args.task is not None else json.loads(args.input.read_text(encoding="utf-8"))
    xml = generate_plan(snapshot)
    args.output.write_text(xml, encoding="utf-8", newline="\n")
    result = {"output": str(args.output), "task_id": snapshot["task_id"]}
    if args.publish:
        result["attachment_id"] = publish_plan(rpc, snapshot["task_id"], xml)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, xmlrpc.client.Error, ET.ParseError):
        print("Eventplan fehlgeschlagen. Eingabedaten, Berechtigungen und Odoo-Verbindung prüfen.", file=sys.stderr)
        raise SystemExit(1)
