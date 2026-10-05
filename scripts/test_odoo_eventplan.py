from __future__ import annotations

import base64
import copy
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from urllib.parse import unquote

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import odoo_eventplan
except ModuleNotFoundError:
    odoo_eventplan = None


@pytest.fixture
def generator():
    return odoo_eventplan


@pytest.fixture
def snapshot():
    return {
        "task_id": 1628,
        "project_name": "Halloweenparty",
        "event_date": "2026-10-31",
        "location": "Kressbronn",
        "technicians": ["Wolf Prinz", "Franz Bienert"],
        "order_name": "S00057",
        "order_state": "sale",
        "items": [
            {"product_id": 153, "name": "Fachkraft VT", "type": "service", "quantity": 1, "uom": "Tag"},
        ],
    }


def test_real_templates_become_one_document_without_modifying_sources(generator, snapshot):
    assert generator is not None, "Der Eventplan-Generator fehlt noch"
    sources = {source: source.read_bytes() for source in generator.TEMPLATE_DIR.glob("*.drawio")}
    document = ET.fromstring(generator.generate_plan(snapshot))
    assert len(document.findall("diagram")) == 5
    assert all(source.read_bytes() == contents for source, contents in sources.items())
    for diagram in document.findall("diagram"):
        metadata = diagram.find(".//mxCell[@id='meta']")
        assert "Halloweenparty" in metadata.get("value")
        assert "31.10.2026" in metadata.get("value")
        assert "Kressbronn" in metadata.get("value")
        assert "Franz Bienert" in metadata.get("value")


def test_personnel_only_order_does_not_invent_equipment_or_addresses(generator, snapshot):
    document = ET.fromstring(generator.generate_plan(snapshot))
    labels = "\n".join(cell.get("value", "") for cell in document.iter("mxCell"))
    assert "Keine Sachartikel im Auftrag" in labels
    assert "Fachkraft VT" not in labels
    assert "CH 001" not in labels
    assert "HPF 100Hz" not in labels
    assert "192.168.10.1" not in labels
    assert not document.findall(".//mxCell[@frawo_product_ids]")


def test_unknown_metadata_stays_explicitly_open(generator, snapshot):
    snapshot.update(event_date=None, location=None, technicians=[])
    labels = ET.fromstring(generator.generate_plan(snapshot)).find(".//mxCell[@id='meta']").get("value")
    assert "Datum: offen" in labels
    assert "Ort: offen" in labels
    assert "Techniker: offen" in labels


def test_booked_devices_are_grouped_without_invented_wiring(generator, snapshot):
    snapshot["items"] = [
        {"product_id": 10, "name": "Moving Head Spot", "type": "consu", "quantity": 2, "uom": "Stück"},
        {"product_id": 11, "name": "Moving Head Beam", "type": "consu", "quantity": 3, "uom": "Stück"},
        {"product_id": 12, "name": "Stativ", "type": "consu", "quantity": 1, "uom": "Stück"},
    ]
    document = ET.fromstring(generator.generate_plan(snapshot))
    moving_heads = document.find(".//diagram[@id='dmx_plan']//mxCell[@id='mh1']")
    assert "2 Stück" in moving_heads.get("value")
    assert "3 Stück" in moving_heads.get("value")
    assert "Adresse / Modus: offen" in moving_heads.get("value")
    assert "CH 001" not in moving_heads.get("value")
    assert "Stativ" in document.find(".//diagram[@id='packlist']").find(".//mxCell[@id='item_2']").get("value")
    assert all("dashed=1" in cell.get("style", "") for cell in document.iter("mxCell") if cell.get("edge") == "1")


def test_labels_are_plain_text_even_with_html_like_input(generator, snapshot):
    snapshot["project_name"] = '<img src="x" onerror="alert(1)"> & Gäste'
    xml = generator.generate_plan(snapshot)
    metadata = ET.fromstring(xml).find(".//mxCell[@id='meta']")
    assert metadata.get("value").startswith("Event: <img")
    assert "html=0" in metadata.get("style")
    assert "&lt;img" in xml


@pytest.mark.parametrize("quantity", [-1, float("nan"), float("inf")])
def test_invalid_quantities_are_rejected(generator, snapshot, quantity):
    snapshot["items"] = [{"product_id": 10, "name": "Moving Head", "type": "consu", "quantity": quantity, "uom": "Stück"}]
    with pytest.raises(ValueError, match="Menge"):
        generator.generate_plan(snapshot)


def test_explicit_dmx_configuration_is_preserved(generator, snapshot):
    snapshot["items"] = [{"product_id": 10, "name": "Moving Head", "type": "consu", "quantity": 1, "uom": "Stück", "dmx": {"universe": 1, "start": 20, "channels": 16}}]
    labels = ET.fromstring(generator.generate_plan(snapshot)).find(".//mxCell[@id='mh1']").get("value")
    assert "U1 / Start 20 / 16 Kanäle" in labels


@pytest.mark.parametrize("dmx", [{"universe": 1, "start": 500, "channels": 16}, {"universe": 0, "start": 1, "channels": 16}])
def test_invalid_dmx_configuration_is_rejected(generator, snapshot, dmx):
    snapshot["items"] = [{"product_id": 10, "name": "Moving Head", "type": "consu", "quantity": 1, "uom": "Stück", "dmx": dmx}]
    with pytest.raises(ValueError, match="DMX"):
        generator.generate_plan(snapshot)


def test_overlapping_dmx_addresses_are_rejected(generator, snapshot):
    snapshot["items"] = [
        {"product_id": 10, "name": "Moving Head", "type": "consu", "quantity": 1, "uom": "Stück", "dmx": {"universe": 1, "start": 1, "channels": 16}},
        {"product_id": 11, "name": "LED PAR", "type": "consu", "quantity": 1, "uom": "Stück", "dmx": {"universe": 1, "start": 16, "channels": 6}},
    ]
    with pytest.raises(ValueError, match="überlappen"):
        generator.generate_plan(snapshot)


def test_link_contains_exact_plan_in_browser_fragment(generator, snapshot):
    xml = generator.generate_plan(snapshot)
    link = generator.editor_link(xml)
    assert link.startswith("https://frawo.tech/draw/#R")
    payload = unquote(link.split("#R", 1)[1])
    decoded = unquote(zlib.decompress(base64.b64decode(payload), -15).decode("utf-8"))
    assert decoded == xml


class FakeRpc:
    def __init__(self):
        self.attachments = []
        self.messages = []
        self.calls = []

    def call(self, model, method, args=None, kwargs=None):
        self.calls.append((model, method, copy.deepcopy(args), copy.deepcopy(kwargs)))
        if model == "ir.attachment":
            if method == "search_read":
                return copy.deepcopy(self.attachments)
            if method == "create":
                self.attachments.append({"id": 77, **args[0]})
                return 77
            if method == "write":
                self.attachments[0].update(args[1])
                return True
            if method == "read":
                return copy.deepcopy(self.attachments)
        if model == "project.task" and method == "message_post":
            self.messages.append(kwargs)
            return 88
        if model == "project.task" and method == "read":
            return [{"id": args[0][0]}]
        if model == "mail.message" and method == "search_read":
            marker = next(value for field, operation, value in args[0] if field == "body")
            return [{"id": 88}] if any(marker in message["body"] for message in self.messages) else []
        raise AssertionError((model, method))


def test_publishing_reuses_private_attachment_and_does_not_repeat_note(generator, snapshot):
    rpc = FakeRpc()
    xml = generator.generate_plan(snapshot)
    assert generator.publish_plan(rpc, 1628, xml) == 77
    assert generator.publish_plan(rpc, 1628, xml) == 77
    assert len(rpc.attachments) == 1
    assert rpc.attachments[0]["public"] is False
    assert rpc.attachments[0]["res_model"] == "project.task"
    assert rpc.attachments[0]["res_id"] == 1628
    assert len(rpc.messages) == 1
    assert rpc.messages[0]["subtype_xmlid"] == "mail.mt_note"
    assert rpc.messages[0]["partner_ids"] == []


def test_duplicate_attachment_identity_aborts_instead_of_overwriting(generator, snapshot):
    rpc = FakeRpc()
    rpc.attachments = [{"id": 1}, {"id": 2}]
    with pytest.raises(ValueError, match="Mehrere"):
        generator.publish_plan(rpc, 1628, generator.generate_plan(snapshot))
    assert not any(method in {"create", "write"} for model, method, args, kwargs in rpc.calls)
    assert not rpc.messages


def test_retry_after_failed_chatter_post_finishes_delivery(generator, snapshot):
    class InterruptedRpc(FakeRpc):
        interrupted = False

        def call(self, model, method, args=None, kwargs=None):
            if method == "message_post" and not self.interrupted:
                self.interrupted = True
                raise OSError("Verbindung abgebrochen")
            return super().call(model, method, args, kwargs)

    rpc = InterruptedRpc()
    xml = generator.generate_plan(snapshot)
    with pytest.raises(OSError):
        generator.publish_plan(rpc, 1628, xml)
    assert len(rpc.attachments) == 1
    assert not rpc.messages
    assert generator.publish_plan(rpc, 1628, xml) == 77
    assert len(rpc.attachments) == 1
    assert len(rpc.messages) == 1


def test_changed_source_updates_same_attachment_and_posts_new_revision(generator, snapshot):
    rpc = FakeRpc()
    assert generator.publish_plan(rpc, 1628, generator.generate_plan(snapshot)) == 77
    snapshot["location"] = "Andere Location"
    assert generator.publish_plan(rpc, 1628, generator.generate_plan(snapshot)) == 77
    assert len(rpc.attachments) == 1
    assert len(rpc.messages) == 2
    assert "Andere Location" in base64.b64decode(rpc.attachments[0]["datas"]).decode("utf-8")


def test_publishing_to_another_task_is_rejected_before_any_write(generator, snapshot):
    rpc = FakeRpc()
    with pytest.raises(ValueError, match="Zielaufgabe"):
        generator.publish_plan(rpc, 9999, generator.generate_plan(snapshot))
    assert not rpc.calls


def test_same_snapshot_generates_identical_content(generator, snapshot):
    assert generator.generate_plan(snapshot) == generator.generate_plan(snapshot)


@pytest.mark.parametrize("name, diagram_id, cell_id", [
    ("Martin Audio CX2", "audio_routing", "spk_top_l"),
    ("CEE-Verteiler", "power_network", "pwr_dist"),
    ("PoE Switch", "power_network", "net_sw"),
])
def test_device_mapping_uses_real_template_ids(generator, snapshot, name, diagram_id, cell_id):
    snapshot["items"] = [{"product_id": 10, "name": name, "type": "consu", "quantity": 1, "uom": "Stück"}]
    document = ET.fromstring(generator.generate_plan(snapshot))
    cell = document.find(f".//diagram[@id='{diagram_id}']//mxCell[@id='{cell_id}']")
    assert cell.get("frawo_product_ids") == "10"


def test_failed_attachment_readback_does_not_log_success(generator, snapshot):
    class CorruptRpc(FakeRpc):
        def call(self, model, method, args=None, kwargs=None):
            result = super().call(model, method, args, kwargs)
            if model == "ir.attachment" and method == "read":
                result[0]["datas"] = base64.b64encode(b"wrong contents").decode()
            return result

    rpc = CorruptRpc()
    with pytest.raises(ValueError, match="am Ziel"):
        generator.publish_plan(rpc, 1628, generator.generate_plan(snapshot))
    assert not rpc.messages


def test_collector_reads_explicit_event_details_and_product_types(generator):
    class SourceRpc:
        def call(self, model, method, args=None, kwargs=None):
            assert method == "read"
            return {
                "project.task": [{"id": 1628, "name": "Einsatz", "project_id": [171, "Halloweenparty"], "sale_order_id": [54, "S00057"], "user_ids": [6, 10, 7], "description": "<p><b>Datum:</b> Sa 31.10.2026, ab 19:00 Uhr · <b>Ort:</b> Kressbronn</p>"}],
                "res.users": [{"id": 6, "name": "Wolf Prinz"}, {"id": 10, "name": "Franz Bienert"}, {"id": 7, "name": "🤖 Agent"}],
                "sale.order": [{"id": 54, "name": "S00057", "state": "sale", "order_line": [221]}],
                "sale.order.line": [{"id": 221, "product_id": [153, "Fachkraft VT"], "product_uom_qty": 1, "product_uom_id": [3, "Tag"], "display_type": False, "is_downpayment": False}],
                "product.product": [{"id": 153, "name": "Fachkraft VT", "type": "service"}],
            }[model]

    collected = generator.collect_snapshot(SourceRpc(), 1628)
    assert collected["event_date"] == "2026-10-31"
    assert collected["location"] == "Kressbronn"
    assert collected["technicians"] == ["Wolf Prinz", "Franz Bienert"]
    assert collected["items"][0]["type"] == "service"


def test_combo_products_are_marked_unresolved(generator, snapshot):
    snapshot["items"] = [{"product_id": 10, "name": "PA-Paket", "type": "combo", "quantity": 1, "uom": "Paket"}]
    labels = "\n".join(cell.get("value", "") for cell in ET.fromstring(generator.generate_plan(snapshot)).iter("mxCell"))
    assert "Kombi-Produkte nicht aufgelöst: PA-Paket" in labels
