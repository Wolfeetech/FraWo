"""Regressionstest fuer check_no_plaintext_secrets.py (Odoo #1917).

Bildet die drei Formen nach, in denen die Webhook-Secrets vom 12.09. bis 05.10.2026
im oeffentlichen Repo standen, mit ERFUNDENEN Werten. Jede Form muss erkannt werden,
die heutige saubere Form (Wert aus der Umgebung bzw. credentials_file) darf nicht anschlagen.

Aufruf: python3 -m pytest scripts/tools/test_check_no_plaintext_secrets.py
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "chk", Path(__file__).with_name("check_no_plaintext_secrets.py"))
chk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chk)

FAKE = "frawo_testwert_nicht_echt_0000"


def _pruefe(tmp_path, name, inhalt):
    p = tmp_path / name
    p.write_text(inhalt, encoding="utf-8")
    return chk.check_configs([p])


def test_form1_alertmanager_credentials(tmp_path):
    yml = f"receivers:\n  - name: x\n    webhook_configs:\n      - http_config:\n          authorization:\n            credentials: {FAKE}\n"
    assert _pruefe(tmp_path, "alertmanager.yml", yml)


def test_form2_handler_konstanten(tmp_path):
    py = f'SECRET = "{FAKE}"\nALERT_SECRET = "{FAKE}"\nKLAUSI_SECRET = "{FAKE}"\n'
    assert len(_pruefe(tmp_path, "odoo_webhook_handler.py", py)) == 3


def test_form3_webhook_pfad_und_env(tmp_path):
    xml = f'<field name="webhook_url">http://10.1.0.31:19001/klausi-chatter/{FAKE}</field>\n'
    env = f"FRAWO_CHATTER_SECRET={FAKE}\n"
    assert _pruefe(tmp_path, "action.xml", xml)
    assert _pruefe(tmp_path, "handler.env", env)


def test_saubere_formen_bleiben_still(tmp_path):
    py = 'SECRET = _need("FRAWO_TASK_SECRET")\nTOKEN = os.environ.get("X_TOKEN", "")\n'
    yml = "          authorization:\n            credentials_file: /etc/prometheus/servassi-hook.token\n"
    sh = ('FRAWO_ALERT_SECRET=$A\nPASSWORD="$PASSWORD"\n'
          'ROUTER_PASSWORD="${ROUTER_PASSWORD}"\nICECAST_SOURCE_PASSWORD=REPLACE_AFTER_SETUP\n')
    assert not _pruefe(tmp_path, "ok.py", py)
    assert not _pruefe(tmp_path, "ok.yml", yml)
    assert not _pruefe(tmp_path, "ok.sh", sh)
