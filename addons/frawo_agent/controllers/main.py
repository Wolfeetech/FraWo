from odoo import http, fields
from odoo.http import request
import logging
import re
import time
import requests
import urllib3

# Suppress insecure certificate warnings for internal API call
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_logger = logging.getLogger(__name__)

class RadioController(http.Controller):

    def _get_azuracast_config(self):
        get_param = request.env['ir.config_parameter'].sudo().get_param
        base_url = get_param('frawo_agent.azuracast_api_url', 'https://10.1.0.38').rstrip('/')
        api_key = get_param('frawo_agent.azuracast_api_key', '')
        return base_url, api_key

    def _get_pve_bridge_config(self):
        get_param = request.env['ir.config_parameter'].sudo().get_param
        bridge_url = get_param('frawo_agent.pve_bridge_url', 'http://10.1.0.128:8888').rstrip('/')
        bridge_token = get_param('frawo_agent.pve_bridge_token', '')
        return bridge_url, bridge_token

    def _is_internal_user(self):
        """Check if the current user is an internal (non-portal, non-public) user."""
        user = request.env.user
        if not user or user._is_public():
            return False
        # Check if user has internal user group
        return user.has_group('base.group_user')

    def _check_rate_limit(self, action, cooldown):
        """Per-browser-session cooldown for public write endpoints (radio votes/requests,
        lead form). These routes are intentionally auth='public' — anonymous website
        visitors and radio listeners are the real users — so the guard is a cooldown,
        not a login/kiosk-token requirement (that would just break the feature).
        """
        session = request.session
        key = f'_frawo_rate_{action}'
        now = time.time()
        last = session.get(key, 0)
        if now - last < cooldown:
            return False
        session[key] = now
        return True

    # ─────────────────────────────────────────────────────────────
    # Public Radio Endpoints
    # ─────────────────────────────────────────────────────────────

    @http.route('/radio/vote', type='json', auth='public', cors='*', methods=['POST'])
    def radio_vote(self, song_id, vote_type, **kwargs):
        user = request.env.user
        _logger.info("Radio vote received: User %s (ID: %s) voted '%s' on song '%s'", user.name, user.id, vote_type, song_id)
        
        try:
            log_vals = {
                "name": f"Radio Vote: {vote_type}",
                "level": "info",
                "message": f"User {user.name} (ID: {user.id}) voted '{vote_type}' on song '{song_id}'"
            }
            # Create the log entry as sudo
            request.env["frawo.agent.log"].sudo().create(log_vals)
            
            # If vote is 'hate' (Skip), call AzuraCast API to skip the current track
            if vote_type == 'hate':
                if not self._check_rate_limit('radio_skip', cooldown=30):
                    return {"status": "error", "message": "Bitte kurz warten, bevor der nächste Skip-Vote gesendet wird."}
                base_url, api_key = self._get_azuracast_config()
                api_url = f"{base_url}/api/station/1/backend/skip"
                headers = {
                    "X-API-Key": api_key
                }
                _logger.info("Sending skip request to AzuraCast at %s...", api_url)
                r = requests.post(api_url, headers=headers, verify=False, timeout=5)
                if r.status_code == 200:
                    _logger.info("AzuraCast song skipped successfully.")
                    return {"status": "success", "message": "Skip registered and song skipped."}
                else:
                    _logger.warning("AzuraCast skip returned status %s: %s", r.status_code, r.text)
                    return {"status": "success", "message": f"Skip logged, but AzuraCast skip failed (status {r.status_code})."}
            
            return {"status": "success", "message": f"Vote {vote_type} registered for song {song_id}"}
        except Exception as e:
            _logger.error("Failed to register radio vote: %s", str(e))
            return {"status": "error", "message": str(e)}

    @http.route('/radio/search', type='json', auth='public', cors='*', methods=['POST'])
    def radio_search(self, query, **kwargs):
        if not query:
            return {"status": "success", "tracks": []}
        try:
            base_url, api_key = self._get_azuracast_config()
            api_url = f"{base_url}/api/station/1/requests"
            headers = {"X-API-Key": api_key}
            r = requests.get(api_url, headers=headers, verify=False, timeout=5)
            if r.status_code != 200:
                return {"status": "error", "message": f"Failed to fetch requests (status {r.status_code})"}
            
            all_tracks = r.json()
            query_lower = query.lower()
            results = []
            for item in all_tracks:
                song = item.get("song", {})
                title = song.get("title", "") or ""
                artist = song.get("artist", "") or ""
                album = song.get("album", "") or ""
                if query_lower in title.lower() or query_lower in artist.lower() or query_lower in album.lower():
                    results.append({
                        "request_id": item.get("request_id"),
                        "title": title,
                        "artist": artist,
                        "album": album,
                        "art": song.get("art")
                    })
                    if len(results) >= 15:
                        break
            return {"status": "success", "tracks": results}
        except Exception as e:
            _logger.error("Radio search failed: %s", str(e))
            return {"status": "error", "message": str(e)}

    @http.route('/radio/request', type='json', auth='public', cors='*', methods=['POST'])
    def radio_request(self, request_id, **kwargs):
        if not request_id:
            return {"status": "error", "message": "Missing request_id"}
        if not self._check_rate_limit('radio_request', cooldown=60):
            return {"status": "error", "message": "Bitte warte kurz, bevor du den nächsten Song anfragst."}
        try:
            base_url, api_key = self._get_azuracast_config()
            api_url = f"{base_url}/api/station/1/request/{request_id}"
            headers = {"X-API-Key": api_key}
            _logger.info("Sending song request to AzuraCast for request_id %s...", request_id)
            r = requests.post(api_url, headers=headers, verify=False, timeout=5)
            if r.status_code == 200:
                res_data = r.json()
                msg = res_data.get("message", "Song-Request erfolgreich übermittelt!")
                # Log the request
                log_vals = {
                    "name": "Radio Request",
                    "level": "info",
                    "message": f"User {request.env.user.name} (ID: {request.env.user.id}) requested track {request_id}: {msg}"
                }
                request.env["frawo.agent.log"].sudo().create(log_vals)
                return {"status": "success", "message": msg}
            else:
                try:
                    res_data = r.json()
                    msg = res_data.get("message", f"Request failed (status {r.status_code})")
                except Exception:
                    msg = f"Request failed with status {r.status_code}: {r.text}"
                _logger.warning("AzuraCast request returned status %s: %s", r.status_code, r.text)
                return {"status": "error", "message": msg}
        except Exception as e:
            _logger.error("Failed to submit radio request: %s", str(e))
            return {"status": "error", "message": str(e)}


    @http.route('/radio/nowplaying', type='http', auth='public', methods=['GET'], cors='*', csrf=False)
    def radio_nowplaying_proxy(self, **kwargs):
        try:
            base_url, api_key = self._get_azuracast_config()
            r = requests.get(f"{base_url}/api/station/1/nowplaying", verify=False, timeout=5)
            if r.status_code == 200:
                text = r.text.replace("https://10.1.0.38", "https://funk.frawo.tech").replace("http://10.1.0.38", "https://funk.frawo.tech")
                return request.make_response(
                    text,
                    headers=[
                        ('Content-Type', 'application/json'),
                        ('Access-Control-Allow-Origin', '*'),
                        ('Cache-Control', 'no-cache')
                    ],
                    status=200
                )
            return request.make_response(r.text, status=r.status_code, headers=[('Content-Type', 'application/json')])
        except Exception as e:
            return request.make_response(
                f'{{"status":"error","message":"{str(e)}"}}',
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    # ─────────────────────────────────────────────────────────────
    # Admin-Only: PVE Bridge Proxy Endpoints
    # ─────────────────────────────────────────────────────────────

    @http.route('/radio/admin/status', type='http', auth='user', methods=['GET'], csrf=False)
    def radio_admin_status(self, **kwargs):
        if not self._is_internal_user():
            return request.make_response(
                '{"status":"error","message":"Forbidden"}',
                headers=[('Content-Type', 'application/json')],
                status=403
            )
        try:
            bridge_url, bridge_token = self._get_pve_bridge_config()
            r = requests.get(
                f"{bridge_url}/status",
                headers={"Authorization": f"Bearer {bridge_token}"},
                timeout=8
            )
            return request.make_response(
                r.text,
                headers=[('Content-Type', 'application/json')],
                status=r.status_code
            )
        except Exception as e:
            _logger.error("PVE bridge status error: %s", str(e))
            return request.make_response(
                f'{{"status":"error","message":"{str(e)}"}}',
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/radio/admin/curate', type='http', auth='user', methods=['POST'], csrf=False)
    def radio_admin_curate(self, **kwargs):
        if not self._is_internal_user():
            return request.make_response(
                '{"status":"error","message":"Forbidden"}',
                headers=[('Content-Type', 'application/json')],
                status=403
            )
        try:
            bridge_url, bridge_token = self._get_pve_bridge_config()
            r = requests.post(
                f"{bridge_url}/curate",
                headers={"Authorization": f"Bearer {bridge_token}"},
                timeout=10
            )
            _logger.info("Curation triggered via API. Status: %s", r.status_code)
            return request.make_response(
                r.text,
                headers=[('Content-Type', 'application/json')],
                status=r.status_code
            )
        except Exception as e:
            _logger.error("PVE bridge curate error: %s", str(e))
            return request.make_response(
                f'{{"status":"error","message":"{str(e)}"}}',
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/radio/admin/upload', type='http', auth='user', methods=['POST'], csrf=False)
    def radio_admin_upload(self, **kwargs):
        if not self._is_internal_user():
            return request.make_response(
                '{"status":"error","message":"Forbidden"}',
                headers=[('Content-Type', 'application/json')],
                status=403
            )
        try:
            bridge_url, bridge_token = self._get_pve_bridge_config()
            # Forward the raw multipart request body to the PVE daemon
            content_type = request.httprequest.content_type
            body = request.httprequest.get_data()
            r = requests.post(
                f"{bridge_url}/upload",
                headers={
                    "Authorization": f"Bearer {bridge_token}",
                    "Content-Type": content_type,
                },
                data=body,
                timeout=120
            )
            _logger.info("File upload forwarded to PVE bridge. Status: %s", r.status_code)
            return request.make_response(
                r.text,
                headers=[('Content-Type', 'application/json')],
                status=r.status_code
            )
        except Exception as e:
            _logger.error("PVE bridge upload error: %s", str(e))
            return request.make_response(
                f'{{"status":"error","message":"{str(e)}"}}',
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/radio/admin/delete', type='http', auth='user', methods=['POST'], csrf=False)
    def radio_admin_delete(self, **kwargs):
        if not self._is_internal_user():
            return request.make_response(
                '{"status":"error","message":"Forbidden"}',
                headers=[('Content-Type', 'application/json')],
                status=403
            )
        try:
            bridge_url, bridge_token = self._get_pve_bridge_config()
            body = request.httprequest.get_data()
            r = requests.post(
                f"{bridge_url}/delete",
                headers={
                    "Authorization": f"Bearer {bridge_token}",
                    "Content-Type": "application/json",
                },
                data=body,
                timeout=10
            )
            return request.make_response(
                r.text,
                headers=[('Content-Type', 'application/json')],
                status=r.status_code
            )
        except Exception as e:
            _logger.error("PVE bridge delete error: %s", str(e))
            return request.make_response(
                f'{{"status":"error","message":"{str(e)}"}}',
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    # ─────────────────────────────────────────────────────────────
    # Prometheus Metrics Exporter: Anker Tracker
    # ─────────────────────────────────────────────────────────────

    @http.route('/anker/metrics', type='http', auth='public', methods=['GET'], csrf=False)
    def anker_prometheus_metrics(self, **kwargs):
        """Prometheus metrics endpoint for Anker Tracker drink consumption."""
        try:
            lines = [
                "# HELP anker_unbilled_bottles Total unbilled bottles per product",
                "# TYPE anker_unbilled_bottles gauge",
            ]
            products = request.env['anker.tracker.product'].sudo().search([('active', '=', True)])
            for p in products:
                # Count unbilled bottles
                unbilled = sum(
                    c.quantity for c in request.env['anker.tracker.consumption'].sudo().search([
                        ('product_id', '=', p.id),
                        ('billed', '=', False)
                    ])
                )
                safe_name = p.name.replace('"', '\\"')
                lines.append(f'anker_unbilled_bottles{{product="{safe_name}",emoji="{p.emoji}"}} {unbilled}')

            # Consumers metric
            lines.append("# HELP anker_active_consumers Total active consumers")
            lines.append("# TYPE anker_active_consumers gauge")
            consumer_count = request.env['anker.tracker.consumer'].sudo().search_count([('active', '=', True)])
            lines.append(f'anker_active_consumers {consumer_count}')

            content = "\n".join(lines) + "\n"
            return request.make_response(content, headers=[('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')])
        except Exception as e:
            _logger.error("Anker metrics error: %s", str(e))
            return request.make_response(f"# Error: {str(e)}\n", status=500, headers=[('Content-Type', 'text/plain')])

    # ─────────────────────────────────────────────────────────────
    # Printable Settlement Report: Anker Tracker (Task #804)
    # ─────────────────────────────────────────────────────────────

    @http.route('/anker/report/settlement', type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def anker_settlement_report(self, **kwargs):
        """Printable settlement report for Anker Tracker drink consumption."""
        try:
            # Handle Mark as Billed action
            if request.httprequest.method == 'POST' and kwargs.get('action') == 'mark_billed':
                open_records = request.env['anker.tracker.consumption'].sudo().search([('billed', '=', False)])
                open_records.write({'billed': True})
                _logger.info("Anker Tracker: Marked %s consumption records as billed.", len(open_records))

            # Fetch consumers and unbilled consumption
            consumers = request.env['anker.tracker.consumer'].sudo().search([('active', '=', True)], order='sequence, name asc')
            consumption_model = request.env['anker.tracker.consumption'].sudo()

            consumer_reports = []
            grand_total = 0.0
            grand_bottles = 0
            grand_crates = 0

            for c in consumers:
                unbilled = consumption_model.search([('consumer_id', '=', c.id), ('billed', '=', False)])
                if not unbilled:
                    continue

                items_dict = {}
                person_total = 0.0

                for rec in unbilled:
                    prod = rec.product_id
                    key = prod.id
                    if key not in items_dict:
                        items_dict[key] = {
                            'name': prod.name,
                            'emoji': prod.emoji,
                            'price': prod.price_per_bottle,
                            'pfand_bottle': prod.pfand_per_bottle,
                            'pfand_crate': prod.pfand_per_crate,
                            'bottles': 0,
                            'crates': 0,
                            'subtotal': 0.0
                        }

                    if rec.unit_type == 'crate':
                        items_dict[key]['crates'] += 1
                        items_dict[key]['bottles'] += rec.quantity
                        cost = (rec.quantity * prod.price_per_bottle) + (rec.quantity * prod.pfand_per_bottle) + prod.pfand_per_crate
                    else:
                        items_dict[key]['bottles'] += rec.quantity
                        cost = (rec.quantity * prod.price_per_bottle) + (rec.quantity * prod.pfand_per_bottle)

                    items_dict[key]['subtotal'] += cost
                    person_total += cost
                    grand_total += cost

                    if rec.unit_type == 'crate':
                        grand_crates += 1
                    grand_bottles += rec.quantity

                consumer_reports.append({
                    'consumer': c,
                    'items': list(items_dict.values()),
                    'total': person_total
                })

            html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Getränkemarkt-Abrechnung — FraWo GbR</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 30px; color: #222; background: #fff; }}
        .header {{ border-bottom: 3px solid #1a237e; padding-bottom: 12px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .header h1 {{ margin: 0; font-size: 24px; color: #1a237e; }}
        .header p {{ margin: 4px 0 0 0; font-size: 13px; color: #666; }}
        .person-card {{ border: 1px solid #e0e0e0; border-radius: 8px; margin-bottom: 20px; padding: 16px; page-break-inside: avoid; }}
        .person-title {{ font-size: 18px; font-weight: bold; color: #0d47a1; margin-bottom: 12px; border-bottom: 1px solid #eeeeee; padding-bottom: 6px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 14px; }}
        th {{ background: #f5f5f5; text-align: left; padding: 8px; font-weight: 600; border-bottom: 2px solid #ddd; }}
        td {{ padding: 8px; border-bottom: 1px solid #eee; }}
        .total-row {{ font-weight: bold; background: #f9f9f9; }}
        .grand-summary {{ background: #e8eaf6; border: 2px solid #3f51b5; border-radius: 8px; padding: 18px; margin-top: 30px; font-size: 16px; display: flex; justify-content: space-between; align-items: center; }}
        .grand-total {{ font-size: 24px; font-weight: 900; color: #1a237e; }}
        .actions {{ margin-bottom: 20px; display: flex; gap: 12px; }}
        .btn {{ padding: 10px 18px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; font-size: 14px; text-decoration: none; }}
        .btn-print {{ background: #1a237e; color: #fff; }}
        .btn-bill {{ background: #2e7d32; color: #fff; }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ margin: 0; padding: 0; }}
            .person-card {{ border: 1px solid #ccc; }}
        }}
    </style>
</head>
<body>

<div class="actions no-print">
    <button class="btn btn-print" onclick="window.print()">🖨️ Abrechnung Drucken / PDF Export</button>
    <form method="POST" action="/anker/report/settlement" style="display:inline;" onsubmit="return confirm('Möchtest du alle offenen Entnahmen wirklich als abgerechnet markieren?');">
        <input type="hidden" name="action" value="mark_billed"/>
        <button type="submit" class="btn btn-bill">✅ Als abgerechnet markieren</button>
    </form>
</div>

<div class="header">
    <div>
        <h1>FraWo GbR — Anker Getränkemarkt</h1>
        <p>Stockenweiler 3, 88138 Hergensweiler | Offene Verbrauchsabrechnung</p>
    </div>
    <div style="text-align:right;">
        <p><strong>Datum:</strong> {fields.Date.today().strftime('%d.%m.%Y')}</p>
        <p><strong>Status:</strong> Offene Posten</p>
    </div>
</div>

{"".join([f'''
<div class="person-card">
    <div class="person-title">👤 {rep["consumer"].name}</div>
    <table>
        <thead>
            <tr>
                <th>Getränk</th>
                <th>Anzahl Flaschen</th>
                <th>Kisten</th>
                <th>Einzelpreis (€)</th>
                <th>Pfand (€)</th>
                <th style="text-align:right;">Gesamt (€)</th>
            </tr>
        </thead>
        <tbody>
            {"".join([f"""
            <tr>
                <td>{item["emoji"]} {item["name"]}</td>
                <td>{item["bottles"]} Fl.</td>
                <td>{item["crates"]} Kiste(n)</td>
                <td>{item["price"]:.2f} €</td>
                <td>{(item["bottles"] * item["pfand_bottle"] + item["crates"] * item["pfand_crate"]):.2f} €</td>
                <td style="text-align:right;">{item["subtotal"]:.2f} €</td>
            </tr>
            """ for item in rep["items"]])}
            <tr class="total-row">
                <td colspan="5">Zwischensumme {rep["consumer"].name}</td>
                <td style="text-align:right; color:#1a237e;">{rep["total"]:.2f} €</td>
            </tr>
        </tbody>
    </table>
</div>
''' for rep in consumer_reports]) if consumer_reports else '<p style="font-size:16px; color:#666;">Keine offenen Entnahmen vorhanden. Alle Getränke sind abgerechnet! 🎉</p>'}

<div class="grand-summary">
    <div>
        <strong>Gesamter offener Verbrauch:</strong><br/>
        <small style="color:#555;">{grand_bottles} Flaschen ({grand_crates} Kisten)</small>
    </div>
    <div class="grand-total">{grand_total:.2f} €</div>
</div>

<div style="margin-top:40px; font-size:12px; color:#888; text-align:center;">
    FraWo GbR | Anker Tracker Odoo System | Automatisch generiert am {fields.Datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
</div>

</body>
</html>"""
            return request.make_response(html_content, headers=[('Content-Type', 'text/html; charset=utf-8')])
        except Exception as e:
            _logger.error("Anker settlement report error: %s", str(e))
            return request.make_response(f"<h2>Fehler bei der Abrechnungserstellung:</h2><p>{str(e)}</p>", status=500, headers=[('Content-Type', 'text/html')])

    # ─────────────────────────────────────────────────────────────
    # Agent & Bot Status API (Task #827)
    # ─────────────────────────────────────────────────────────────

    # Token für den Zugriff auf die Zusammenfassung. Steht ausschliesslich in
    # der Datenbank, niemals im Quellcode — das Repo ist öffentlich.
    SUMMARY_TOKEN_PARAM = 'frawo_agent.summary_token'

    def _check_summary_auth(self):
        """Lässt angemeldete Benutzer durch, sonst wird ein Token verlangt.

        BEFUND 29.07.2026: Dieser Endpunkt stand auf auth='public' OHNE jede
        Prüfung und las per sudo() interne Zahlen. Über den Cloudflare-Tunnel
        war er aus dem offenen Internet erreichbar:

            curl https://frawo.tech/api/agent/summary
            {"unbilled_bottles": 134, "open_tasks_count": 168, ...}

        Kein Einbruch, aber eine unnötige Auskunft an jeden, der die Adresse
        kennt. Gleiches Muster wie beim Kiosk (_check_kiosk_auth): Token aus
        ir.config_parameter, Vergleich mit consteq gegen Zeitmessung, und
        fail closed — ist kein Token gesetzt, ist der Endpunkt zu.
        """
        from odoo.tools import consteq

        user = request.env.user
        if user and not user._is_public():
            return True

        expected = (request.env['ir.config_parameter'].sudo()
                    .get_param(self.SUMMARY_TOKEN_PARAM, '') or '').strip()
        if not expected:
            _logger.warning(
                "Agent-Zusammenfassung abgelehnt — Systemparameter %s ist nicht gesetzt.",
                self.SUMMARY_TOKEN_PARAM,
            )
            return False

        token = (request.httprequest.headers.get('X-Agent-Token')
                 or request.params.get('token') or '')
        return consteq(token, expected)

    @http.route('/api/agent/summary', type='http', auth='public', methods=['GET'], csrf=False)
    def agent_summary_api(self, **kwargs):
        """JSON summary endpoint for OpenClaw & Telegram Bots."""
        import json
        if not self._check_summary_auth():
            return request.make_response(
                json.dumps({'error': 'unauthorized'}),
                headers=[('Content-Type', 'application/json')],
                status=401,
            )
        try:
            # Unbilled Anker bottles
            try:
                unbilled = sum(
                    c.quantity
                    for c in request.env['anker.tracker.consumption'].sudo().search([('billed', '=', False)])
                )
            except Exception:
                unbilled = 0

            # Open tasks count
            try:
                open_tasks = request.env['project.task'].sudo().search_count([('active', '=', True), ('stage_id', 'in', [1, 2, 143, 144, 159])])
            except Exception:
                open_tasks = 0

            # Live Radio Now Playing
            try:
                base_url, api_key = self._get_azuracast_config()
                r = requests.get(f"{base_url}/api/station/1/nowplaying", verify=False, timeout=3)
                np = r.json() if r.status_code == 200 else {}
                song = np.get('now_playing', {}).get('song', {})
                now_playing = f"{song.get('artist', '')} - {song.get('title', '')}".strip(" -")
                listeners = np.get('listeners', {}).get('current', 0)
            except Exception:
                now_playing = "—"
                listeners = 0

            data = {
                "status": "ok",
                "unbilled_bottles": unbilled,
                "open_tasks_count": open_tasks,
                "radio_now_playing": now_playing,
                "radio_listeners": listeners,
                "timestamp": fields.Datetime.now().isoformat()
            }
            return request.make_response(json.dumps(data, indent=2), headers=[('Content-Type', 'application/json')])
        except Exception as e:
            return request.make_response(json.dumps({"status": "error", "message": str(e)}), status=500, headers=[('Content-Type', 'application/json')])

    # ─────────────────────────────────────────────────────────────
    # Surface Go Kiosk Terminal Landing Page (Task #826)
    # ─────────────────────────────────────────────────────────────

    @http.route('/kiosk', type='http', auth='public', methods=['GET'], csrf=False)
    def kiosk_home(self, **kwargs):
        """Touch-optimised Kiosk Landingpage for Surface Go (Werkstatt + Radio Curation)."""
        try:
            # Live AzuraCast now-playing
            try:
                base_url, api_key = self._get_azuracast_config()
                r = requests.get(f"{base_url}/api/station/1/nowplaying", verify=False, timeout=3)
                np = r.json() if r.status_code == 200 else {}
                now_title  = np.get('now_playing', {}).get('song', {}).get('title', '—')
                now_artist = np.get('now_playing', {}).get('song', {}).get('artist', '')
                listeners  = np.get('listeners', {}).get('current', '—')
                stream_url = np.get('station', {}).get('listen_url', '')
            except Exception:
                now_title = '—'; now_artist = ''; listeners = '—'; stream_url = ''

            # Unbilled Anker-bottles quick count
            try:
                total_unbilled = sum(
                    c.quantity
                    for c in request.env['anker.tracker.consumption'].sudo().search([('billed', '=', False)])
                )
            except Exception:
                total_unbilled = '?'

            html = f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no"/>
  <meta name="apple-mobile-web-app-capable" content="yes"/>
  <title>FraWo Kiosk</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg:      #0d0f14;
      --surface: #161a23;
      --card:    #1e2330;
      --accent:  #00e5ff;
      --accent2: #7c4dff;
      --green:   #00c853;
      --red:     #ff1744;
      --text:    #e8eaf6;
      --sub:     #7986cb;
      --radius:  16px;
    }}
    html, body {{ height: 100%; background: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; overflow: hidden; }}
    body {{ display: grid; grid-template-rows: auto 1fr auto; gap: 0; height: 100vh; }}

    /* ── HEADER ── */
    header {{
      background: var(--surface);
      padding: 14px 24px;
      display: flex; align-items: center; justify-content: space-between;
      border-bottom: 1px solid #1e2a3a;
    }}
    .logo {{ font-size: 22px; font-weight: 900; background: linear-gradient(90deg,var(--accent),var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .clock {{ font-size: 28px; font-weight: 800; color: var(--accent); font-variant-numeric: tabular-nums; }}
    .date-label {{ font-size: 13px; color: var(--sub); text-align: right; }}

    /* ── MAIN GRID ── */
    main {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 16px;
      padding: 16px;
      overflow: hidden;
    }}
    .tile {{
      background: var(--card);
      border-radius: var(--radius);
      padding: 22px;
      display: flex; flex-direction: column; gap: 12px;
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
      border: 1px solid #2a3044;
      text-decoration: none; color: inherit;
      -webkit-tap-highlight-color: transparent;
      user-select: none;
    }}
    .tile:active {{ transform: scale(0.97); box-shadow: 0 0 0 3px var(--accent); }}
    .tile-icon {{ font-size: 38px; line-height: 1; }}
    .tile-title {{ font-size: 20px; font-weight: 800; }}
    .tile-sub {{ font-size: 13px; color: var(--sub); }}
    .tile-badge {{
      align-self: flex-start;
      background: var(--accent2);
      color: #fff;
      font-size: 12px; font-weight: 700;
      padding: 3px 10px; border-radius: 999px;
      margin-top: auto;
    }}
    .tile.green {{ border-color: var(--green); }}
    .tile.green .tile-badge {{ background: var(--green); color: #000; }}
    .tile.radio {{ border-color: var(--accent); }}
    .tile.radio .tile-badge {{ background: var(--accent); color: #000; }}
    .tile.repair {{ border-color: var(--red); }}
    .tile.repair .tile-badge {{ background: var(--red); }}

    /* ── RADIO BAR ── */
    .radio-bar {{
      background: var(--surface);
      border-top: 1px solid #1e2a3a;
      padding: 12px 24px;
      display: flex; align-items: center; gap: 16px;
    }}
    .radio-bar .now-icon {{ font-size: 28px; animation: pulse 2s infinite; }}
    @keyframes pulse {{ 0%,100%{{ opacity:1 }} 50%{{ opacity:.4 }} }}
    .radio-bar .track-info {{ flex: 1; }}
    .radio-bar .track-title {{ font-size: 15px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 400px; }}
    .radio-bar .track-artist {{ font-size: 12px; color: var(--sub); }}
    .radio-bar .listeners {{ font-size: 13px; color: var(--sub); white-space: nowrap; }}
    .radio-bar .listeners span {{ font-weight: 700; color: var(--accent); }}
    .radio-btn {{
      background: var(--accent); color: #000;
      border: none; border-radius: 12px;
      padding: 10px 20px; font-size: 15px; font-weight: 800;
      cursor: pointer; text-decoration: none;
      transition: opacity 0.15s;
    }}
    .radio-btn:active {{ opacity: 0.7; }}
  </style>
</head>
<body>

<header>
  <div class="logo">⚡ FraWo Kiosk</div>
  <div style="text-align:right">
    <div class="clock" id="clock">--:--</div>
    <div class="date-label" id="dateline">--.--.----</div>
  </div>
</header>

<main>
  <!-- ODOO PROJECT BOARD -->
  <a class="tile" href="https://frawo.tech/odoo/project" target="_blank">
    <div class="tile-icon">📋</div>
    <div class="tile-title">Werkstatt-Board</div>
    <div class="tile-sub">Odoo Projekte &amp; Aufgaben</div>
    <div class="tile-badge">🚀 Odoo öffnen</div>
  </a>

  <!-- ANKER TRACKER SETTLEMENT -->
  <a class="tile green" href="/anker/report/settlement" target="_blank">
    <div class="tile-icon">🍺</div>
    <div class="tile-title">Getränke-Abrechnung</div>
    <div class="tile-sub">Anker Tracker — offene Posten</div>
    <div class="tile-badge">🧾 {total_unbilled} Flaschen offen</div>
  </a>

  <!-- RADIO CONTROL -->
  <a class="tile radio" href="https://funk.frawo.tech" target="_blank">
    <div class="tile-icon">🎛️</div>
    <div class="tile-title">FraWo Funk</div>
    <div class="tile-sub">AzuraCast Radio-Steuerung</div>
    <div class="tile-badge">🎙️ Radio öffnen</div>
  </a>

  <!-- IT EQUIPMENT / MAINTENANCE -->
  <a class="tile repair" href="https://frawo.tech/odoo/maintenance" target="_blank">
    <div class="tile-icon">🔧</div>
    <div class="tile-title">Wartung &amp; Reparaturen</div>
    <div class="tile-sub">Geräte-Register &amp; offene Aufträge</div>
    <div class="tile-badge">⚠️ Wartung öffnen</div>
  </a>
</main>

<!-- NOW PLAYING BAR -->
<div class="radio-bar">
  <div class="now-icon">🎵</div>
  <div class="track-info">
    <div class="track-title">{now_title}</div>
    <div class="track-artist">{now_artist}</div>
  </div>
  <div class="listeners">👂 <span>{listeners}</span> Hörer</div>
  <a class="radio-btn" href="{stream_url}" target="_blank">▶ Stream</a>
</div>

<script>
  function tick() {{
    const now = new Date();
    document.getElementById('clock').textContent =
      now.toLocaleTimeString('de-DE', {{hour:'2-digit', minute:'2-digit', second:'2-digit'}});
    document.getElementById('dateline').textContent =
      now.toLocaleDateString('de-DE', {{weekday:'long', day:'2-digit', month:'long', year:'numeric'}});
  }}
  tick();
  setInterval(tick, 1000);

  // Auto-refresh every 60 seconds to pick up live data
  setTimeout(() => location.reload(), 60000);
</script>
</body>
</html>"""
            return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
        except Exception as e:
            _logger.error("Kiosk page error: %s", str(e))
            return request.make_response(f"<h2>Kiosk Fehler:</h2><p>{str(e)}</p>", status=500, headers=[('Content-Type', 'text/html')])

    _EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

    @http.route('/website/lead/create', type='json', auth='public', cors='*', methods=['POST'], csrf=False)
    def website_lead_create(self, name=None, email=None, phone=None, message=None, subject=None, **kwargs):
        """Public API endpoint for website contact form -> Odoo CRM Lead creation."""
        try:
            name = (name or '').strip()
            email = (email or '').strip()
            phone = (phone or '').strip()
            message = (message or '').strip()
            subject = (subject or '').strip()

            if not name or not (email or phone):
                return {"status": "error", "message": "Name und E-Mail oder Telefon sind erforderlich."}
            if email and not self._EMAIL_RE.match(email):
                return {"status": "error", "message": "Bitte eine gültige E-Mail-Adresse angeben."}
            if len(name) > 200 or len(email) > 200 or len(phone) > 50 or len(subject) > 200 or len(message) > 5000:
                return {"status": "error", "message": "Eingabe zu lang."}
            if not self._check_rate_limit('website_lead', cooldown=60):
                return {"status": "error", "message": "Bitte warte kurz, bevor du eine weitere Anfrage sendest."}

            lead_vals = {
                "name": subject or f"Website-Anfrage: {name}",
                "contact_name": name,
                "email_from": email or "",
                "phone": phone or "",
                "description": message or "",
                "type": "lead",
                "user_id": 7,  # Assigned to Agent
            }
            lead = request.env["crm.lead"].sudo().create(lead_vals)
            _logger.info("Website Lead created successfully: ID %s (%s)", lead.id, name)
            return {"status": "success", "lead_id": lead.id, "message": "Vielen Dank für Ihre Anfrage!"}
        except Exception as e:
            _logger.error("Failed to create website lead: %s", str(e))
            return {"status": "error", "message": "Anfrage konnte nicht gespeichert werden."}




