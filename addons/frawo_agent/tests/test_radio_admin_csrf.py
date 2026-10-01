# -*- coding: utf-8 -*-
"""CSRF-Schutz fuer die PVE-Bridge-Admin-Routen (Odoo #1803).

/radio/admin/curate, /radio/admin/upload, /radio/admin/delete sind
type='http', auth='user', csrf=False (sie koennen kein normales Odoo-
CSRF-Token nutzen, weil upload multipart ist und curate/delete von
externen Werkzeugen aufgerufen werden koennen sollen). Vorbild fuer das
Testmuster: test_radio_urteil.py::TestRadioUrteilRoutes.
"""
import json
from unittest.mock import patch

from odoo.tests import HttpCase, tagged


class _FakeBridgeResponse:
    def __init__(self, status_code=200, text='{"ok":true}'):
        self.status_code = status_code
        self.text = text


@tagged("post_install", "-at_install", "frawo_agent")
class TestRadioAdminCsrf(HttpCase):
    def setUp(self):
        super().setUp()
        self.admin = self.env["res.users"].create({
            "name": "Admin Route Test",
            "login": "admin_test_radio_admin_csrf",
            "password": "admin_test_radio_admin_csrf_pw",
            "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
        })

    def _auth(self):
        self.authenticate("admin_test_radio_admin_csrf", "admin_test_radio_admin_csrf_pw")

    # ── /radio/admin/curate: kein Body -> Herkunfts-Check ───────────────────

    def test_curate_fremde_herkunft_403(self):
        self._auth()
        r = self.url_open("/radio/admin/curate", method="POST",
                           headers={"Origin": "https://evil.example.com"})
        self.assertEqual(r.status_code, 403)

    def test_curate_ohne_herkunfts_header_403(self):
        self._auth()
        r = self.url_open("/radio/admin/curate", method="POST")
        self.assertEqual(r.status_code, 403)

    @patch("odoo.addons.frawo_agent.controllers.main.requests.post")
    def test_curate_legitime_herkunft_laeuft_durch(self, mock_post):
        mock_post.return_value = _FakeBridgeResponse(200, '{"ok":true}')
        self._auth()
        r = self.url_open("/radio/admin/curate", method="POST",
                           headers={"Origin": self.base_url()})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(mock_post.called)

    @patch("odoo.addons.frawo_agent.controllers.main.requests.post")
    def test_curate_legitime_herkunft_ueber_referer_laeuft_durch(self, mock_post):
        # Fallback: kein Origin-Header, aber ein passender Referer (manche
        # Browser/Clients senden bei POST nur Referer).
        mock_post.return_value = _FakeBridgeResponse(200, '{"ok":true}')
        self._auth()
        r = self.url_open("/radio/admin/curate", method="POST",
                           headers={"Referer": self.base_url() + "/frawo/hub"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(mock_post.called)

    # ── /radio/admin/upload: multipart + Herkunfts-Check ────────────────────

    def test_upload_falscher_content_type_415(self):
        self._auth()
        r = self.url_open("/radio/admin/upload", method="POST",
                           data="kein multipart", headers={"Content-Type": "text/plain"})
        self.assertEqual(r.status_code, 415)

    def test_upload_multipart_fremde_herkunft_403(self):
        self._auth()
        r = self.url_open("/radio/admin/upload", method="POST",
                           files={"file": ("a.mp3", b"123", "audio/mpeg")},
                           headers={"Origin": "https://evil.example.com"})
        self.assertEqual(r.status_code, 403)

    def test_upload_multipart_ohne_herkunfts_header_403(self):
        self._auth()
        r = self.url_open("/radio/admin/upload", method="POST",
                           files={"file": ("a.mp3", b"123", "audio/mpeg")})
        self.assertEqual(r.status_code, 403)

    @patch("odoo.addons.frawo_agent.controllers.main.requests.post")
    def test_upload_multipart_legitime_herkunft_laeuft_durch(self, mock_post):
        mock_post.return_value = _FakeBridgeResponse(200, '{"ok":true}')
        self._auth()
        r = self.url_open("/radio/admin/upload", method="POST",
                           files={"file": ("a.mp3", b"123", "audio/mpeg")},
                           headers={"Origin": self.base_url()})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(mock_post.called)

    # ── /radio/admin/delete: JSON-Content-Type reicht (wie /redaktion/urteil) ──

    def test_delete_falscher_content_type_415(self):
        self._auth()
        r = self.url_open("/radio/admin/delete", method="POST",
                           data="filename=a.mp3", headers={"Content-Type": "text/plain"})
        self.assertEqual(r.status_code, 415)

    @patch("odoo.addons.frawo_agent.controllers.main.requests.post")
    def test_delete_json_laeuft_durch(self, mock_post):
        mock_post.return_value = _FakeBridgeResponse(200, '{"ok":true}')
        self._auth()
        r = self.url_open("/radio/admin/delete", method="POST",
                           data=json.dumps({"filename": "a.mp3"}),
                           headers={"Content-Type": "application/json"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(mock_post.called)
