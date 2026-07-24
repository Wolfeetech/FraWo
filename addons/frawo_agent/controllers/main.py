from odoo import http
from odoo.http import request
import logging
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

    # ─────────────────────────────────────────────────────────────
    # Public Radio Endpoints
    # ─────────────────────────────────────────────────────────────

    @http.route('/radio/vote', type='json', auth='user', cors='*', methods=['POST'])
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

    @http.route('/radio/search', type='json', auth='user', cors='*', methods=['POST'])
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

    @http.route('/radio/request', type='json', auth='user', cors='*', methods=['POST'])
    def radio_request(self, request_id, **kwargs):
        if not request_id:
            return {"status": "error", "message": "Missing request_id"}
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

