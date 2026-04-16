import getpass
import os
import xmlrpc.client
from dataclasses import dataclass


DEFAULT_ODOO_URL = "http://10.1.0.22:8069"
DEFAULT_ODOO_DB = "FraWo_GbR"


@dataclass
class OdooSession:
    url: str
    db: str
    username: str
    secret: str
    uid: int
    common: xmlrpc.client.ServerProxy
    models: xmlrpc.client.ServerProxy


def connect(
    default_user: str = "wolf@frawo-tech.de",
    *,
    url: str | None = None,
    db: str | None = None,
    prompt_for_username: bool = False,
    secret_label: str = "Odoo Passwort oder API-Key",
) -> OdooSession:
    url = url or os.getenv("ODOO_RPC_URL", DEFAULT_ODOO_URL)
    db = db or os.getenv("ODOO_RPC_DB", DEFAULT_ODOO_DB)

    username = os.getenv("ODOO_RPC_USER")
    if not username:
        if prompt_for_username:
            prompt = f"Odoo Login (Enter fuer '{default_user}'): "
            username = input(prompt).strip() or default_user
        else:
            username = default_user

    secret = os.getenv("ODOO_RPC_API_KEY") or os.getenv("ODOO_RPC_PASSWORD")
    if not secret:
        secret = getpass.getpass(f"{secret_label}: ")

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(db, username, secret, {})
    if not uid:
        raise RuntimeError("Authentifizierung fehlgeschlagen.")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
    return OdooSession(
        url=url,
        db=db,
        username=username,
        secret=secret,
        uid=uid,
        common=common,
        models=models,
    )
