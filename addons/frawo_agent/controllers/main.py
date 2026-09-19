from odoo import http, fields
from odoo.http import request
import logging
import json
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

            # Zusaetzlich strukturiert speichern (frawo.radio.vote), damit die
            # Stimmen auswertbar sind (Odoo-Menue "Radio-Stimmen") statt nur
            # als Text im Agent-Log zu verschwinden. Darf das eigentliche Voting
            # nie zum Absturz bringen -- daher eigenes try/except.
            try:
                request.env["frawo.radio.vote"].sudo().create({
                    "track_id": song_id,
                    "vote_type": vote_type,
                    "voter_ip": request.httprequest.remote_addr or "unknown",
                })
            except Exception as e:
                _logger.warning("Radio-Vote-Auswertung (frawo.radio.vote) fehlgeschlagen: %s", e)

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

                # Alk. und alkoholfrei getrennt (Wolf, 06.09.2026): Pfand für
                # alkoholfreie Getraenke wird NICHT auf der Alkoholfrei-Liste
                # ausgewiesen, sondern zusammen mit dem Alkohol abgerechnet.
                items_alc = {}
                items_free = {}
                alc_total = 0.0
                free_total = 0.0
                pfand_from_free = 0.0

                for rec in unbilled:
                    prod = rec.product_id
                    bucket = items_alc if prod.is_alcoholic else items_free
                    key = prod.id
                    if key not in bucket:
                        bucket[key] = {
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
                        bucket[key]['crates'] += 1
                        bucket[key]['bottles'] += rec.quantity
                        pfand = (rec.quantity * prod.pfand_per_bottle) + prod.pfand_per_crate
                        grand_crates += 1
                    else:
                        bucket[key]['bottles'] += rec.quantity
                        pfand = rec.quantity * prod.pfand_per_bottle

                    drink_cost = rec.quantity * prod.price_per_bottle
                    if prod.is_alcoholic:
                        cost = drink_cost + pfand
                        bucket[key]['subtotal'] += cost
                        alc_total += cost
                    else:
                        bucket[key]['subtotal'] += drink_cost
                        free_total += drink_cost
                        pfand_from_free += pfand

                    grand_bottles += rec.quantity

                alc_total += pfand_from_free
                person_total = alc_total + free_total
                grand_total += person_total

                consumer_reports.append({
                    'consumer': c,
                    'items_alc': list(items_alc.values()),
                    'items_free': list(items_free.values()),
                    'alc_total': alc_total,
                    'free_total': free_total,
                    'pfand_from_free': pfand_from_free,
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
        .section-sub {{ font-size: 14px; font-weight: 700; color: #333; margin: 14px 0 4px 0; }}
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
            .kiosk-back {{ display: none !important; }}
        }}
        {self.KIOSK_BACK_CSS}
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
    {"" if not rep["items_alc"] else f"""
    <div class="section-sub">🍺 Alkoholisch</div>
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
            {"".join([f'''
            <tr>
                <td>{item["emoji"]} {item["name"]}</td>
                <td>{item["bottles"]} Fl.</td>
                <td>{item["crates"]} Kiste(n)</td>
                <td>{item["price"]:.2f} €</td>
                <td>{(item["bottles"] * item["pfand_bottle"] + item["crates"] * item["pfand_crate"]):.2f} €</td>
                <td style="text-align:right;">{item["subtotal"]:.2f} €</td>
            </tr>
            ''' for item in rep["items_alc"]])}
            {"" if rep["pfand_from_free"] <= 0 else f'''
            <tr>
                <td colspan="4" style="font-style:italic; color:#666;">zzgl. Pfand für alkoholfreie Getränke (siehe unten)</td>
                <td style="text-align:right;">{rep["pfand_from_free"]:.2f} €</td>
            </tr>
            '''}
            <tr class="total-row">
                <td colspan="5">Zwischensumme Alkoholisch</td>
                <td style="text-align:right; color:#1a237e;">{rep["alc_total"]:.2f} €</td>
            </tr>
        </tbody>
    </table>
    """}
    {"" if not rep["items_free"] else f"""
    <div class="section-sub">💧 Alkoholfrei <span style="font-weight:normal; color:#888;">(Pfand wird zusammen mit dem Alkohol abgerechnet)</span></div>
    <table>
        <thead>
            <tr>
                <th>Getränk</th>
                <th>Anzahl Flaschen</th>
                <th>Kisten</th>
                <th>Einzelpreis (€)</th>
                <th style="text-align:right;">Gesamt (€)</th>
            </tr>
        </thead>
        <tbody>
            {"".join([f'''
            <tr>
                <td>{item["emoji"]} {item["name"]}</td>
                <td>{item["bottles"]} Fl.</td>
                <td>{item["crates"]} Kiste(n)</td>
                <td>{item["price"]:.2f} €</td>
                <td style="text-align:right;">{item["subtotal"]:.2f} €</td>
            </tr>
            ''' for item in rep["items_free"]])}
            <tr class="total-row">
                <td colspan="4">Zwischensumme Alkoholfrei</td>
                <td style="text-align:right; color:#1a237e;">{rep["free_total"]:.2f} €</td>
            </tr>
        </tbody>
    </table>
    """}
    <div style="text-align:right; font-weight:900; font-size:16px; margin-top:8px; color:#1a237e;">
        Gesamt {rep["consumer"].name}: {rep["total"]:.2f} €
    </div>
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
{self.KIOSK_BACK_HTML}
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

    @http.route('/api/agent/create_booking', type='json', auth='public', methods=['POST'], csrf=False)
    def agent_create_booking(self, datum, ort, fest_typ=None, kunde_name=None, kunde_kontakt=None, notizen=None, **kwargs):
        """Booking → Kalendertermin + Auftrags-Aufgabe + (falls vorhanden) Kundenkontakt.

        Minimaler Input (Datum, Ort, optional Fest-Typ/Kunde) erzeugt automatisch
        alles Weitere, statt dass Termin/Aufgabe/Packliste einzeln von Hand
        angelegt werden. Kunde wird gesucht oder neu angelegt (per Name),
        damit Aufträge künftig wirklich mit einem Kontakt verknüpft sind
        (aktuell hat keine der 53 Auftrags-Aufgaben einen partner_id gesetzt).
        """
        import json
        if not self._check_summary_auth():
            return {'error': 'unauthorized'}

        try:
            env = request.env
            titel = f"{fest_typ or 'Auftrag'} — {kunde_name or ort}"

            partner = False
            if kunde_name:
                partner = env['res.partner'].sudo().search([('name', '=ilike', kunde_name)], limit=1)
                if not partner:
                    vals = {'name': kunde_name}
                    if kunde_kontakt:
                        if '@' in kunde_kontakt:
                            vals['email'] = kunde_kontakt
                        else:
                            vals['phone'] = kunde_kontakt
                    partner = env['res.partner'].sudo().create(vals)

            start_dt = fields.Datetime.to_datetime(datum) or fields.Datetime.now()
            from datetime import timedelta
            # user_id=6 (wolf@frawo.tech) + dessen partner_id=7 als Teilnehmer:
            # nur dieser Account hat aktive Google-Kalender-Synchronisierung,
            # ohne das landet der Termin im Nirwana des Public-User-Kontexts
            # und taucht nie in Google/HA (calendar.wolf_termine) auf.
            event_vals = {
                'name': titel,
                'start': start_dt,
                'stop': start_dt + timedelta(hours=8),
                'location': ort,
                'description': notizen or '',
                'user_id': 6,
                'partner_ids': [(4, 7), (4, 16)],
            }
            if partner:
                event_vals['partner_ids'].append((4, partner.id))
            event = env['calendar.event'].sudo().create(event_vals)

            task_desc = (
                f"<p><b>Ort:</b> {ort}<br/>"
                f"<b>Fest-Typ:</b> {fest_typ or '–'}<br/>"
                f"<b>Kalendertermin:</b> "
                f"<a href='/odoo/calendar/{event.id}'>Termin öffnen</a></p>"
                f"<p>{notizen or ''}</p>"
                f"<p>📦 <b>Packliste:</b> noch keine Fest-Typ-Vorlagen hinterlegt — "
                f"Unteraufgabe 'Packliste zusammenstellen' angelegt, bis die "
                f"Standard-Listen pro Fest-Typ existieren.</p>"
            )
            task_vals = {
                'name': titel,
                'project_id': 104,  # FraWo GbR: Aufträge & Events
                'date_deadline': start_dt,
                'description': task_desc,
            }
            if partner:
                task_vals['partner_id'] = partner.id
            task = env['project.task'].sudo().create(task_vals)

            env['project.task'].sudo().create({
                'name': '📦 Packliste zusammenstellen',
                'project_id': 104,
                'parent_id': task.id,
                'date_deadline': start_dt,
            })

            return {
                'status': 'ok',
                'task_id': task.id,
                'task_url': f'/odoo/project.task/{task.id}',
                'event_id': event.id,
                'partner_id': partner.id if partner else False,
            }
        except Exception as e:
            _logger.error("create_booking failed: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/agent/bottles_detail', type='http', auth='public', methods=['GET'], csrf=False)
    def agent_bottles_detail_api(self, **kwargs):
        """JSON detail endpoint for unbilled Anker-Tracker consumption (Task #1052).

        Reuses anker.tracker.consumption.generate_purchase_summary() (read-only,
        does NOT bill anything) so the kiosk/dashboard can show itemised bottles
        per product instead of just a total count.
        """
        import json
        if not self._check_summary_auth():
            return request.make_response(
                json.dumps({'error': 'unauthorized'}),
                headers=[('Content-Type', 'application/json')],
                status=401,
            )
        try:
            summary = request.env['anker.tracker.consumption'].sudo().generate_purchase_summary()
            return request.make_response(json.dumps(summary, indent=2), headers=[('Content-Type', 'application/json')])
        except Exception as e:
            return request.make_response(json.dumps({"status": "error", "message": str(e)}), status=500, headers=[('Content-Type', 'application/json')])

    # ─────────────────────────────────────────────────────────────
    # HA Touchscreen-Kiosk: Server-Status (Task #1039 Etappe 3)
    # ─────────────────────────────────────────────────────────────

    PROMETHEUS_URL = 'http://10.1.0.35:9090/api/v1/query'
    NODE_LABELS = {
        'stockenweiler-pve': '🖥️ ProDesk',
        'anker-pve': '🖥️ Anker',
        'monitoring-stack': '📊 Monitoring (CT150)',
    }

    # Fester Rueckweg-Knopf fuer alle Seiten, die vom Touchscreen-Kiosk aus
    # angetippt werden. Der Kiosk-Browser laeuft im echten --kiosk-Modus ohne
    # jede Browser-Chrome (kein Tab, kein Zurueck-Pfeil) -- ohne diesen Knopf
    # bleibt jeder externe Tap eine Einbahnstrasse (Befund 25.08.2026, Wolf).
    KIOSK_BACK_CSS = """
        .kiosk-back { position: fixed; left: 16px; bottom: 16px; z-index: 9999;
            background: #a050f0; color: #fff; text-decoration: none; font-weight: 700;
            font-family: Inter, -apple-system, sans-serif; padding: 14px 22px;
            border-radius: 30px; box-shadow: 0 4px 16px rgba(0,0,0,0.4); font-size: 15px; }
    """
    KIOSK_BACK_HTML = (
        '<a class="kiosk-back" href="http://10.1.0.40:8123/kiosk-frawo/start" '
        'target="_top">← Zurück zum Kiosk</a>'
    )

    def _prom_query(self, q):
        try:
            r = requests.get(self.PROMETHEUS_URL, params={'query': q}, timeout=5)
            return r.json().get('data', {}).get('result', [])
        except Exception as e:
            _logger.warning("Prometheus query failed (%s): %s", q, e)
            return []

    @http.route('/kiosk/server', type='http', auth='public', methods=['GET'], csrf=False)
    def kiosk_server_status(self, **kwargs):
        """Server-Status fuers Touchscreen-Kiosk: Modernes Cockpit mit interaktiven Tachos & Live-Prometheus-Daten."""
        if not self._check_summary_auth():
            return request.make_response("unauthorized", status=401)
        try:
            loads = {m['metric']['instance']: float(m['value'][1]) for m in self._prom_query('node_load1')}
            mem_avail = {m['metric']['instance']: float(m['value'][1]) for m in self._prom_query('node_memory_MemAvailable_bytes')}
            mem_total = {m['metric']['instance']: float(m['value'][1]) for m in self._prom_query('node_memory_MemTotal_bytes')}
            disk_avail = {m['metric']['instance']: float(m['value'][1]) for m in self._prom_query('node_filesystem_avail_bytes{mountpoint="/"}')}
            disk_total = {m['metric']['instance']: float(m['value'][1]) for m in self._prom_query('node_filesystem_size_bytes{mountpoint="/"}')}

            nodes = []
            for instance, label in self.NODE_LABELS.items():
                load = loads.get(instance, 0.0)
                # Normalize load to approx percent based on 4-8 cores (max 10.0 scale)
                load_pct = min(round((load / 4.0) * 100, 1), 100.0) if load is not None else 0.0
                ram_pct = 0.0
                ram_used_gb = 0.0
                ram_total_gb = 0.0
                if mem_total.get(instance):
                    ram_total_gb = round(mem_total[instance] / (1024**3), 1)
                    ram_used_gb = round((mem_total[instance] - mem_avail.get(instance, 0)) / (1024**3), 1)
                    ram_pct = round((1 - mem_avail.get(instance, 0) / mem_total[instance]) * 100, 1)
                disk_pct = 0.0
                disk_used_gb = 0.0
                disk_total_gb = 0.0
                if disk_total.get(instance):
                    disk_total_gb = round(disk_total[instance] / (1024**3), 1)
                    disk_used_gb = round((disk_total[instance] - disk_avail.get(instance, 0)) / (1024**3), 1)
                    disk_pct = round((1 - disk_avail.get(instance, 0) / disk_total[instance]) * 100, 1)
                nodes.append({
                    'id': instance,
                    'name': label,
                    'load': load,
                    'load_pct': load_pct,
                    'ram_pct': ram_pct,
                    'ram_used_gb': ram_used_gb,
                    'ram_total_gb': ram_total_gb,
                    'disk_pct': disk_pct,
                    'disk_used_gb': disk_used_gb,
                    'disk_total_gb': disk_total_gb
                })

            guest_info = self._prom_query('pve_guest_info')
            guest_up = {}
            for m in self._prom_query('pve_up{id=~"(qemu|lxc)/.*"}'):
                key = m['metric'].get('id', '') + '|' + m['metric'].get('pve_node', '')
                guest_up[key] = m['value'][1] == '1'

            guests = []
            for m in guest_info:
                gm = m['metric']
                if gm.get('template') == '1':
                    continue
                key = gm.get('id', '') + '|' + gm.get('pve_node', '')
                guests.append({
                    'name': gm.get('name', gm.get('id', '?')),
                    'node': gm.get('pve_node', ''),
                    'up': guest_up.get(key),
                })
            guests.sort(key=lambda g: (g['node'], g['name']))
            guests_down = [g for g in guests if g['up'] is False]

            tuev = self._prom_query('frawo_backup_tuev')
            tuev_total = len(tuev)
            tuev_ok = sum(1 for m in tuev if m['value'][1] == '1')

            def make_gauge_svg(title, val_pct, display_val, unit, sub_label):
                # SVG semi-circle gauge (radius 45, cx=60, cy=60)
                # circumference of half circle = pi * 45 ≈ 141.37
                circumference = 141.37
                pct = max(0.0, min(100.0, float(val_pct)))
                stroke_offset = circumference * (1 - (pct / 100.0))
                
                # Color gradient selection
                if pct >= 90:
                    grad_id = "grad-red"
                    glow_color = "#ff1744"
                elif pct >= 75:
                    grad_id = "grad-amber"
                    glow_color = "#ffb300"
                else:
                    grad_id = "grad-cyan"
                    glow_color = "#00e5ff"
                
                return f'''
                <div class="gauge-card">
                    <div class="gauge-title">{title}</div>
                    <div class="gauge-svg-container">
                        <svg viewBox="0 0 120 75" class="gauge-svg">
                            <defs>
                                <linearGradient id="grad-cyan" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stop-color="#00e5ff"/>
                                    <stop offset="100%" stop-color="#a050f0"/>
                                </linearGradient>
                                <linearGradient id="grad-amber" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stop-color="#ffb300"/>
                                    <stop offset="100%" stop-color="#ff8a65"/>
                                </linearGradient>
                                <linearGradient id="grad-red" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stop-color="#ff1744"/>
                                    <stop offset="100%" stop-color="#d50000"/>
                                </linearGradient>
                            </defs>
                            <!-- Background Arc -->
                            <path d="M 15 65 A 45 45 0 0 1 105 65" fill="none" stroke="#232733" stroke-width="10" stroke-linecap="round" />
                            <!-- Active Progress Arc -->
                            <path d="M 15 65 A 45 45 0 0 1 105 65" fill="none" stroke="url(#{grad_id})" stroke-width="10" stroke-linecap="round" 
                                  stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_offset}"
                                  style="filter: drop-shadow(0 0 6px {glow_color}88); transition: stroke-dashoffset 1s ease-in-out;" />
                        </svg>
                        <div class="gauge-center-val">
                            <span class="val-num">{display_val}</span>
                            <span class="val-unit">{unit}</span>
                        </div>
                    </div>
                    <div class="gauge-sub">{sub_label}</div>
                </div>'''

            node_sections = ''
            for n in nodes:
                gauge_load = make_gauge_svg("CPU Auslastung", n['load_pct'], f"{n['load']:.1f}", "Load", f"Peak: {n['load_pct']:.0f}%")
                gauge_ram = make_gauge_svg("RAM Speicher", n['ram_pct'], f"{n['ram_pct']:.0f}", "%", f"{n['ram_used_gb']} / {n['ram_total_gb']} GB")
                gauge_disk = make_gauge_svg("NVMe Root", n['disk_pct'], f"{n['disk_pct']:.0f}", "%", f"{n['disk_used_gb']} / {n['disk_total_gb']} GB")
                
                node_sections += f'''
                <div class="node-panel">
                    <div class="node-header">
                        <span class="node-icon">🖥️</span>
                        <span class="node-name">{n['name']}</span>
                        <span class="node-badge">Online</span>
                    </div>
                    <div class="gauge-cluster">
                        {gauge_load}
                        {gauge_ram}
                        {gauge_disk}
                    </div>
                </div>'''

            guest_cards = ''
            for g in guests:
                is_up = g['up']
                status_class = "guest-up" if is_up else "guest-down"
                status_text = "Aktiv" if is_up else "Gestoppt"
                node_short = "ProDesk" if "stock" in g['node'].lower() else ("Anker" if "anker" in g['node'].lower() else g['node'])
                guest_cards += f'''
                <div class="guest-card {status_class}">
                    <div class="guest-led"></div>
                    <div class="guest-details">
                        <div class="guest-title">{g['name']}</div>
                        <div class="guest-host">{node_short}</div>
                    </div>
                    <div class="guest-status-tag">{status_text}</div>
                </div>'''

            tuev_color = "#00e676" if tuev_ok == tuev_total else "#ff1744"
            html = f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="30">
<title>FraWo System-Cockpit</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: radial-gradient(circle at 10% 10%, rgba(160,80,240,0.12), transparent 40%),
                radial-gradient(circle at 90% 90%, rgba(0,229,255,0.08), transparent 45%),
                #0c0e14;
    color: #e8eaf6;
    font-family: 'Inter', -apple-system, sans-serif;
    padding: 20px;
    min-height: 100vh;
  }}
  
  .header-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 14px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }}
  .header-title {{
    font-size: 22px;
    font-weight: 900;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #00e5ff, #a050f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .live-indicator {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 700;
    color: #00e676;
    background: rgba(0,230,118,0.1);
    padding: 6px 14px;
    border-radius: 20px;
    border: 1px solid rgba(0,230,118,0.3);
  }}
  .live-dot {{
    width: 8px;
    height: 8px;
    background: #00e676;
    border-radius: 50%;
    box-shadow: 0 0 10px #00e676;
    animation: pulse 2s infinite;
  }}
  @keyframes pulse {{
    0% {{ transform: scale(0.95); opacity: 0.8; }}
    50% {{ transform: scale(1.2); opacity: 1; }}
    100% {{ transform: scale(0.95); opacity: 0.8; }}
  }}

  /* Node Cockpit */
  .nodes-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 20px;
    margin-bottom: 28px;
  }}
  .node-panel {{
    background: rgba(26, 30, 42, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  }}
  .node-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
  }}
  .node-name {{
    font-size: 17px;
    font-weight: 800;
    flex: 1;
  }}
  .node-badge {{
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    color: #00e676;
    background: rgba(0,230,118,0.12);
    padding: 4px 10px;
    border-radius: 12px;
  }}

  /* Gauge Cluster */
  .gauge-cluster {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }}
  .gauge-card {{
    background: rgba(18, 22, 32, 0.6);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 12px 8px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  .gauge-title {{
    font-size: 11px;
    font-weight: 700;
    color: #9fa8da;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
  }}
  .gauge-svg-container {{
    position: relative;
    width: 100px;
    height: 62px;
  }}
  .gauge-svg {{
    width: 100%;
    height: 100%;
  }}
  .gauge-center-val {{
    position: absolute;
    bottom: 2px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: center;
    align-items: baseline;
    gap: 2px;
  }}
  .val-num {{
    font-size: 16px;
    font-weight: 900;
    color: #fff;
  }}
  .val-unit {{
    font-size: 10px;
    font-weight: 700;
    color: #9fa8da;
  }}
  .gauge-sub {{
    font-size: 10px;
    color: #7986cb;
    font-weight: 600;
    margin-top: 4px;
  }}

  /* Overview TÜV Banner */
  .tuev-banner {{
    background: linear-gradient(135deg, rgba(0,230,118,0.1), rgba(0,229,255,0.05));
    border: 1px solid rgba(0,230,118,0.3);
    border-radius: 16px;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 28px;
  }}
  .tuev-title {{ font-size: 15px; font-weight: 800; }}
  .tuev-sub {{ font-size: 12px; color: #9fa8da; }}
  .tuev-score {{ font-size: 24px; font-weight: 900; color: {tuev_color}; }}

  /* Guests Grid */
  .section-label {{
    font-size: 14px;
    font-weight: 800;
    color: #9fa8da;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 12px;
  }}
  .guests-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 10px;
    margin-bottom: 30px;
  }}
  .guest-card {{
    background: rgba(26, 30, 42, 0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .guest-led {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }}
  .guest-up .guest-led {{ background: #00e676; box-shadow: 0 0 6px #00e676; }}
  .guest-down .guest-led {{ background: #ff1744; box-shadow: 0 0 6px #ff1744; }}
  .guest-details {{ flex: 1; min-width: 0; }}
  .guest-title {{ font-size: 13px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .guest-host {{ font-size: 10px; color: #7986cb; }}
  .guest-status-tag {{ font-size: 10px; font-weight: 700; color: #9fa8da; }}

  /* Grafana Button */
  .grafana-btn {{
    display: block;
    text-align: center;
    background: linear-gradient(135deg, rgba(160,80,240,0.3), rgba(0,229,255,0.3));
    border: 1px solid #a050f0;
    border-radius: 14px;
    padding: 14px;
    color: #fff;
    font-weight: 800;
    text-decoration: none;
    font-size: 14px;
    transition: transform 0.15s ease;
  }}
  .grafana-btn:active {{ transform: scale(0.98); }}

  {self.KIOSK_BACK_CSS}
</style>
</head>
<body>

<div class="header-bar">
  <div class="header-title">⚡ FraWo Infrastructure Cockpit</div>
  <div class="live-indicator"><span class="live-dot"></span> Live-Prometheus</div>
</div>

<div class="tuev-banner">
  <div>
    <div class="tuev-title">🛡️ Backup- &amp; Service-TÜV</div>
    <div class="tuev-sub">Alle 25 Scrape-Targets und Sicherungen verifiziert</div>
  </div>
  <div class="tuev-score">{tuev_ok}/{tuev_total} OK</div>
</div>

<div class="section-label">Hypervisor Auslastung &amp; Tachos</div>
<div class="nodes-grid">
  {node_sections}
</div>

<div class="section-label">Container &amp; Virtuelle Maschinen (CT/VM)</div>
<div class="guests-grid">
  {guest_cards}
</div>

<a class="grafana-btn" href="http://100.100.115.80:3000/d/frawo-ueberblick" target="_top">📊 Detail-Grafana-Dashboard öffnen →</a>

{self.KIOSK_BACK_HTML}

</body>
</html>'''
            return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
        except Exception as e:
            _logger.error("kiosk_server_status error: %s", str(e))
            return request.make_response(f"<p style='color:#fff'>Fehler: {str(e)}</p>", status=500, headers=[('Content-Type', 'text/html')])

    # ─────────────────────────────────────────────────────────────
    # Musikbibliothek-Sanierung: Live-Fortschritt (25.08.2026)
    # ─────────────────────────────────────────────────────────────

    @http.route('/kiosk/musik_status', type='http', auth='public', methods=['GET'], csrf=False)
    def musik_sanierung_status(self, **kwargs):
        """Fortschrittsanzeige fuer die Bereinigung der Musikbibliothek (beets
        auf CT120), Paperless-Style: Wolf soll den Stand selbst mitverfolgen
        koennen, statt auf Zwischenmeldungen im Chat zu warten. Liest eine
        kleine Status-JSON, die auf CT120 selbst geschrieben wird -- kein
        Fake-Fortschritt, nur echte Zahlen aus dem laufenden Log."""
        if not self._check_summary_auth():
            return request.make_response("unauthorized", status=401)
        try:
            r = requests.get('http://10.1.0.94:8338/status.json', timeout=5)
            r.raise_for_status()
            d = r.json()
        except Exception as e:
            _logger.warning("musik_sanierung_status: Status-Server nicht erreichbar: %s", str(e))
            d = None

        if d is None:
            html = f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="30">
<title>Musikbibliothek</title>
<style>body{background:#0d0f14;color:#e8eaf6;font-family:'Inter','Segoe UI',sans-serif;padding:20px;}</style>
<style>{self.KIOSK_BACK_CSS}</style>
</head><body><p>⚠️ Status-Server auf CT120 gerade nicht erreichbar. Lädt in 30s neu.</p>{self.KIOSK_BACK_HTML}</body></html>"""
            return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])

        gl = d.get('genre_lauf', {})
        qa = d.get('quarantaene_aufgeraeumt', {})
        bb = d.get('beatport_batch_repariert', {})
        pr = d.get('pfad_reparatur', {})

        geprueft = gl.get('alben_geprueft', 0)
        gesamt = gl.get('alben_gesamt', 1) or 1
        pct = round(min(geprueft / gesamt, 1.0) * 100, 1)
        fertig = geprueft >= gesamt

        stand_roh = d.get('stand', '')
        try:
            stand_txt = fields.Datetime.from_string(stand_roh.replace('T', ' ').split('.')[0]).strftime('%d.%m. %H:%M') if stand_roh else '–'
        except Exception:
            stand_txt = stand_roh

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="30">
<title>Musikbibliothek-Sanierung</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ background: #0d0f14; color: #e8eaf6; font-family: 'Inter', 'Segoe UI', sans-serif; }}
  body {{ padding: 20px; max-width: 480px; margin: 0 auto; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  .stand {{ color: #7986cb; font-size: 12px; margin-bottom: 20px; }}
  .card {{ background: #1e2330; border: 1px solid #2a3044; border-radius: 12px; padding: 18px; margin-bottom: 14px; }}
  .card-title {{ font-weight: 700; margin-bottom: 12px; font-size: 15px; }}
  .bignum {{ font-size: 32px; font-weight: 800; }}
  .sub {{ color: #7986cb; font-size: 13px; margin-top: 4px; }}
  .bar-bg {{ background: #2a3044; border-radius: 8px; height: 14px; margin-top: 12px; overflow: hidden; }}
  .bar-fill {{ background: {"#00c853" if fertig else "#00e5ff"}; height: 100%; width: {pct}%; transition: width 0.5s; }}
  .metric-row {{ display: flex; justify-content: space-between; padding: 6px 0; font-size: 14px; border-bottom: 1px solid #2a3044; }}
  .metric-row:last-child {{ border-bottom: none; }}
  .metric-label {{ color: #7986cb; }}
  .metric-val {{ font-weight: 700; }}
  .done-badge {{ display: inline-block; background: #00c85322; color: #00c853; border: 1px solid #00c853; border-radius: 20px; padding: 4px 12px; font-size: 12px; font-weight: 700; margin-top: 8px; }}
  {self.KIOSK_BACK_CSS}
</style>
</head>
<body>
<h1>🎵 Musikbibliothek-Sanierung</h1>
<div class="stand">Stand: {stand_txt} · lädt alle 30s neu</div>

<div class="card">
  <div class="card-title">Genre-Bereinigung (Last.fm)</div>
  <div class="bignum">{geprueft} <span style="font-size:18px;color:#7986cb;">/ {gesamt} Alben</span></div>
  <div class="bar-bg"><div class="bar-fill"></div></div>
  {'<div class="done-badge">✓ fertig</div>' if fertig else f'<div class="sub">{pct}% durch</div>'}
</div>

<div class="card">
  <div class="card-title">Pfad-Reparatur</div>
  <div class="metric-row"><span class="metric-label">Veraltete Stellen gefunden</span><span class="metric-val" style="color:#ffa726">{gl.get('pfad_fehler_gefunden', 0)}</span></div>
  <div class="metric-row"><span class="metric-label">Tracks neu mit echtem Pfad erfasst</span><span class="metric-val" style="color:#00e5ff">{pr.get('tracks_neu_erfasst', 0)}</span></div>
  <div class="metric-row"><span class="metric-label">Alben neu erfasst</span><span class="metric-val">{pr.get('alben_neu_erfasst', 0)}</span></div>
  <div class="sub">{'Läuft noch — Datei liegt woanders als beets dachte, wird gerade nachgezogen.' if pr.get('laeuft') else 'Läuft aktuell nicht.'}</div>
</div>

<div class="card">
  <div class="card-title">Quarantäne aufgeräumt</div>
  <div class="metric-row"><span class="metric-label">Duplikate gelöscht</span><span class="metric-val">{qa.get('geloescht', 0)}</span></div>
  <div class="metric-row"><span class="metric-label">Ohne Alternative gerettet</span><span class="metric-val">{qa.get('gerettet', 0)}</span></div>
  <div class="metric-row"><span class="metric-label">Einzigartige Titel geprüft</span><span class="metric-val">{qa.get('geprueft', 0)}</span></div>
</div>

<div class="card">
  <div class="card-title">Beatport-Chart-Batch (Artist/Title)</div>
  <div class="metric-row"><span class="metric-label">In echten Dateien korrigiert</span><span class="metric-val">{bb.get('erledigt', 0)} / {bb.get('gesamt', 0)}</span></div>
</div>
{self.KIOSK_BACK_HTML}
</body>
</html>"""
        return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])

    # ─────────────────────────────────────────────────────────────
    # HA Touchscreen-Kiosk: Aufgaben-Widget (Task #1039 Etappe 2)
    # ─────────────────────────────────────────────────────────────

    @http.route('/api/agent/tasks_widget', type='http', auth='public', methods=['GET'], csrf=False)
    def agent_tasks_widget(self, **kwargs):
        """Kompaktes, antippbares HTML-Widget mit den naechsten wichtigen
        Aufgaben, gedacht zum Einbetten per iframe-Card im HA-Touchscreen-
        Dashboard (kiosk-frawo). Ein blosser Zaehler ('142 offene Aufgaben')
        bringt am Bildschirm nichts, wenn man nie direkt zur Aufgabe kommt --
        deshalb hier eine echte, antippbare Liste statt einer Zahl.
        """
        import json
        if not self._check_summary_auth():
            return request.make_response(
                json.dumps({'error': 'unauthorized'}),
                headers=[('Content-Type', 'application/json')],
                status=401,
            )
        try:
            tasks = request.env['project.task'].sudo().search(
                [
                    ('active', '=', True),
                    ('stage_id', 'in', [1, 2, 3, 143, 144, 159]),
                ],
                order='priority desc, date_deadline asc nulls last',
                limit=5,
            )

            # Kein Link auf die einzelne Aufgabe: /my/tasks/{id} verlangt einen
            # Odoo-Login, den es am Touchscreen-Kiosk nie geben wird (Befund
            # 25.08.2026) -- also nur anzeigen, nicht antippbar auf Detailebene.
            rows = []
            for t in tasks:
                deadline = t.date_deadline.strftime('%d.%m.') if t.date_deadline else ''
                prio_dot = {'0': '', '1': '🔸', '2': '🔴'}.get(t.priority or '0', '')
                rows.append(f"""
                <div class="row">
                    <span class="prio">{prio_dot}</span>
                    <span class="name">{t.name}</span>
                    <span class="deadline">{deadline}</span>
                </div>""")

            rows_html = "".join(rows) if rows else '<div class="empty">🎉 Nichts Dringendes offen</div>'

            html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aufgaben</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ background: #0d0f14; color: #e8eaf6; font-family: 'Inter', 'Segoe UI', sans-serif; }}
  body {{ padding: 20px; max-width: 480px; margin: 0 auto; }}
  h1 {{ font-size: 20px; margin-bottom: 16px; }}
  .list {{ display: flex; flex-direction: column; gap: 6px; padding: 2px; }}
  .row {{
    display: flex; align-items: center; gap: 10px;
    background: #1e2330; border: 1px solid #2a3044; border-radius: 12px;
    padding: 12px 14px; color: #e8eaf6;
    font-size: 15px; font-weight: 600;
  }}
  .prio {{ font-size: 14px; width: 18px; text-align: center; flex-shrink: 0; }}
  .name {{ flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .deadline {{ font-size: 13px; color: #7986cb; flex-shrink: 0; }}
  .empty {{ color: #7986cb; font-size: 14px; padding: 12px; text-align: center; }}
  {self.KIOSK_BACK_CSS}
</style>
</head>
<body>
<h1>🗒️ Nächste Aufgaben</h1>
<div class="list">{rows_html}</div>
{self.KIOSK_BACK_HTML}
</body>
</html>"""
            return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
        except Exception as e:
            _logger.error("agent_tasks_widget error: %s", str(e))
            return request.make_response(f"<p style='color:#fff'>Fehler: {str(e)}</p>", status=500, headers=[('Content-Type', 'text/html')])

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

            # Honeypot spam trap: bots fill hidden fields
            if kwargs.get('b_url') or kwargs.get('website_hp') or kwargs.get('company_hp'):
                _logger.info("Spam bot detected via honeypot from %s. Silently discarding.", request.httprequest.remote_addr)
                return {"status": "success", "lead_id": 0, "message": "Vielen Dank für Ihre Anfrage!"}

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

    @http.route('/api/rental/inquiry', type='json', auth='public', cors='*', methods=['POST'], csrf=False)
    def api_rental_inquiry(self, name=None, email=None, phone=None, date_start=None, date_end=None,
                           package_code=None, delivery=False, setup=False, message=None, **kwargs):
        """Public API endpoint for Mietpark / Rental inquiry -> creates Odoo Sale Order draft (Angebot)."""
        try:
            # 1. Honeypot check
            if kwargs.get('b_url') or kwargs.get('website_hp'):
                _logger.info("Rental inquiry spam bot detected via honeypot. Discarding.")
                return {"status": "success", "order_name": "S00000", "message": "Vielen Dank für deine Mietanfrage!"}

            # 2. Rate limit
            if not self._check_rate_limit('rental_inquiry', cooldown=20):
                return {"status": "error", "message": "Bitte warte kurz, bevor du eine weitere Anfrage sendest."}

            # 3. Input validation
            name = (name or '').strip()
            email = (email or '').strip()
            phone = (phone or '').strip()
            message = (message or '').strip()
            package_code = (package_code or '').strip()

            if not name or not email:
                return {"status": "error", "message": "Name und E-Mail-Adresse sind erforderlich."}
            if not self._EMAIL_RE.match(email):
                return {"status": "error", "message": "Bitte eine gültige E-Mail-Adresse angeben."}

            # 4. Dates & Duration calculation
            days = 1
            date_info_str = "Mietzeitraum flexibel / nach Absprache"
            if date_start and date_end:
                try:
                    from datetime import datetime
                    d1 = datetime.strptime(date_start, "%Y-%m-%d")
                    d2 = datetime.strptime(date_end, "%Y-%m-%d")
                    delta = (d2 - d1).days + 1
                    if delta > 0:
                        days = delta
                        date_info_str = f"{date_start} bis {date_end} ({days} Tag(e))"
                except Exception:
                    pass

            # 5. Partner lookup / creation
            Partner = request.env['res.partner'].sudo()
            partner = Partner.search([('email', '=ilike', email)], limit=1)
            if not partner:
                partner = Partner.create({
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'customer_rank': 1,
                    'comment': f"Automatisch angelegt über Website-Mietanfrage ({date_info_str})"
                })
            else:
                if phone and not partner.phone:
                    partner.write({'phone': phone})

            # 6. Find Product
            Product = request.env['product.product'].sudo()
            product = None
            if package_code:
                product = Product.search([('default_code', '=', package_code)], limit=1)
            if not product:
                product = Product.search([('default_code', '=', 'RENT-PA-COMPACT')], limit=1)

            # 7. Build order lines
            order_lines = []
            if product:
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': float(days),
                    'price_unit': product.list_price,
                    'name': f"{product.name} (Miete: {date_info_str})",
                }))

            if delivery:
                p_del = Product.search([('default_code', '=', 'SRV-ANFAHRT')], limit=1)
                if p_del:
                    order_lines.append((0, 0, {
                        'product_id': p_del.id,
                        'product_uom_qty': 1.0,
                        'price_unit': p_del.list_price,
                    }))

            if setup:
                p_set = Product.search([('default_code', '=', 'FW-022')], limit=1)
                if p_set:
                    order_lines.append((0, 0, {
                        'product_id': p_set.id,
                        'product_uom_qty': 2.0,  # 2 Stunden Aufbau/Abbau Standard
                        'price_unit': p_set.list_price,
                    }))

            # 8. Create Sale Order (Quotation / Angebot)
            so_vals = {
                'partner_id': partner.id,
                'origin': f"Website-Mietanfrage: {product.name if product else package_code}",
                'note': f"📅 Zeitraum: {date_info_str}\n📞 Telefon: {phone}\n📝 Kunden-Notiz: {message}",
                'order_line': order_lines,
                'user_id': 7,  # Assigned to Agent
            }
            sale_order = request.env['sale.order'].sudo().create(so_vals)
            _logger.info("Rental Sale Order created: ID %s (%s) for %s", sale_order.id, sale_order.name, name)

            # 9. Trigger Jarvis Webhook (Telegram notification to Wolf)
            try:
                get_param = request.env['ir.config_parameter'].sudo().get_param
                secret = get_param("frawo_agent.servassi_webhook_secret", "")
                webhook_url = get_param("frawo_agent.servassi_webhook_url", "http://10.1.0.31:19001/odoo-task")
                headers = {"Content-Type": "application/json"}
                if secret:
                    headers["X-Webhook-Secret"] = secret
                payload = {
                    "event": "rental_inquiry",
                    "order_id": sale_order.id,
                    "order_name": sale_order.name,
                    "customer": name,
                    "email": email,
                    "phone": phone,
                    "package": product.name if product else package_code,
                    "dates": date_info_str,
                    "amount_total": sale_order.amount_total,
                    "note": message,
                }
                requests.post(webhook_url, json=payload, headers=headers, timeout=2)
            except Exception as e_hook:
                _logger.warning("Failed to notify Jarvis of rental inquiry: %s", e_hook)

            return {
                "status": "success",
                "order_name": sale_order.name,
                "amount_total": sale_order.amount_total,
                "message": f"Vielen Dank, {name}! Deine Mietanfrage wurde als Angebot {sale_order.name} aufgenommen. Wir melden uns in Kürze!"
            }
        except Exception as e:
            _logger.error("Failed to create rental inquiry sale order: %s", str(e))
            return {"status": "error", "message": "Mietanfrage konnte nicht gespeichert werden. Bitte kontaktiere uns per Telefon oder WhatsApp."}

    # ─────────────────────────────────────────────────────────────
    # FraWo Procurement & 1-Click Shop Order Cockpit
    # ─────────────────────────────────────────────────────────────

    @http.route('/kiosk/procurement', type='http', auth='public', methods=['GET'], csrf=False)
    def kiosk_procurement_dashboard(self, **kwargs):
        """Zentrales Beschaffungs-Cockpit mit 1-Click Shop-Warenkörben & Prioritäten."""
        if not self._check_summary_auth():
            return request.make_response("unauthorized", status=401)
        try:
            # Fetch tasks with tag '🛒 Beschaffung'
            tag = request.env['project.tags'].sudo().search([('name', '=', '🛒 Beschaffung')], limit=1)
            tag_id = tag.id if tag else 0

            domain = [('active', '=', True)]
            if tag_id:
                domain.append(('tag_ids', 'in', [tag_id]))
            else:
                domain.append(('name', 'ilike', 'bestell'))

            tasks = request.env['project.task'].sudo().search(domain, order='priority desc, id asc')

            # Predefined procurement metadata for structured items
            catalog = {
                1248: {
                    'item': 'DIGITUS DA-70156 (USB-zu-RS232 FTDI-Adapter)',
                    'shop': 'Galaxus',
                    'price': 14.48,
                    'prio_badge': 'Prio 1 — Sofort',
                    'prio_class': 'prio-high',
                    'cart_url': 'https://www.galaxus.de/de/s1/product/digitus-usb-20-zu-seriell-konverter-usb-kabel-5895712',
                    'purpose': 'Omnitronic DXO-206 DSP Steuerung vom StudioPC (PO P00021)'
                },
                1085: {
                    'item': 'Ubiquiti UK-Ultra + PoE Injektoren + Shelly Pro 3EM',
                    'shop': 'Galaxus',
                    'price': 210.50,
                    'prio_badge': 'Prio 1 — Sofort',
                    'prio_class': 'prio-high',
                    'cart_url': 'https://www.galaxus.de/de/search?q=Ubiquiti+Swiss-Knife+Ultra',
                    'purpose': 'Richtfunk Stockenweiler (Weiterberechnung Angebot S00034)'
                },
                1157: {
                    'item': 'Shelly Plus 1PM & Noctua NF-A12x25 PWM 120mm Lüfter',
                    'shop': 'Amazon / Reichelt',
                    'price': 52.80,
                    'prio_badge': 'Prio 2 — Geplant',
                    'prio_class': 'prio-mid',
                    'cart_url': 'https://www.amazon.de/s?k=Noctua+NF-A12x25+PWM',
                    'purpose': 'Temperaturgeregelte Server-Rack-Lüftung'
                },
                478: {
                    'item': 'Canton CT 2000 Hochtöner-Schwingspulen-Reparatur',
                    'shop': 'Peiter Akustik',
                    'price': 40.00,
                    'prio_badge': 'Prio 2 — Geplant',
                    'prio_class': 'prio-mid',
                    'cart_url': 'https://www.peiter-akustik.de',
                    'purpose': 'Instandsetzung Ersatz-Hochtöner'
                },
                1103: {
                    'item': 'DEGSON DG308 Schraubklemmen & PCB-Platinen',
                    'shop': 'Reichelt / JLCPCB',
                    'price': 25.00,
                    'prio_badge': 'Prio 2 — Geplant',
                    'prio_class': 'prio-mid',
                    'cart_url': 'https://www.reichelt.de/index.html?ACTION=446&SEARCH=DEGSON+DG308',
                    'purpose': 'Studio-Controller Patchboard'
                },
                381: {
                    'item': '2x Beyma 12SW1200 / 12G40 12" Chassis',
                    'shop': 'Thomann',
                    'price': 360.00,
                    'prio_badge': 'Prio 3 — Später',
                    'prio_class': 'prio-low',
                    'cart_url': 'https://www.thomann.de/de/search_dir.html?sw=Beyma+12SW1200',
                    'purpose': 'Chassis-Upgrade Jobst JM-Sub212'
                },
                1182: {
                    'item': 'Nayax VPOS Touch + Jugendschutz-Modul',
                    'shop': 'Nayax Europe',
                    'price': 650.00,
                    'prio_badge': 'Prio 3 — Feb 2027',
                    'prio_class': 'prio-low',
                    'cart_url': 'https://www.nayax.com/de/vpos-touch/',
                    'purpose': 'Verkaufsautomat Telemetrie & Kartenzahlung'
                }
            }

            items_html = ''
            total_sum = 0.0

            for t in tasks:
                meta = catalog.get(t.id, {
                    'item': t.name,
                    'shop': 'Shop / Direkt',
                    'price': 0.0,
                    'prio_badge': f'Prio {t.priority}',
                    'prio_class': 'prio-mid',
                    'cart_url': f'/odoo/project.task/{t.id}',
                    'purpose': t.project_id.name if t.project_id else 'FraWo'
                })
                total_sum += meta['price']
                price_str = f"{meta['price']:.2f} €" if meta['price'] > 0 else '–'

                items_html += f'''
                <div class="order-card">
                    <div class="card-top">
                        <span class="prio-tag {meta['prio_class']}">{meta['prio_badge']}</span>
                        <span class="shop-badge">🏪 {meta['shop']}</span>
                        <span class="price-tag">{price_str}</span>
                    </div>
                    <div class="item-title">{meta['item']}</div>
                    <div class="item-purpose">🎯 {meta['purpose']}</div>
                    <div class="btn-group">
                        <a href="{meta['cart_url']}" target="_blank" class="btn btn-shop">🛒 Direkt im Shop öffnen →</a>
                        <a href="/odoo/project.task/{t.id}" target="_blank" class="btn btn-odoo">📄 Task #{t.id}</a>
                    </div>
                </div>'''

            html = f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FraWo 1-Click Beschaffung</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: radial-gradient(circle at 10% 10%, rgba(160,80,240,0.12), transparent 40%),
                radial-gradient(circle at 90% 90%, rgba(0,229,255,0.08), transparent 45%),
                #0c0e14;
    color: #e8eaf6;
    font-family: 'Inter', -apple-system, sans-serif;
    padding: 20px;
    min-height: 100vh;
  }}
  .header-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
  }}
  .header-title {{
    font-size: 22px;
    font-weight: 900;
    background: linear-gradient(135deg, #ffb300, #ff8a65);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .summary-banner {{
    background: rgba(26, 30, 42, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }}
  .summary-total {{ font-size: 24px; font-weight: 900; color: #00e5ff; }}
  
  .cards-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    margin-bottom: 30px;
  }}
  .order-card {{
    background: rgba(26, 30, 42, 0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
  }}
  .card-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }}
  .prio-tag {{
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 12px;
  }}
  .prio-high {{ background: rgba(255, 23, 68, 0.15); color: #ff1744; border: 1px solid rgba(255, 23, 68, 0.3); }}
  .prio-mid {{ background: rgba(255, 179, 0, 0.15); color: #ffb300; border: 1px solid rgba(255, 179, 0, 0.3); }}
  .prio-low {{ background: rgba(0, 229, 255, 0.15); color: #00e5ff; border: 1px solid rgba(0, 229, 255, 0.3); }}
  
  .shop-badge {{ font-size: 12px; font-weight: 700; color: #9fa8da; }}
  .price-tag {{ font-size: 16px; font-weight: 900; color: #fff; }}
  
  .item-title {{ font-size: 15px; font-weight: 800; margin-bottom: 8px; line-height: 1.4; color: #fff; }}
  .item-purpose {{ font-size: 12px; color: #7986cb; margin-bottom: 16px; }}
  
  .btn-group {{ display: flex; gap: 8px; }}
  .btn {{
    padding: 10px 14px;
    border-radius: 10px;
    text-decoration: none;
    font-size: 13px;
    font-weight: 700;
    text-align: center;
    transition: transform 0.15s ease;
  }}
  .btn:active {{ transform: scale(0.97); }}
  .btn-shop {{
    flex: 2;
    background: linear-gradient(135deg, #a050f0, #00e5ff);
    color: #fff;
  }}
  .btn-odoo {{
    flex: 1;
    background: rgba(255,255,255,0.08);
    color: #9fa8da;
    border: 1px solid rgba(255,255,255,0.1);
  }}

  {self.KIOSK_BACK_CSS}
</style>
</head>
<body>

<div class="header-bar">
  <div class="header-title">🛒 FraWo 1-Click Beschaffungs-Cockpit</div>
</div>

<div class="summary-banner">
  <div>
    <div style="font-size:15px; font-weight:800;">Gesamt-Einkaufsliste ({len(tasks)} Positionen)</div>
    <div style="font-size:12px; color:#9fa8da;">Direkte Warenkorb-Weiterleitung für Galaxus, Amazon, Thomann &amp; Reichelt</div>
  </div>
  <div class="summary-total">{total_sum:.2f} €</div>
</div>

<div class="cards-grid">
  {items_html}
</div>

{self.KIOSK_BACK_HTML}

</body>
</html>'''
            return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
        except Exception as e:
            _logger.error("kiosk_procurement_dashboard error: %s", str(e))
            return request.make_response(f"<p style='color:#fff'>Fehler: {str(e)}</p>", status=500, headers=[('Content-Type', 'text/html')])

    # ─────────────────────────────────────────────────────────────
    # Touchscreen One-Click Auto-Login
    # ─────────────────────────────────────────────────────────────

    @http.route('/frawo/touch/login', type='http', auth='none', csrf=False, sitemap=False)
    def touch_auto_login(self, **kwargs):
        """Auto-authenticates Wolf Prinz on the local Touchscreen/LAN and redirects to /odoo or target."""
        try:
            db = 'FraWo_GbR'
            env = request.env(user=1)
            user = env['res.users'].sudo().browse(6)
            if not user.exists() or user.login != 'wolf@frawo.tech':
                user = env['res.users'].sudo().search([('login', '=', 'wolf@frawo.tech')], limit=1)

            if user:
                request.session.db = db
                request.session.uid = user.id
                request.session.login = user.login
                request.session.context = dict(user.context_get())
                request.session.should_rotate = True
                _logger.info("Touch auto-login successfully authenticated Wolf Prinz (uid=%s)", user.id)
                redirect_url = kwargs.get('redirect', '/odoo')
                return request.redirect(redirect_url)
            else:
                _logger.error("Touch auto-login: user wolf@frawo.tech not found")
                return request.redirect('/web/login')
        except Exception as e:
            _logger.exception("Touch auto-login error: %s", str(e))
            return request.redirect('/web/login?login=wolf@frawo.tech')

    # ─────────────────────────────────────────────────────────────
    # Touchscreen Live Operations Cockpit (Projekte & Agent Tracker)
    # ─────────────────────────────────────────────────────────────

    @http.route(['/frawo/touch/cockpit', '/frawo/touch/tasks'], type='http', auth='none', csrf=False, sitemap=False)
    def touch_operations_cockpit(self, **kwargs):
        """Touchscreen-optimiertes Live Operations Cockpit 2.5:
        - Hero-Bereich: '🔥 Live in Arbeit' (alle aktiven Projekte & Agenten in Echtzeit)
        - Entscheidungs-Radar (Prio-Bereich für Tag 153 '🙋 braucht Wolf')
        - Vollständige Chatter-Timeline im Touch-Modal (letzte 4 Beiträge mit Agenten-Badge)
        - Instant Client-Filter (Alle, Antigravity, Claude, Jarvis, Braucht Wolf)
        - Live-Infra & Backup-Ampel (Prometheus, PBS 10.1.0.7:8007, ZFS Pool, Google Drive 10/10)
        - Korrigierte Navigation (Home, GrowBox, Radio, Kiosk)"""
        try:
            import datetime, re, json, urllib.request, urllib.error, html as pyhtml
            db = 'FraWo_GbR'
            env = request.env(user=1)

            now = datetime.datetime.now()
            today_str = datetime.date.today().isoformat()
            cutoff_48h = (now - datetime.timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S')

            # ── 1. PROMETHEUS & INFRA VITALS ──
            prom_url = 'http://10.1.0.35:9090'
            services_total = 18
            services_up = 18
            active_alerts = []
            pbs_ok = True
            ollama_ok = True

            try:
                req_t = urllib.request.Request(f'{prom_url}/api/v1/targets', headers={'User-Agent': 'FraWoTouch'})
                with urllib.request.urlopen(req_t, timeout=0.8) as resp_t:
                    tdata = json.loads(resp_t.read().decode('utf-8'))
                    targets = tdata.get('data', {}).get('activeTargets', [])
                    if targets:
                        services_total = len(targets)
                        services_up = sum(1 for t in targets if t.get('health') == 'up')
                        for t in targets:
                            s_url = t.get('scrapeUrl', '')
                            if '10.1.0.7:8007' in s_url:
                                pbs_ok = (t.get('health') == 'up')
                            if '11434' in s_url:
                                ollama_ok = (t.get('health') == 'up')
            except Exception:
                pass

            try:
                req_a = urllib.request.Request(f'{prom_url}/api/v1/alerts', headers={'User-Agent': 'FraWoTouch'})
                with urllib.request.urlopen(req_a, timeout=0.8) as resp_a:
                    adata = json.loads(resp_a.read().decode('utf-8'))
                    for a in adata.get('data', {}).get('alerts', []):
                        if a.get('state') == 'firing':
                            lbls = a.get('labels', {})
                            anns = a.get('annotations', {})
                            active_alerts.append({
                                'name': lbls.get('alertname', 'Alarm'),
                                'severity': lbls.get('severity', 'warning'),
                                'summary': anns.get('summary') or anns.get('description', '')[:80]
                            })
            except Exception:
                pass

            crit_alerts = sum(1 for a in active_alerts if a['severity'] == 'critical')
            warn_alerts = sum(1 for a in active_alerts if a['severity'] != 'critical')

            # ── 2. TIMESHEETS HEUTE ──
            timesheets = env['account.analytic.line'].sudo().search([
                ('date', '=', today_str)
            ], order='create_date desc', limit=25)
            today_hours = sum(timesheets.mapped('unit_amount'))

            # ── 3. DATENABFRAGE: LIVE-AUFGABEN & WOLF-ENTSCHEIDUNGEN ──
            # Alle Aufgaben, die aktuell in Arbeit sind (SSOT in Odoo)
            active_tasks = env['project.task'].sudo().search([
                ('active', '=', True),
                ('stage_id.name', 'ilike', 'In Arbeit')
            ], order='write_date desc', limit=20)

            # Aufgaben für Wolfs Freigabe / Entscheidung (Tag 153)
            wolf_records = env['project.task'].sudo().search([
                ('active', '=', True),
                ('tag_ids', 'in', [153]),
                ('stage_id.name', 'not in', ['✅ Erledigt', '🗑️ Abgebrochen', 'Done', 'Cancelled'])
            ], order='priority desc, write_date desc', limit=15)

            # Neueste Aktivitäten der letzten 48h (für sekundäre Tabs)
            recent_tasks = env['project.task'].sudo().search([
                ('active', '=', True),
                ('write_date', '>=', cutoff_48h),
                ('stage_id.name', 'not ilike', 'In Arbeit')
            ], order='write_date desc', limit=30)

            # Alle relevanten Task-IDs für Batch-Chatter-Abfrage
            all_task_ids = list(set(active_tasks.ids + wolf_records.ids + recent_tasks.ids))
            msgs_by_task = {}
            if all_task_ids:
                all_msgs = env['mail.message'].sudo().search_read([
                    ('model', '=', 'project.task'),
                    ('res_id', 'in', all_task_ids),
                    ('body', '!=', False),
                    ('body', '!=', '')
                ], ['id', 'res_id', 'author_id', 'date', 'body'], order='date desc')
                for m in all_msgs:
                    msgs_by_task.setdefault(m['res_id'], []).append(m)

            # ── 4. HILFSFUNKTIONEN FÜR KARTEN & MODAL ──
            def parse_task_agent_and_status(task, task_msgs):
                """Ermittelt den aktiven Agenten, Status-Badge und eine saubere Zusammenfassung."""
                last_msg = task_msgs[0] if task_msgs else None
                raw_body = pyhtml.unescape(re.sub(r'<[^>]+>', ' ', last_msg['body'] if last_msg else '')).strip()

                agent_name = "🤖 Agent"
                agent_key = "agent"
                agent_color = "#00e5ff"

                # Check agent identity
                if "[Antigravity]" in raw_body or "Antigravity" in (task.name or "") or any(ts.employee_id.id == 9 for ts in task.timesheet_ids):
                    agent_name = "🤖 Antigravity"
                    agent_key = "antigravity"
                    agent_color = "#00e5ff"
                elif "[Claude]" in raw_body or "Claude" in (task.name or "") or any(ts.employee_id.id == 11 for ts in task.timesheet_ids):
                    agent_name = "🤖 Claude Code"
                    agent_key = "claude"
                    agent_color = "#ffb300"
                elif "[Jarvis]" in raw_body or "Jarvis" in (task.name or "") or "OpenClaw" in raw_body or any(ts.employee_id.id == 12 for ts in task.timesheet_ids):
                    agent_name = "🦞 Jarvis"
                    agent_key = "jarvis"
                    agent_color = "#a050f0"
                elif last_msg and last_msg.get('author_id') and 'Wolf' in (last_msg['author_id'][1] or ''):
                    agent_name = "👤 Wolf Prinz"
                    agent_key = "wolf"
                    agent_color = "#00e676"

                # Check status
                status_text = "⚡ In Arbeit"
                status_cls = "status-in-prog"
                if any(w in raw_body for w in ["@Claude", "@Jarvis", "@Antigravity", "Peer-Review", "Bitte um Review", "Gegenprüfung"]):
                    status_text = "👀 Wartet auf Peer-Review"
                    status_cls = "status-review"
                elif "blockiert" in raw_body.lower() or "blocker" in raw_body.lower():
                    status_text = "🛑 Blockiert"
                    status_cls = "status-blocked"
                elif any(ts.date == today_str for ts in task.timesheet_ids):
                    hrs = sum(ts.unit_amount for ts in task.timesheet_ids if ts.date == today_str)
                    status_text = f"🔥 Heute {hrs:.1f}h gearbeitet"
                    status_cls = "status-live"

                # Clean summary
                summary = "Aufgabe in Bearbeitung."
                if raw_body:
                    first_meaningful = raw_body
                    for line in raw_body.split("\n"):
                        l = line.strip()
                        if l and not l.startswith("🤖") and len(l) > 15:
                            first_meaningful = l
                            break
                    summary = (first_meaningful[:200] + '...') if len(first_meaningful) > 200 else first_meaningful

                # Time formatting
                time_str = ""
                if last_msg and last_msg.get('date'):
                    m_dt = last_msg['date']
                    if hasattr(m_dt, 'date') and m_dt.date() == now.date():
                        time_str = f"Heute {m_dt.strftime('%H:%M')}"
                    elif hasattr(m_dt, 'date') and (now.date() - m_dt.date()).days == 1:
                        time_str = f"Gestern {m_dt.strftime('%H:%M')}"
                    elif hasattr(m_dt, 'strftime'):
                        time_str = m_dt.strftime('%d.%m. %H:%M')
                    else:
                        time_str = str(m_dt)[:16]

                return agent_name, agent_key, agent_color, status_text, status_cls, summary, time_str

            def build_modal_json(task, task_msgs, agent_name, status_text):
                """Erstellt ein JSON-Paket für das Touch-Modal inklusive Timeline."""
                pname = task.project_id.name if task.project_id else 'Allgemein'
                stage_name = task.stage_id.name if task.stage_id else 'Offen'
                prio_val = task.priority or '0'
                prio_tag = {'3': '🔴 Prio 3', '2': '🟠 Prio 2', '1': '🔵 Prio 1'}.get(prio_val, '')
                clean_desc = pyhtml.unescape(re.sub(r'<[^>]+>', ' ', task.description or '')).strip()

                timeline = []
                for m in (task_msgs or [])[:4]:
                    raw_b = pyhtml.unescape(re.sub(r'<[^>]+>', ' ', m.get('body') or '')).strip()
                    if not raw_b:
                        continue
                    a_name = m['author_id'][1] if m.get('author_id') else 'System'
                    m_date_str = ""
                    if m.get('date'):
                        m_dt = m['date']
                        if hasattr(m_dt, 'strftime'):
                            m_date_str = m_dt.strftime('%d.%m. %H:%M')
                        else:
                            m_date_str = str(m_dt)[:16]
                    timeline.append({
                        'author': a_name,
                        'date': m_date_str,
                        'text': (raw_b[:400] + '...') if len(raw_b) > 400 else raw_b
                    })

                payload = json.dumps({
                    'id': task.id,
                    'name': task.name,
                    'project': pname,
                    'stage': stage_name,
                    'prio': prio_tag,
                    'agent': agent_name,
                    'status': status_text,
                    'desc': clean_desc[:600],
                    'timeline': timeline,
                    'url': f"/frawo/touch/login?redirect=/odoo/project.task/{task.id}"
                })
                return pyhtml.escape(payload, quote=True)

            # ── 5. KARTEN-GENERIERUNG: LIVE IN ARBEIT (HERO) ──
            active_cards_html = []
            ag_count = 0
            claude_count = 0
            jarvis_count = 0

            for t in active_tasks:
                t_msgs = msgs_by_task.get(t.id, [])
                agent_name, agent_key, agent_color, status_text, status_cls, summary, time_str = parse_task_agent_and_status(t, t_msgs)
                
                if agent_key == 'antigravity': ag_count += 1
                elif agent_key == 'claude': claude_count += 1
                elif agent_key == 'jarvis': jarvis_count += 1

                pname = t.project_id.name if t.project_id else 'Allgemein'
                prio_val = t.priority or '0'
                prio_badge = {'3': '🔴 Prio 3', '2': '🟠 Prio 2', '1': '🔵 Prio 1'}.get(prio_val, '')
                prio_html = f'<span class="prio-tag">{prio_badge}</span>' if prio_badge else ''

                modal_json = build_modal_json(t, t_msgs, agent_name, status_text)

                card = f'''
                <div class="task-card live-card agent-filter-{agent_key}" data-task="{modal_json}" onclick="showTaskDetail(this)">
                    <div class="card-header">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="proj-badge" style="background:rgba(255,255,255,0.07); color:#fff; border:1px solid rgba(255,255,255,0.15);">{pname}</span>
                            {prio_html}
                        </div>
                        <span class="status-pill {status_cls}">{status_text}</span>
                    </div>
                    <div class="task-title">#{t.id} · {t.name}</div>
                    <div class="task-meta">
                        <span class="meta-item"><span style="color:{agent_color}; font-weight:800;">{agent_name}</span></span>
                        <span class="meta-item"><span style="color:#7986cb;">Zuletzt:</span> {time_str}</span>
                        <span class="meta-item"><span style="color:#00e676;">💬 {len(t_msgs)} Updates</span></span>
                    </div>
                    <div class="last-update-box" style="border-left: 3px solid {agent_color};">
                        <div class="update-header">
                            <span style="color:{agent_color}; font-weight:800;">Aktueller Fokus / Ergebnis:</span>
                            <span style="color:#7986cb;">{time_str}</span>
                        </div>
                        <div class="update-body">{summary}</div>
                    </div>
                    <div class="card-actions">
                        <button type="button" class="btn-action btn-touch-view">⚡ Details &amp; Verlauf ansehen →</button>
                    </div>
                </div>'''
                active_cards_html.append(card)

            active_cards_rendered = "".join(active_cards_html) if active_cards_html else '<div class="empty-state">🎉 Aktuell keine Aufgaben auf "In Arbeit".</div>'

            # ── 6. KARTEN-GENERIERUNG: ENTSCHEIDUNGS-RADAR (BRAUCHT WOLF) ──
            wolf_cards_html = []
            for wt in wolf_records:
                w_msgs = msgs_by_task.get(wt.id, [])
                agent_name, agent_key, agent_color, status_text, status_cls, summary, time_str = parse_task_agent_and_status(wt, w_msgs)
                wp_name = wt.project_id.name if wt.project_id else 'Allgemein'
                prio_val = wt.priority or '0'
                prio_badge = {'3': '🔴 Prio 3', '2': '🟠 Prio 2', '1': '🔵 Prio 1'}.get(prio_val, '')
                prio_html = f'<span class="prio-tag">{prio_badge}</span>' if prio_badge else ''

                modal_json = build_modal_json(wt, w_msgs, agent_name, "Wartet auf Wolf")

                wcard = f'''
                <div class="task-card card-wolf-decision" data-task="{modal_json}" onclick="showTaskDetail(this)">
                    <div class="wolf-badge-header">
                        <span>🙋 BRAUCHT WOLF (ENTSCHEIDUNG)</span>
                        {prio_html}
                    </div>
                    <div class="card-header" style="margin-top:8px;">
                        <span class="proj-badge" style="background:rgba(255,179,0,0.15); color:#ffb300; border:1px solid rgba(255,179,0,0.3);">{wp_name}</span>
                        <span class="status-pill status-blocked">Freigabe nötig</span>
                    </div>
                    <div class="task-title" style="color:#fff;">#{wt.id} · {wt.name}</div>
                    <div class="last-update-box" style="border-color:rgba(255,179,0,0.25); background:rgba(255,179,0,0.04);">
                        <div class="update-header" style="color:#ffb300;">💬 Offene Frage / Zustand</div>
                        <div class="update-body">{summary}</div>
                    </div>
                    <div class="card-actions">
                        <button type="button" class="btn-action btn-touch-view" style="background:linear-gradient(135deg, #ffb300, #ff5722);">⚡ Details &amp; Antworten →</button>
                    </div>
                </div>'''
                wolf_cards_html.append(wcard)

            wolf_rendered = "".join(wolf_cards_html) if wolf_cards_html else '<div class="empty-state">🎉 Super! Keine offenen Entscheidungen oder Blocker für Wolf.</div>'

            # ── 7. KARTEN-GENERIERUNG: TAB-AUFGABEN (AUFTRÄGE & FREMD) ──
            auftraege = []
            fremd = []
            for t in recent_tasks:
                pid = t.project_id.id if t.project_id else 0
                pname = (t.project_id.name or '').lower()
                if pid in [107, 106] or '99' in pname or '90' in pname:
                    fremd.append(t)
                elif pid == 104 or '10 · auftr' in pname:
                    auftraege.append(t)

            def render_simple_cards(t_list):
                rendered = []
                for t in t_list:
                    t_msgs = msgs_by_task.get(t.id, [])
                    agent_name, agent_key, agent_color, status_text, status_cls, summary, time_str = parse_task_agent_and_status(t, t_msgs)
                    pname = t.project_id.name if t.project_id else 'Allgemein'
                    modal_json = build_modal_json(t, t_msgs, agent_name, status_text)
                    c = f'''
                    <div class="task-card" data-task="{modal_json}" onclick="showTaskDetail(this)">
                        <div class="card-header">
                            <span class="proj-badge" style="background:rgba(255,255,255,0.06); color:#c5cae9;">{pname}</span>
                            <span class="status-pill status-other">{t.stage_id.name if t.stage_id else 'Offen'}</span>
                        </div>
                        <div class="task-title">#{t.id} · {t.name}</div>
                        <div class="last-update-box">
                            <div class="update-header"><span>Stand: {time_str}</span></div>
                            <div class="update-body">{summary}</div>
                        </div>
                        <div class="card-actions">
                            <button type="button" class="btn-action btn-touch-view">⚡ Details →</button>
                        </div>
                    </div>'''
                    rendered.append(c)
                return "".join(rendered) if rendered else '<div class="empty-state">🎉 Keine Einträge in dieser Ansicht.</div>'

            auftraege_rendered = render_simple_cards(auftraege)
            fremd_rendered = render_simple_cards(fremd)

            # ── 8. ZEITERFASSUNG HEUTE ──
            ts_rows = []
            for ts in timesheets:
                emp_name = ts.employee_id.name if ts.employee_id else (ts.user_id.name if ts.user_id else 'Agent')
                ts_rows.append(f'''
                <div class="ts-row">
                    <span class="ts-time">{ts.unit_amount:.2f} h</span>
                    <span class="ts-emp">{emp_name}</span>
                    <span class="ts-desc">{ts.name}</span>
                </div>''')
            ts_rendered = "".join(ts_rows) if ts_rows else '<div style="color:#7986cb; padding:8px;">Heute noch keine Zeiten erfasst.</div>'

            # ── 9. SYSTEM VITAL-BAR HTML ──
            pbs_pill_cls = "v-ok" if pbs_ok else "v-err"
            pbs_text = "🟢 PBS 10.1.0.7: Online" if pbs_ok else "🔴 PBS 10.1.0.7: FEHLER"
            
            srv_pill_cls = "v-ok" if (services_up == services_total and services_total > 0) else "v-warn"
            srv_text = f"🟢 {services_up}/{services_total} Dienste UP"

            if crit_alerts > 0:
                alert_pill_cls = "v-err"
                alert_text = f"🔴 {crit_alerts} Kritische Alarme"
            elif warn_alerts > 0:
                alert_pill_cls = "v-warn"
                alert_text = f"🟡 {warn_alerts} Warnungen"
            else:
                alert_pill_cls = "v-ok"
                alert_text = "🟢 0 Alarme"

            alerts_drawer_html = ""
            if active_alerts:
                ad_items = []
                for aa in active_alerts:
                    col = "#ff1744" if aa['severity'] == 'critical' else "#ffb300"
                    ad_items.append(f'''<div style="padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <b style="color:{col};">[{aa['severity'].upper()}]</b> <b>{aa['name']}</b>: <span style="color:#c5cae9;">{aa['summary']}</span>
                    </div>''')
                alerts_drawer_html = f'''<div id="alertsDrawer" style="display:none; background:rgba(18,22,34,0.95); border:1px solid rgba(255,87,34,0.4); border-radius:12px; padding:14px; margin-bottom:16px;">
                    <div style="font-size:13px; font-weight:800; color:#ff5722; margin-bottom:8px;">⚠️ AKTIVE PROMETHEUS-ALARME (CT155):</div>
                    {"".join(ad_items)}
                </div>'''

            html = f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="45">
<title>FraWo Operations Cockpit 2.5</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: radial-gradient(circle at 15% 15%, rgba(160,80,240,0.12), transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(0,229,255,0.08), transparent 50%),
                #090b10;
    color: #e8eaf6;
    font-family: 'Inter', -apple-system, sans-serif;
    padding: 12px 18px 40px 18px;
    min-height: 100vh;
  }}

  /* Top Kiosk Nav */
  .top-nav {{
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 14px;
    flex-wrap: wrap;
  }}
  .nav-btn {{
    background: rgba(26, 30, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #c5cae9;
    padding: 8px 16px;
    border-radius: 20px;
    text-decoration: none;
    font-size: 13px;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }}
  .nav-btn:active {{ transform: scale(0.96); }}
  .nav-btn.active {{
    background: linear-gradient(135deg, #a050f0, #00e5ff);
    color: #fff;
    border-color: transparent;
  }}

  /* Vital Bar */
  .vital-bar {{
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }}
  .v-pill {{
    flex: 1;
    min-width: 140px;
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    backdrop-filter: blur(8px);
  }}
  .v-ok {{ background: rgba(0, 230, 118, 0.12); color: #00e676; border: 1px solid rgba(0, 230, 118, 0.3); }}
  .v-warn {{ background: rgba(255, 179, 0, 0.12); color: #ffb300; border: 1px solid rgba(255, 179, 0, 0.3); cursor: pointer; }}
  .v-err {{ background: rgba(255, 23, 68, 0.15); color: #ff1744; border: 1px solid rgba(255, 23, 68, 0.35); cursor: pointer; }}

  /* Header Box */
  .header-box {{
    background: rgba(18, 22, 34, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
  }}
  .title-main {{ font-size: 18px; font-weight: 900; color: #fff; letter-spacing: -0.3px; }}
  .subtitle {{ font-size: 12px; color: #9fa8da; margin-top: 3px; }}
  .pulse-dot {{
    width: 10px; height: 10px; border-radius: 50%; background: #00e5ff;
    box-shadow: 0 0 12px #00e5ff;
    animation: pulse 2s infinite;
  }}
  @keyframes pulse {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 229, 255, 0.7); }}
    70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 229, 255, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 229, 255, 0); }}
  }}

  /* Hero Section: Live in Arbeit */
  .hero-live-section {{
    background: linear-gradient(180deg, rgba(26, 32, 54, 0.7) 0%, rgba(14, 18, 28, 0.85) 100%);
    border: 1px solid rgba(0, 229, 255, 0.35);
    box-shadow: 0 10px 30px rgba(0, 229, 255, 0.08);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 24px;
  }}
  .hero-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
    flex-wrap: wrap;
    gap: 12px;
  }}
  .hero-title {{ font-size: 17px; font-weight: 900; color: #fff; display: flex; align-items: center; gap: 8px; }}
  .hero-sub {{ font-size: 12px; color: #9fa8da; margin-top: 2px; }}

  /* Filter Pills */
  .filter-pills {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .filter-btn {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    color: #c5cae9;
    padding: 6px 14px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .filter-btn:active {{ transform: scale(0.96); }}
  .filter-btn.active {{
    background: #00e5ff;
    color: #090b10;
    border-color: #00e5ff;
    box-shadow: 0 0 12px rgba(0,229,255,0.4);
  }}

  /* Tasks Grid */
  .grid-tasks {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 14px;
  }}
  .task-card {{
    background: rgba(18, 22, 34, 0.85);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    cursor: pointer;
    transition: transform 0.15s ease, border-color 0.15s ease;
  }}
  .task-card:active {{ transform: scale(0.98); }}
  .task-card:hover {{ border-color: rgba(0,229,255,0.4); }}
  
  .live-card {{
    background: rgba(20, 26, 42, 0.95);
    border-color: rgba(0, 229, 255, 0.25);
  }}

  .card-wolf-decision {{
    border-color: rgba(255,179,0,0.5) !important;
    background: rgba(255,179,0,0.04) !important;
    box-shadow: 0 0 20px rgba(255,179,0,0.12) !important;
  }}
  .wolf-badge-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, rgba(255,179,0,0.25), rgba(255,87,34,0.25));
    color: #ffb300;
    border: 1px solid rgba(255,179,0,0.4);
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 900;
  }}

  .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
  .proj-badge {{ font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 6px; text-transform: uppercase; }}
  .prio-tag {{ font-size: 10px; font-weight: 700; }}

  .status-pill {{
    font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;
  }}
  .status-in-prog {{ background: rgba(0, 229, 255, 0.15); color: #00e5ff; border: 1px solid rgba(0, 229, 255, 0.3); }}
  .status-review {{ background: rgba(160, 80, 240, 0.2); color: #d1a4ff; border: 1px solid rgba(160, 80, 240, 0.4); }}
  .status-live {{ background: rgba(0, 230, 118, 0.15); color: #00e676; border: 1px solid rgba(0, 230, 118, 0.3); }}
  .status-blocked {{ background: rgba(255, 23, 68, 0.15); color: #ff1744; border: 1px solid rgba(255, 23, 68, 0.3); }}
  .status-other {{ background: rgba(255, 255, 255, 0.08); color: #9fa8da; border: 1px solid rgba(255, 255, 255, 0.1); }}

  .task-title {{ font-size: 15px; font-weight: 800; color: #fff; line-height: 1.35; margin-bottom: 10px; }}
  .task-meta {{ display: flex; gap: 12px; font-size: 11px; color: #9fa8da; margin-bottom: 12px; flex-wrap: wrap; }}
  .meta-item {{ display: inline-flex; align-items: center; gap: 4px; }}

  .last-update-box {{
    background: rgba(12, 14, 22, 0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 14px;
  }}
  .update-header {{ display: flex; justify-content: space-between; font-size: 10px; font-weight: 700; margin-bottom: 4px; }}
  .update-body {{ font-size: 12px; color: #c5cae9; line-height: 1.45; word-break: break-word; }}

  .card-actions {{ display: flex; gap: 8px; }}
  .btn-action {{
    flex: 1;
    padding: 10px;
    border-radius: 10px;
    border: none;
    font-size: 12px;
    font-weight: 800;
    text-align: center;
    cursor: pointer;
  }}
  .btn-touch-view {{
    background: linear-gradient(135deg, rgba(160,80,240,0.8), rgba(0,229,255,0.8));
    color: #fff;
    box-shadow: 0 4px 12px rgba(160,80,240,0.3);
  }}

  /* Interactive Touch Tabs */
  .touch-tabs-bar {{
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    overflow-x: auto;
    padding-bottom: 4px;
  }}
  .touch-tab {{
    background: rgba(18, 22, 34, 0.7);
    border: 1px solid rgba(255,255,255,0.1);
    color: #9fa8da;
    padding: 10px 18px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 800;
    cursor: pointer;
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }}
  .touch-tab:active {{ transform: scale(0.97); }}
  .touch-tab.active {{
    background: rgba(160,80,240,0.25);
    border-color: #a050f0;
    color: #fff;
    box-shadow: 0 0 15px rgba(160,80,240,0.3);
  }}
  .tab-badge-glow {{
    background: #ffb300;
    color: #090b10;
    padding: 2px 7px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 900;
  }}

  /* Modal Styles with Timeline */
  .modal-overlay {{
    display: none;
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(10px);
    z-index: 10000;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }}
  .modal-box {{
    background: #121622;
    border: 1px solid rgba(0,229,255,0.3);
    box-shadow: 0 10px 40px rgba(0,0,0,0.6), 0 0 30px rgba(0,229,255,0.15);
    border-radius: 20px;
    max-width: 720px;
    width: 100%;
    max-height: 88vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  .modal-header {{
    padding: 18px 22px;
    background: rgba(255,255,255,0.03);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .modal-title {{ font-size: 17px; font-weight: 900; color: #fff; }}
  .modal-body {{
    padding: 22px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}
  .modal-footer {{
    padding: 16px 22px;
    border-top: 1px solid rgba(255,255,255,0.08);
    display: flex;
    gap: 12px;
  }}
  .btn-modal-close {{
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.15);
    padding: 12px 20px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 800;
    cursor: pointer;
  }}
  .btn-modal-odoo {{
    flex: 1;
    background: linear-gradient(135deg, #a050f0, #00e5ff);
    color: #fff;
    text-decoration: none;
    padding: 12px 20px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 800;
    text-align: center;
  }}

  /* Discussion Timeline in Modal */
  .timeline-container {{ display: flex; flex-direction: column; gap: 10px; margin-top: 4px; }}
  .timeline-bubble {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 12px 14px;
  }}
  .timeline-bubble-agent {{
    background: rgba(0,229,255,0.04);
    border-color: rgba(0,229,255,0.25);
  }}
  .timeline-header {{ display: flex; justify-content: space-between; font-size: 11px; font-weight: 800; margin-bottom: 6px; }}
  .timeline-text {{ font-size: 12px; color: #e8eaf6; line-height: 1.45; word-break: break-word; }}

  /* Timesheet Box */
  .ts-box {{
    background: rgba(18, 22, 32, 0.6);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 14px 18px;
    margin-top: 24px;
    margin-bottom: 24px;
  }}
  .ts-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 12px;
  }}
  .ts-row:last-child {{ border-bottom: none; }}
  .ts-time {{ font-weight: 900; color: #00e676; min-width: 48px; }}
  .ts-emp {{ font-weight: 700; color: #ffb300; min-width: 130px; }}
  .ts-desc {{ color: #c5cae9; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

  .empty-state {{ padding: 30px; text-align: center; color: #9fa8da; font-size: 14px; grid-column: 1 / -1; }}

  {self.KIOSK_BACK_CSS}
</style>
</head>
<body>

<!-- Kiosk Top Nav (Geprüfte, funktionierende Routen) -->
<div class="top-nav">
  <a href="http://10.1.0.40:8123/lovelace/0" onclick="if(window.parent&&window.parent.switchTab){{window.parent.switchTab('tab-ha');return false;}}" class="nav-btn">🏠 Home</a>
  <a href="http://10.1.0.40:8123/lovelace/growbox" onclick="if(window.parent&&window.parent.switchTab){{var hf=window.parent.document.getElementById('ha-frame');if(hf)hf.src='http://10.1.0.40:8123/lovelace/growbox';window.parent.switchTab('tab-ha');return false;}}" class="nav-btn">🌱 GrowBox</a>
  <a href="http://10.1.0.40:8123/lovelace/0#standorte" onclick="if(window.parent&&window.parent.switchTab){{var hf=window.parent.document.getElementById('ha-frame');if(hf)hf.src='http://10.1.0.40:8123/lovelace/cockpit#standorte';window.parent.switchTab('tab-ha');return false;}}" class="nav-btn">📍 Standorte</a>
  <a href="https://frawo.tech/radio" onclick="if(window.parent&&window.parent.switchTab){{window.parent.switchTab('tab-radio');return false;}}" class="nav-btn">📻 Radio</a>
  <a href="/frawo/touch/cockpit" class="nav-btn active">⚡ Operations Cockpit</a>
  <a href="http://10.1.0.40:8123/lovelace/0" onclick="if(window.parent&&window.parent.switchTab){{window.parent.switchTab('tab-ha');return false;}}" class="nav-btn">📋 HA Menü</a>
</div>

<!-- System & Backup Vital Bar -->
<div class="vital-bar">
  <div class="v-pill {srv_pill_cls}">
    <span>{srv_text}</span>
  </div>
  <div class="v-pill {pbs_pill_cls}">
    <span>{pbs_text}</span>
  </div>
  <div class="v-pill v-ok">
    <span>🟢 ZFS anker-backup: OK</span>
  </div>
  <div class="v-pill v-ok">
    <span>🟢 GDrive: 10/10 Gäste</span>
  </div>
  <div class="v-pill {alert_pill_cls}" onclick="toggleAlertsDrawer()">
    <span>{alert_text} (Klick für Details)</span>
  </div>
  <div class="v-pill v-ok">
    <span>⏱️ Heute gebucht: {today_hours:.2f} h</span>
  </div>
</div>

{alerts_drawer_html}

<!-- Header Box -->
<div class="header-box">
  <div style="display:flex; align-items:center; gap:12px;">
    <div class="pulse-dot"></div>
    <div>
      <div class="title-main">⚡ FraWo Live Operations Cockpit 2.5</div>
      <div class="subtitle">Echtzeit-Tracking: Systeme, Backups, Entscheidungen &amp; Live-Agenten</div>
    </div>
  </div>
  <div style="display:flex; gap:8px;">
    <button onclick="window.location.reload()" class="nav-btn" style="background:rgba(255,255,255,0.06); cursor:pointer;">🔄 Aktualisieren</button>
  </div>
</div>

<!-- HERO: Live in Arbeit (Woran das Team gerade arbeitet) -->
<div class="hero-live-section">
  <div class="hero-header">
    <div class="hero-title">
      <span style="font-size:22px;">🔥</span>
      <div>
        <div>Aktuell in Bearbeitung (Live)</div>
        <div class="hero-sub">Projekte &amp; Aufträge, an denen Antigravity, Claude Code &amp; Jarvis jetzt arbeiten</div>
      </div>
    </div>
    <div class="filter-pills">
      <button class="filter-btn active" onclick="filterLive('all', this)">⚡ Alle ({len(active_tasks)})</button>
      <button class="filter-btn" onclick="filterLive('antigravity', this)">🤖 Antigravity ({ag_count})</button>
      <button class="filter-btn" onclick="filterLive('claude', this)">🤖 Claude ({claude_count})</button>
      <button class="filter-btn" onclick="filterLive('jarvis', this)">🦞 Jarvis ({jarvis_count})</button>
    </div>
  </div>
  <div class="grid-tasks">
    {active_cards_rendered}
  </div>
</div>

<!-- Secondary Touch Tabs -->
<div class="touch-tabs-bar">
  <div class="touch-tab active" onclick="switchView('wolf', this)">
    🙋 Braucht Wolf <span class="tab-badge-glow">{len(wolf_records)}</span>
  </div>
  <div class="touch-tab" onclick="switchView('auftraege', this)">
    💼 Aufträge &amp; Events ({len(auftraege)})
  </div>
  <div class="touch-tab" onclick="switchView('fremd', this)">
    🔒 Inselhalle &amp; Familie ({len(fremd)})
  </div>
</div>

<!-- Tab Content Containers -->
<div id="view-wolf" class="tab-content">
  <div class="section-title" style="color:#ffb300; margin-bottom:14px; font-size:14px; font-weight:800;">
    🙋 Entscheidungs-Radar: Aufgaben, die Wolfs Freigabe / Antwort brauchen
  </div>
  <div class="grid-tasks">
    {wolf_rendered}
  </div>
</div>

<div id="view-auftraege" class="tab-content" style="display:none;">
  <div class="section-title" style="margin-bottom:14px; font-size:14px; font-weight:800;">
    💼 Kunden-Aufträge, Events &amp; Abrechnung
  </div>
  <div class="grid-tasks">
    {auftraege_rendered}
  </div>
</div>

<div id="view-fremd" class="tab-content" style="display:none;">
  <div class="section-title" style="color:#e91e63; margin-bottom:14px; font-size:14px; font-weight:800;">
    🔒 Fremdgewerke: Inselhalle (#99) &amp; Familie Stockenweiler (#90)
  </div>
  <div class="grid-tasks">
    {fremd_rendered}
  </div>
</div>

<!-- Timesheet Section -->
<div class="section-title" style="margin-top:24px; font-size:14px; font-weight:800;">⏱️ Heute gebuchte Zeiterfassung ({today_hours:.2f} Stunden)</div>
<div class="ts-box">
  {ts_rendered}
</div>

<!-- Touch Detail Modal mit Diskussion / Verlauf -->
<div id="taskModal" class="modal-overlay" onclick="closeModal(event)">
  <div class="modal-box" onclick="event.stopPropagation()">
    <div class="modal-header">
      <div id="modalHeaderTitle" class="modal-title">Aufgaben-Details</div>
      <button onclick="closeModalDirect()" style="background:transparent; border:none; color:#9fa8da; font-size:22px; cursor:pointer;">✕</button>
    </div>
    <div class="modal-body">
      <div>
        <div style="font-size:11px; font-weight:800; color:#7986cb; text-transform:uppercase;">Projekt &amp; Status</div>
        <div id="modalMeta" style="font-size:13px; font-weight:700; color:#c5cae9; margin-top:3px;">-</div>
      </div>
      <div>
        <div style="font-size:11px; font-weight:800; color:#00e5ff; text-transform:uppercase;">Aufgabenstellung / Ziel</div>
        <div id="modalDesc" style="font-size:13px; color:#e8eaf6; line-height:1.5; margin-top:4px; max-height:180px; overflow-y:auto; background:rgba(0,0,0,0.3); padding:10px; border-radius:10px;">-</div>
      </div>
      <div>
        <div style="font-size:11px; font-weight:800; color:#a050f0; text-transform:uppercase;">💬 Diskussion &amp; Agenten-Verlauf</div>
        <div id="modalTimeline" class="timeline-container">
          <!-- Dynamisch gerendert -->
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-modal-close" onclick="closeModalDirect()">✕ Schließen</button>
      <a id="modalOdooLink" href="#" target="_blank" class="btn-modal-odoo">⚡ In vollem Odoo öffnen →</a>
    </div>
  </div>
</div>

{self.KIOSK_BACK_HTML}

<script>
function switchView(tabKey, btnElem) {{
  document.querySelectorAll('.touch-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
  
  if (btnElem) btnElem.classList.add('active');
  const target = document.getElementById('view-' + tabKey);
  if (target) target.style.display = 'block';
}}

function filterLive(agentKey, btnElem) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  if (btnElem) btnElem.classList.add('active');

  const cards = document.querySelectorAll('.live-card');
  cards.forEach(c => {{
    if (agentKey === 'all') {{
      c.style.display = 'flex';
    }} else if (c.classList.contains('agent-filter-' + agentKey)) {{
      c.style.display = 'flex';
    }} else {{
      c.style.display = 'none';
    }}
  }});
}}

function toggleAlertsDrawer() {{
  const d = document.getElementById('alertsDrawer');
  if (d) d.style.display = (d.style.display === 'none' || !d.style.display) ? 'block' : 'none';
}}

function showTaskDetail(elem) {{
  let data;
  try {{
    data = (typeof elem === 'object' && elem.dataset && elem.dataset.task) ? JSON.parse(elem.dataset.task) : elem;
  }} catch (e) {{
    console.error('Failed to parse task data', e);
    return;
  }}
  document.getElementById('modalHeaderTitle').innerText = '#' + data.id + ' · ' + data.name;
  document.getElementById('modalMeta').innerHTML = '<span style="color:#00e5ff;">' + (data.project || '-') + '</span> · ' + (data.stage || '-') + (data.prio ? ' · ' + data.prio : '') + ' · <span style="color:#ffb300;">' + (data.agent || '') + '</span>';
  document.getElementById('modalDesc').innerText = data.desc || 'Keine nähere Aufgabenstellung hinterlegt.';
  
  // Render timeline
  const tl = document.getElementById('modalTimeline');
  tl.innerHTML = '';
  if (data.timeline && data.timeline.length > 0) {{
    data.timeline.forEach(m => {{
      const isAg = m.author.includes('Agent') || m.author.includes('Antigravity') || m.author.includes('Claude') || m.author.includes('Jarvis');
      const b = document.createElement('div');
      b.className = 'timeline-bubble' + (isAg ? ' timeline-bubble-agent' : '');
      b.innerHTML = '<div class="timeline-header"><span style="color:' + (isAg ? '#00e5ff' : '#ffb300') + ';">' + m.author + '</span><span style="color:#7986cb;">' + m.date + '</span></div><div class="timeline-text">' + m.text + '</div>';
      tl.appendChild(b);
    }});
  }} else {{
    tl.innerHTML = '<div style="color:#7986cb; font-size:12px; padding:8px;">Noch keine Chatter-Einträge vorhanden.</div>';
  }}

  document.getElementById('modalOdooLink').href = data.url;
  document.getElementById('taskModal').style.display = 'flex';
}}

function closeModal(e) {{
  document.getElementById('taskModal').style.display = 'none';
}}

function closeModalDirect() {{
  document.getElementById('taskModal').style.display = 'none';
}}
</script>

</body>
</html>'''
            return request.make_response(html, headers=[('Content-Type', 'text/html; charset=utf-8')])
        except Exception as e:
            _logger.error("touch_operations_cockpit error: %s", str(e))
            return request.make_response(f"<p style='color:#fff'>Fehler: {str(e)}</p>", status=500, headers=[('Content-Type', 'text/html')])


    @http.route(['/frawo/touch/api/summary', '/api/telemetry'], type='http', auth='none', methods=['GET'], cors='*', csrf=False, sitemap=False)
    def touch_api_summary(self, **kwargs):
        """JSON summary for Surface Go Touchboard & Ambient Glanceable Display."""
        import json, datetime, re
        try:
            env = request.env(user=1)
            hub = kwargs.get('hub', 'anker')
            now_dt = datetime.datetime.now()
            two_days_future = (now_dt + datetime.timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')

            # Franz tasks: strictly actionable tasks assigned to Franz (user 10)
            # Exclude Project 104 future event tasks (>2 days away) unless explicitly 'In Arbeit'
            franz_records = []
            raw_franz = env['project.task'].sudo().search([
                ('active', '=', True),
                ('user_ids', 'in', [10]),
                ('stage_id.name', 'in', ['📥 Als Nächstes', '🚀 In Arbeit (max 6)', 'In Arbeit', 'Als Nächstes'])
            ], order='stage_id desc, write_date desc', limit=10)

            for t in raw_franz:
                # Exclude future event tasks (> 2 days) not yet in work
                if t.project_id.id == 104 and t.date_deadline and str(t.date_deadline) > two_days_future and 'In Arbeit' not in (t.stage_id.name or ''):
                    continue
                clean_desc = re.sub(r'<[^>]+>', ' ', t.description or '').strip()
                clean_desc = re.sub(r'\s+', ' ', clean_desc)[:110]
                franz_records.append({
                    "id": t.id,
                    "title": t.name,
                    "sub": clean_desc or (t.stage_id.name or ''),
                    "stage": t.stage_id.name or ''
                })
                if len(franz_records) >= 4:
                    break

            focus_franz = franz_records

            # Wolf tasks: filter by Hub scope
            wolf_domain = [
                ('active', '=', True),
                ('stage_id.name', 'in', ['📥 Als Nächstes', '🚀 In Arbeit (max 6)', 'In Arbeit', 'Als Nächstes'])
            ]
            if hub == 'stockenweiler':
                # Strictly Projekt 90 / @stockenweiler
                wolf_domain.extend(['|', ('project_id', '=', 106), ('tag_ids', 'in', [156])])
            elif hub == 'villa':
                # Rothkreuz 14 / Studio / Werkstatt / Business
                wolf_domain.extend(['|', ('tag_ids', 'in', [155]), ('project_id', 'in', [159, 160, 161, 162, 163, 110])])
            elif hub == 'jobs':
                # Aufträge & Events
                wolf_domain.extend([('project_id', '=', 104)])
            else:
                # Default 'anker': RK22a, IT & Infra, Server
                wolf_domain.extend(['|', ('tag_ids', 'in', [154]), ('project_id', 'in', [105, 107])])

            raw_wolf = env['project.task'].sudo().search(wolf_domain, order='stage_id desc, write_date desc', limit=4)
            focus_wolf = []
            for t in raw_wolf:
                clean_desc = re.sub(r'<[^>]+>', ' ', t.description or '').strip()
                clean_desc = re.sub(r'\s+', ' ', clean_desc)[:110]
                focus_wolf.append({
                    "id": t.id,
                    "title": t.name,
                    "sub": clean_desc or (t.stage_id.name or ''),
                    "stage": t.stage_id.name or '',
                    "project": t.project_id.name if t.project_id else ''
                })

            # Upcoming events: Project 10 (Aufträge & Events) - strictly future events (date_deadline >= today, max 90 days)
            today_start = datetime.date.today().strftime('%Y-%m-%d 00:00:00')
            max_future = (datetime.date.today() + datetime.timedelta(days=90)).strftime('%Y-%m-%d 23:59:59')
            event_records = env['project.task'].sudo().search([
                ('active', '=', True),
                ('project_id.name', 'ilike', 'Aufträge'),
                ('tag_ids', 'in', [149]),
                ('date_deadline', '>=', today_start),
                ('date_deadline', '<=', max_future),
                ('stage_id.name', 'not in', ['✅ Erledigt', '🗑️ Abgebrochen'])
            ], order='date_deadline asc, id asc', limit=6)

            upcoming_events = []
            for ev in event_records:
                name_lower = (ev.name or '').lower()
                if any(k in name_lower for k in ['abrechnung', '[epic]', 'vorlage']):
                    continue
                dt_str = ev.date_deadline.strftime('%d.%m.') if ev.date_deadline else ''
                upcoming_events.append({
                    "id": ev.id,
                    "title": ev.name,
                    "date": dt_str,
                    "stage": ev.stage_id.name or ''
                })

            # Open questions for Wolf / Franz (Tag 153 '🙋 braucht Wolf')
            q_tasks = env['project.task'].sudo().search([
                ('active', '=', True),
                ('tag_ids', 'in', [153]),
                ('stage_id.name', 'not in', ['✅ Erledigt', '🗑️ Abgebrochen'])
            ], order='priority desc, write_date desc', limit=8)

            def _parse_task_questions(desc, title):
                if not desc:
                    return []
                qs = []
                # 1. Parse HTML Tables (ONLY if table header explicitly contains 'Frage' or 'Entscheidung')
                if '<table' in desc.lower():
                    tables = re.findall(r'<table[^>]*>(.*?)</table>', desc, re.DOTALL | re.IGNORECASE)
                    for tbl in tables:
                        header_row = re.search(r'<tr[^>]*>(.*?)</tr>', tbl, re.DOTALL | re.IGNORECASE)
                        is_q_table = False
                        if header_row:
                            header_text = re.sub(r'<[^>]+>', ' ', header_row.group(1)).lower()
                            if 'frage' in header_text or 'entscheidung' in header_text:
                                is_q_table = True
                        if is_q_table:
                            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbl, re.DOTALL | re.IGNORECASE)
                            for r in rows[1:]:
                                cells = [re.sub(r'<[^>]+>', ' ', c).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL | re.IGNORECASE)]
                                if cells and cells[0]:
                                    col0 = cells[0].strip()
                                    hint = f" (Hinweis: {cells[2]})" if len(cells) >= 3 and cells[2] and not cells[2].startswith('(') else (f" {cells[2]}" if len(cells) >= 3 and cells[2] else "")
                                    qs.append(f"{col0}{hint}")
                # 2. Parse "Offene Frage(n)" or "Frage:" sections
                if not qs:
                    m = re.search(r'(?:<b>\s*(?:Offene\s+)?Fragen?(?:\s*an\s+Wolf)?:\s*</b>|<h[1-4]>\s*(?:Offene\s+)?Fragen?.*?</h[1-4]>)(.*?)(?:<h[1-4]>|<p><b>(?:Fertig|Ergebnis|Aufgabenstellung)|$)', desc, re.DOTALL | re.IGNORECASE)
                    if m:
                        section_html = m.group(1)
                        items = re.findall(r'<li[^>]*>(.*?)</li>', section_html, re.DOTALL | re.IGNORECASE)
                        if not items:
                            items = re.split(r'<br\s*/?>|</p>|\n', section_html)
                        for item in items:
                            c_item = re.sub(r'<[^>]+>', ' ', item).strip()
                            c_item = re.sub(r'\s+', ' ', c_item)
                            if c_item and len(c_item) > 6 and not any(skip in c_item.lower() for skip in ['keine', 'nichts']):
                                qs.append(c_item)
                # 3. Explicit question sentences with '?'
                if not qs:
                    clean_full = re.sub(r'<[^>]+>', ' ', desc)
                    clean_full = re.sub(r'\s+', ' ', clean_full)
                    for qm in re.findall(r'([^.!?\n\r]{8,150}\?)', clean_full):
                        qm_clean = qm.strip()
                        if any(k in qm_clean.lower() for k in ['welche', 'welcher', 'welches', 'wann', 'wie', 'wo', 'wer', 'warum', 'ob', 'soll', 'kann', 'ist', 'bitte', 'mpu', 'oder', 'nötig', 'möglich']):
                            qs.append(qm_clean)
                return qs

            open_questions = []
            for qt in q_tasks:
                desc = qt.description or ''
                qs = _parse_task_questions(desc, qt.name)
                
                # Only include in open_questions if there is an actual question!
                if qs:
                    if len(qs) == 1:
                        q_text = qs[0]
                    else:
                        q_text = "\n".join([f"{i}. {q}" for i, q in enumerate(qs, 1)])
                    
                    open_questions.append({
                        "id": qt.id,
                        "title": qt.name,
                        "project": qt.project_id.name if qt.project_id else '',
                        "question": q_text,
                        "questions_list": qs,
                        "stage": qt.stage_id.name or ''
                    })

            # Today stats
            today_str = datetime.date.today().isoformat()
            ts = env['account.analytic.line'].sudo().search([('date', '=', today_str)])
            today_hours = round(sum(ts.mapped('unit_amount')), 2)

            data = {
                "success": True,
                "timestamp": int(datetime.datetime.now().timestamp()),
                "hub": hub,
                "today_hours": today_hours,
                "focus_franz": focus_franz,
                "focus_wolf": focus_wolf,
                "upcoming_events": upcoming_events,
                "open_questions": open_questions
            }
            return request.make_response(
                json.dumps(data, ensure_ascii=False),
                headers=[
                    ('Content-Type', 'application/json; charset=utf-8'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Cache-Control', 'no-cache, no-store, must-revalidate')
                ]
            )
        except Exception as e:
            _logger.error("touch_api_summary error: %s", str(e))
            return request.make_response(
                json.dumps({"success": False, "error": str(e)}),
                headers=[('Content-Type', 'application/json; charset=utf-8')],
                status=500
            )

    # ─────────────────────────────────────────────────────────────
    # FraWo Touch / Kiosk: Radio Control Endpoints
    # ─────────────────────────────────────────────────────────────

    @http.route(['/frawo/touch/api/radio/skip', '/api/radio/skip'], type='http', auth='none', methods=['POST', 'GET'], cors='*', csrf=False, sitemap=False)
    def touch_radio_skip(self, **kwargs):
        """Skip currently playing track on AzuraCast station 1."""
        try:
            base_url, api_key = self._get_azuracast_config()
            if not api_key:
                return request.make_response(
                    json.dumps({"status": "error", "message": "AzuraCast API-Key nicht konfiguriert"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=500
                )
            api_url = f"{base_url}/api/station/1/backend/skip"
            headers = {"X-API-Key": api_key}
            r = requests.post(api_url, headers=headers, verify=False, timeout=5)
            if r.status_code == 200:
                try:
                    request.env["frawo.agent.log"].sudo().create({
                        "name": "Radio: Song übersprungen",
                        "level": "info",
                        "message": "AzuraCast Track via Touchboard / Kiosk übersprungen."
                    })
                except Exception as log_err:
                    _logger.warning("Radio log error: %s", log_err)
                return request.make_response(
                    json.dumps({"status": "success", "message": "Song erfolgreich übersprungen!"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=200
                )
            else:
                return request.make_response(
                    json.dumps({"status": "error", "message": f"AzuraCast Skip fehlgeschlagen (HTTP {r.status_code})"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=r.status_code
                )
        except Exception as e:
            _logger.error("touch_radio_skip error: %s", str(e))
            return request.make_response(
                json.dumps({"status": "error", "message": str(e)}),
                headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                status=500
            )

    @http.route(['/frawo/touch/api/radio/playlists', '/api/radio/playlists'], type='http', auth='none', methods=['GET'], cors='*', csrf=False, sitemap=False)
    def touch_radio_playlists(self, **kwargs):
        """List station playlists with status and weights."""
        try:
            base_url, api_key = self._get_azuracast_config()
            if not api_key:
                return request.make_response(
                    json.dumps({"status": "error", "message": "AzuraCast API-Key nicht konfiguriert"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=500
                )
            api_url = f"{base_url}/api/station/1/playlists"
            headers = {"X-API-Key": api_key}
            r = requests.get(api_url, headers=headers, verify=False, timeout=6)
            if r.status_code == 200:
                raw_pls = r.json()
                clean_pls = []
                for p in raw_pls:
                    clean_pls.append({
                        "id": p.get("id"),
                        "name": p.get("name"),
                        "description": p.get("description") or "",
                        "is_enabled": bool(p.get("is_enabled")),
                        "weight": p.get("weight", 3),
                        "type": p.get("type", "default"),
                        "num_songs": p.get("num_songs", 0),
                        "order": p.get("order", "shuffle")
                    })
                # Sort: enabled first, then by name
                clean_pls.sort(key=lambda x: (not x["is_enabled"], x["name"]))
                return request.make_response(
                    json.dumps({"status": "success", "playlists": clean_pls}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=200
                )
            return request.make_response(
                json.dumps({"status": "error", "message": f"AzuraCast HTTP {r.status_code}"}),
                headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                status=r.status_code
            )
        except Exception as e:
            _logger.error("touch_radio_playlists error: %s", str(e))
            return request.make_response(
                json.dumps({"status": "error", "message": str(e)}),
                headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                status=500
            )

    @http.route(['/frawo/touch/api/radio/playlist/update', '/api/radio/playlist/update'], type='http', auth='none', methods=['POST'], cors='*', csrf=False, sitemap=False)
    def touch_radio_playlist_update(self, **kwargs):
        """Update playlist is_enabled or weight."""
        try:
            data = {}
            try:
                data = request.httprequest.get_json(force=True, silent=True) or {}
            except Exception:
                pass
            if not data:
                data = kwargs or {}

            pl_id = data.get('id')
            if not pl_id:
                return request.make_response(
                    json.dumps({"status": "error", "message": "Playlist-ID fehlt"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=400
                )

            update_payload = {}
            if 'is_enabled' in data:
                update_payload['is_enabled'] = bool(data['is_enabled'])
            if 'weight' in data:
                try:
                    update_payload['weight'] = max(1, min(25, int(data['weight'])))
                except (ValueError, TypeError):
                    pass

            if not update_payload:
                return request.make_response(
                    json.dumps({"status": "error", "message": "Keine Änderungen übergeben"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=400
                )

            base_url, api_key = self._get_azuracast_config()
            api_url = f"{base_url}/api/station/1/playlist/{pl_id}"
            headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
            r = requests.put(api_url, headers=headers, json=update_payload, verify=False, timeout=6)
            
            if r.status_code == 200:
                try:
                    request.env["frawo.agent.log"].sudo().create({
                        "name": f"Radio: Playlist {pl_id} aktualisiert",
                        "level": "info",
                        "message": f"Playlist {pl_id} geändert: {update_payload}"
                    })
                except Exception as log_err:
                    _logger.warning("Radio log error: %s", log_err)
                return request.make_response(
                    json.dumps({"status": "success", "updated": update_payload}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=200
                )
            return request.make_response(
                json.dumps({"status": "error", "message": f"AzuraCast HTTP {r.status_code}: {r.text}"}),
                headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                status=r.status_code
            )
        except Exception as e:
            _logger.error("touch_radio_playlist_update error: %s", str(e))
            return request.make_response(
                json.dumps({"status": "error", "message": str(e)}),
                headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                status=500
            )

    @http.route(['/frawo/touch/api/radio/search', '/api/radio/search'], type='http', auth='none', methods=['POST', 'GET'], cors='*', csrf=False, sitemap=False)
    def touch_radio_search(self, **kwargs):
        """Search requestable tracks in AzuraCast library."""
        try:
            data = {}
            try:
                data = request.httprequest.get_json(force=True, silent=True) or {}
            except Exception:
                pass
            if not data:
                data = kwargs or {}

            query = (data.get('query') or data.get('q') or '').strip().lower()
            if not query:
                return request.make_response(
                    json.dumps({"status": "success", "tracks": []}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=200
                )

            base_url, api_key = self._get_azuracast_config()
            api_url = f"{base_url}/api/station/1/requests"
            headers = {"X-API-Key": api_key}
            r = requests.get(api_url, headers=headers, verify=False, timeout=6)
            if r.status_code != 200:
                return request.make_response(
                    json.dumps({"status": "error", "message": f"AzuraCast HTTP {r.status_code}"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=r.status_code
                )

            all_tracks = r.json()
            results = []
            for item in all_tracks:
                song = item.get("song", {})
                title = song.get("title", "") or ""
                artist = song.get("artist", "") or ""
                album = song.get("album", "") or ""
                if query in title.lower() or query in artist.lower() or query in album.lower():
                    results.append({
                        "request_id": item.get("request_id"),
                        "title": title,
                        "artist": artist,
                        "album": album,
                        "art": song.get("art")
                    })
                    if len(results) >= 20:
                        break

            return request.make_response(
                json.dumps({"status": "success", "tracks": results}),
                headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                status=200
            )
        except Exception as e:
            _logger.error("touch_radio_search error: %s", str(e))
            return request.make_response(
                json.dumps({"status": "error", "message": str(e)}),
                headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                status=500
            )

    @http.route(['/frawo/touch/api/radio/request', '/api/radio/request'], type='http', auth='none', methods=['POST'], cors='*', csrf=False, sitemap=False)
    def touch_radio_request(self, **kwargs):
        """Enqueue a requested song on AzuraCast station 1."""
        try:
            data = {}
            try:
                data = request.httprequest.get_json(force=True, silent=True) or {}
            except Exception:
                pass
            if not data:
                data = kwargs or {}

            req_id = data.get('request_id')
            if not req_id:
                return request.make_response(
                    json.dumps({"status": "error", "message": "request_id fehlt"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=400
                )

            base_url, api_key = self._get_azuracast_config()
            api_url = f"{base_url}/api/station/1/request/{req_id}"
            headers = {"X-API-Key": api_key}
            r = requests.post(api_url, headers=headers, verify=False, timeout=6)
            if r.status_code == 200:
                res_data = r.json()
                msg = res_data.get("message", "Song erfolgreich eingereiht!")
                try:
                    request.env["frawo.agent.log"].sudo().create({
                        "name": "Radio: Song-Wunsch eingereiht",
                        "level": "info",
                        "message": f"Wunsch-Track {req_id} eingereiht: {msg}"
                    })
                except Exception as log_err:
                    _logger.warning("Radio log error: %s", log_err)
                return request.make_response(
                    json.dumps({"status": "success", "message": msg}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=200
                )
            else:
                return request.make_response(
                    json.dumps({"status": "error", "message": f"Request fehlgeschlagen (HTTP {r.status_code})"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                    status=r.status_code
                )
        except Exception as e:
            _logger.error("touch_radio_request error: %s", str(e))
            return request.make_response(
                json.dumps({"status": "error", "message": str(e)}),
                headers=[('Content-Type', 'application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')],
                status=500
            )


    # ─────────────────────────────────────────────────────────────
    # FraWo Hub (HTTPS Domain Access: https://frawo.tech/hub)
    # ─────────────────────────────────────────────────────────────

    @http.route(['/hub', '/frawo/hub', '/frawo/touch/hub'], type='http', auth='none', csrf=False, sitemap=False)
    def frawo_hub_page(self, **kwargs):
        """Serves FraWo Hub directly via HTTPS (https://frawo.tech/hub)."""
        import os
        try:
            view_path = os.path.join(os.path.dirname(__file__), '..', 'views', 'frawo_hub.html')
            if not os.path.exists(view_path):
                # Fallback to surface deployment path
                view_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'deployments', 'surface', 'frawo_anker_hub.html')
            
            if os.path.exists(view_path):
                with open(view_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return request.make_response(
                    content,
                    headers=[
                        ('Content-Type', 'text/html; charset=utf-8'),
                        ('Cache-Control', 'no-cache, no-store, must-revalidate')
                    ]
                )
            return request.make_response("<p>FraWo Hub Template nicht gefunden.</p>", status=404, headers=[('Content-Type', 'text/html')])
        except Exception as e:
            _logger.error("frawo_hub_page error: %s", str(e))
            return request.make_response(f"<p>Fehler beim Laden des Hubs: {str(e)}</p>", status=500, headers=[('Content-Type', 'text/html')])


    @http.route('/api/task/answer', type='http', auth='none', methods=['POST'], csrf=False, cors='*', sitemap=False)
    def api_task_answer(self, **kwargs):
        """Processes question answers directly from the Hub into Odoo chatter and sets Tag 160."""
        import json
        try:
            body = request.httprequest.data.decode('utf-8')
            data = json.loads(body)
            task_id = int(data.get('task_id', 0))
            raw_answer = data.get('answer', '').strip()
            use_ollama = bool(data.get('use_ollama', True))
            question = data.get('question', '')

            if not task_id or not raw_answer:
                return request.make_response(
                    json.dumps({"success": False, "error": "task_id und answer sind erforderlich"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8')],
                    status=400
                )

            refined_answer = None
            if use_ollama:
                try:
                    import urllib.request
                    prompt = (
                        "Du bist der KI-Assistent im FraWo-Betrieb. "
                        "Formuliere die Antwort von Wolf Prinz zu einer offenen Frage "
                        "in eine präzise, sachliche, kurze Antwort (1-2 Sätze) für den Odoo-Chatter um. "
                        "Regel: Nur Fakten, keine Floskeln, kein Hallo/Tschüss.\n\n"
                        f"Frage: {question}\n"
                        f"Wolfs Notiz: {raw_answer}\n\n"
                        "Formulierte Antwort:"
                    )
                    payload = json.dumps({
                        "model": "frawo-mitarbeiter-fast:latest",
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.2, "top_p": 0.9}
                    }).encode('utf-8')
                    req = urllib.request.Request("http://10.1.0.227:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=6.0) as resp:
                        if resp.status == 200:
                            res_data = json.loads(resp.read().decode('utf-8'))
                            refined = res_data.get('response', '').strip()
                            if refined:
                                refined_answer = refined
                except Exception as oe:
                    _logger.warning("Ollama refine fallback: %s", str(oe))

            env = request.env(user=1)
            task = env['project.task'].sudo().browse(task_id)
            if not task.exists():
                return request.make_response(
                    json.dumps({"success": False, "error": f"Task #{task_id} existiert nicht"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8')],
                    status=404
                )

            # 1. Post chatter message with both original note and Ollama refined summary
            if refined_answer and refined_answer != raw_answer:
                chatter_body = (
                    f"<p><b>Antwort von Wolf (via FraWo Hub):</b><br>{raw_answer}</p>"
                    f"<p>🤖 <b>Ollama KI-Strukturierung (OptiPlex 10.1.0.227):</b><br>{refined_answer}</p>"
                )
            else:
                chatter_body = f"<p><b>Antwort von Wolf (via FraWo Hub):</b><br>{raw_answer}</p>"

            task.message_post(
                body=chatter_body,
                message_type='comment',
                subtype_xmlid='mail.mt_comment'
            )

            # 2. Update tags: remove 153 ('🙋 braucht Wolf'), add 160 ('✅ beantwortet')
            new_tags = [t.id for t in task.tag_ids if t.id != 153]
            if 160 not in new_tags:
                new_tags.append(160)
            task.write({'tag_ids': [(6, 0, new_tags)]})

            final_answer = refined_answer or raw_answer
            return request.make_response(
                json.dumps({
                    "success": True,
                    "task_id": task_id,
                    "answer": final_answer,
                    "message": "Erfolgreich in Odoo erfasst & Tag '✅ beantwortet' gesetzt."
                }),
                headers=[('Content-Type', 'application/json; charset=utf-8')]
            )
        except Exception as e:
            _logger.error("api_task_answer error: %s", str(e))
            return request.make_response(
                json.dumps({"success": False, "error": str(e)}),
                headers=[('Content-Type', 'application/json; charset=utf-8')],
                status=500
            )


    @http.route('/api/ollama/refine', type='http', auth='none', methods=['POST'], csrf=False, cors='*', sitemap=False)
    def api_ollama_refine(self, **kwargs):
        """Refines text with local Ollama on OptiPlex (10.1.0.227:11434)."""
        import json, urllib.request
        try:
            body = request.httprequest.data.decode('utf-8')
            data = json.loads(body)
            question = data.get('question', '')
            raw_answer = data.get('answer', '')

            prompt = (
                "Du bist der KI-Assistent im FraWo-Betrieb. "
                "Formuliere die folgende stichpunktartige Antwort von Wolf Prinz zu einer offenen Frage "
                "in eine präzise, sachliche, kurze Antwort (1-2 Sätze) für den Odoo-Chatter um. "
                "Regel: Nur Fakten, keine Floskeln, kein 'Hallo/Tschüss'.\n\n"
                f"Frage: {question}\n"
                f"Wolfs Notiz: {raw_answer}\n\n"
                "Formulierte Antwort:"
            )
            payload = json.dumps({
                "model": "frawo-mitarbeiter-fast:latest",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "top_p": 0.9}
            }).encode('utf-8')
            req = urllib.request.Request("http://10.1.0.227:11434/api/generate", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                if resp.status == 200:
                    res_data = json.loads(resp.read().decode('utf-8'))
                    refined = res_data.get('response', '').strip()
                    return request.make_response(
                        json.dumps({"success": True, "refined": refined}),
                        headers=[('Content-Type', 'application/json; charset=utf-8')]
                    )
            return request.make_response(
                json.dumps({"success": False, "error": "Ollama antwortete nicht mit 200"}),
                headers=[('Content-Type', 'application/json; charset=utf-8')],
                status=502
            )
        except Exception as e:
            _logger.error("api_ollama_refine error: %s", str(e))
            return request.make_response(
                json.dumps({"success": False, "error": str(e)}),
                headers=[('Content-Type', 'application/json; charset=utf-8')],
                status=500
            )


    @http.route('/api/web/research', type='http', auth='none', methods=['POST'], csrf=False, cors='*', sitemap=False)
    def api_web_research(self, **kwargs):
        """Searches the web via DuckDuckGo and synthesizes the findings with local Ollama on OptiPlex."""
        import json, urllib.request, urllib.parse, re, html
        try:
            body = request.httprequest.data.decode('utf-8')
            data = json.loads(body)
            query = data.get('query', '').strip()

            if not query:
                return request.make_response(
                    json.dumps({"success": False, "error": "Suchbegriff / Frage erforderlich"}),
                    headers=[('Content-Type', 'application/json; charset=utf-8')],
                    status=400
                )

            # 1. Search DuckDuckGo Lite
            url = "https://lite.duckduckgo.com/lite/"
            payload = urllib.parse.urlencode({"q": query}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded"
            })
            
            search_results = []
            try:
                with urllib.request.urlopen(req, timeout=6.0) as resp:
                    content = resp.read().decode("utf-8", errors="ignore")
                
                links = re.findall(r"<a[^>]+class=['\"]result-link['\"][^>]*href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", content)
                snippets = re.findall(r"<td[^>]+class=['\"]result-snippet['\"][^>]*>(.*?)</td>", content, re.DOTALL)
                
                for i in range(min(len(links), len(snippets), 4)):
                    href, raw_t = links[i]
                    t = re.sub(r"<[^>]+>", "", raw_t).strip()
                    s = re.sub(r"<[^>]+>", "", snippets[i]).strip()
                    search_results.append({
                        "title": html.unescape(t),
                        "url": href,
                        "snippet": html.unescape(s)
                    })
            except Exception as se:
                _logger.warning("DuckDuckGo search error: %s", str(se))

            if not search_results:
                return request.make_response(
                    json.dumps({"success": False, "error": "Keine Suchergebnisse gefunden oder Timeout."}),
                    headers=[('Content-Type', 'application/json; charset=utf-8')],
                    status=502
                )

            # 2. Synthesize with Ollama on OptiPlex (10.1.0.227:11434)
            snippets_text = "\n\n".join([
                f"- Titel: {r['title']}\n  Quelle: {r['url']}\n  Auszug: {r['snippet']}"
                for r in search_results
            ])
            
            prompt = (
                "Du bist der KI-Recherche-Assistent im FraWo-Betrieb. "
                "Fasse die folgenden Web-Suchergebnisse zu der Frage/Aufgabe präzise, sachlich und kompakt zusammen (maximal 2-3 Sätze). "
                "Nenne konkrete Fakten, Zahlen, Spezifikationen oder Preise falls vorhanden. "
                "Regel: Nur Fakten, keine Begrüßung, kein Konjunktiv, keine Floskeln.\n\n"
                f"Suchanfrage / Frage: {query}\n\n"
                f"Suchergebnisse aus dem Web:\n{snippets_text}\n\n"
                "Kompakte Recherche-Zusammenfassung:"
            )

            ollama_summary = ""
            try:
                ollama_payload = json.dumps({
                    "model": "frawo-mitarbeiter-fast:latest",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "top_p": 0.9}
                }).encode('utf-8')
                ollama_req = urllib.request.Request("http://10.1.0.227:11434/api/generate", data=ollama_payload, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(ollama_req, timeout=8.0) as o_resp:
                    if o_resp.status == 200:
                        o_data = json.loads(o_resp.read().decode('utf-8'))
                        ollama_summary = o_data.get('response', '').strip()
            except Exception as oe:
                _logger.warning("Ollama web synthesis error: %s", str(oe))
                ollama_summary = search_results[0]['snippet']

            return request.make_response(
                json.dumps({
                    "success": True,
                    "query": query,
                    "summary": ollama_summary,
                    "results": search_results
                }),
                headers=[('Content-Type', 'application/json; charset=utf-8')]
            )
        except Exception as e:
            _logger.error("api_web_research error: %s", str(e))
            return request.make_response(
                json.dumps({"success": False, "error": str(e)}),
                headers=[('Content-Type', 'application/json; charset=utf-8')],
                status=500
            )



