# -*- coding: utf-8 -*-
import logging
from datetime import date
from odoo import http
from odoo.http import request
from odoo.tools import consteq

KIOSK_TOKEN_PARAM = 'frawo_agent.kiosk_token'
KIOSK_TOKEN_PLACEHOLDER = 'SETZE_KIOSK_TOKEN'
KIOSK_SESSION_FLAG = 'frawo_kiosk_authorized'

_logger = logging.getLogger(__name__)

class AnkerTrackerController(http.Controller):

    @http.route('/anker-tracker/sw.js', type='http', auth='public')
    def anker_tracker_sw(self, **kwargs):
        sw_content = """
const CACHE_NAME = 'anker-tracker-v1';
const ASSETS = [
  '/anker-tracker',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap',
  'https://unpkg.com/@phosphor-icons/web@2.1.1/src/bold/style.css',
  'https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method === 'POST') {
    // Cannot cache POST requests easily without Background Sync.
    // For now, let them fail normally when offline.
    return;
  }
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request).then(fetchRes => {
        return caches.open(CACHE_NAME).then(cache => {
          if (event.request.url.startsWith('http')) {
             cache.put(event.request.url, fetchRes.clone());
          }
          return fetchRes;
        });
      });
    }).catch(() => caches.match('/anker-tracker'))
  );
});
"""
        return request.make_response(sw_content, headers=[('Content-Type', 'application/javascript')])

    @http.route('/anker-tracker/manifest.json', type='http', auth='public')
    def anker_tracker_manifest(self, **kwargs):
        manifest_content = """
{
  "name": "Anker Tracker",
  "short_name": "Tracker",
  "start_url": "/anker-tracker",
  "display": "standalone",
  "background_color": "#0c0f14",
  "theme_color": "#0c0f14",
  "icons": [
    {
      "src": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48dGV4dCB5PSIuOWVtIiBmb250LXNpemU9IjkwIj7impM8L3RleHQ+PC9zdmc+",
      "sizes": "192x192",
      "type": "image/svg+xml"
    }
  ]
}
"""
        return request.make_response(manifest_content, headers=[('Content-Type', 'application/json')])


    def _render_standalone(self, template, values):
        """Rendert ein QWeb-Template als eigenständige HTML-Seite.

        Die Templates enthalten ein vollständiges <html>-Dokument. Der DOCTYPE
        kann nicht im Template stehen (XML erlaubt ihn nur ganz am Anfang) und
        wird deshalb hier vorangestellt — ohne ihn schalten Browser in den
        Quirks-Modus und das Kiosk-Layout verrutscht.
        """
        html = request.env['ir.qweb']._render(template, values)
        return request.make_response(
            '<!DOCTYPE html>\n' + str(html),
            headers=[('Content-Type', 'text/html; charset=utf-8')],
        )

    def _check_kiosk_auth(self):
        """Erlaubt Zugriff für angemeldete Benutzer oder mit gültigem Kiosk-Token.

        Das Token steht ausschliesslich in der Datenbank (ir.config_parameter
        'frawo_agent.kiosk_token'), niemals im Quellcode — das Repo ist public.
        Ist kein Token gesetzt, wird der Zugriff verweigert (fail closed).

        Ein einmal korrekt übergebenes Token wird in der Sitzung vermerkt. Die
        Kiosk-Oberfläche ruft ihre Daten per JSON-RPC ohne Token ab; das Tablet
        muss die Adresse mit ?kiosk_token=... daher nur einmal öffnen.
        """
        user = request.env.user
        if user and not user._is_public():
            return

        if request.session.get(KIOSK_SESSION_FLAG):
            return

        expected = (request.env['ir.config_parameter'].sudo()
                    .get_param(KIOSK_TOKEN_PARAM, '') or '').strip()
        if not expected or expected == KIOSK_TOKEN_PLACEHOLDER:
            _logger.warning(
                "Anker Tracker: Kiosk-Zugriff abgelehnt — Systemparameter %s ist nicht gesetzt.",
                KIOSK_TOKEN_PARAM,
            )
            raise request.not_found()

        token = request.httprequest.headers.get('X-Kiosk-Token') or request.params.get('kiosk_token') or ''
        if not consteq(token, expected):
            raise request.not_found()

        request.session[KIOSK_SESSION_FLAG] = True



    @http.route(['/anker-tracker', '/anker_tracker'], type='http', auth='public')
    def anker_tracker_view(self, **kwargs):
        """Serves the Anker Tracker HTML kiosk as a standalone page."""
        self._check_kiosk_auth()
        return self._render_standalone('frawo_agent.anker_tracker_template', {})

    @http.route('/anker-tracker/print', type='http', auth='public')
    def anker_tracker_print_view(self, **kwargs):
        """Renders the print-optimized A4 invoice layout for the beverage store."""
        self._check_kiosk_auth()
        try:
            consumers_model = request.env['anker.tracker.consumer'].sudo()
            products_model = request.env['anker.tracker.product'].sudo()
            consumptions_model = request.env['anker.tracker.consumption'].sudo()

            consumers = consumers_model.search([('active', '=', True)])
            products = products_model.search([('active', '=', True)])

            grand_total_bottles = 0
            product_totals = []
            for product in products:
                count = consumptions_model.search_count([
                    ('product_id', '=', product.id),
                    ('billed', '=', False)
                ])
                if count > 0:
                    grand_total_bottles += count
                    crates = count // (product.crate_size or 1)
                    bottles = count % (product.crate_size or 1)
                    product_totals.append({
                        'product': product,
                        'count': count,
                        'crates': crates,
                        'bottles': bottles,
                    })

            consumer_totals = []
            for consumer in consumers:
                consumer_records = consumptions_model.search([
                    ('consumer_id', '=', consumer.id),
                    ('billed', '=', False)
                ])
                count = len(consumer_records)
                if count > 0:
                    prod_details = {}
                    for rec in consumer_records:
                        p = rec.product_id
                        if p.id not in prod_details:
                            prod_details[p.id] = {
                                'name': p.name,
                                'emoji': p.emoji,
                                'manufacturer': p.manufacturer or '',
                                'volume': p.volume,
                                'count': 0
                            }
                        prod_details[p.id]['count'] += 1
                    consumer_totals.append({
                        'consumer': consumer,
                        'count': count,
                        'details': list(prod_details.values())
                    })

            today_str = date.today().strftime('%d.%m.%Y')
            return self._render_standalone('frawo_agent.anker_tracker_print_template', {
                'product_totals': product_totals,
                'consumer_totals': consumer_totals,
                'grand_total_bottles': grand_total_bottles,
                'today_str': today_str,
            })
        except Exception as e:
            _logger.error("Anker Tracker print view error: %s", e)
            return request.make_response(f"Fehler: {str(e)}", status=500)

    @http.route('/anker_tracker/get_data', type='jsonrpc', auth='public', methods=['POST'])
    def get_data(self, **kwargs):
        """Fetches active consumers, products, and recent unbilled consumptions."""
        self._check_kiosk_auth()
        try:
            consumers_model = request.env['anker.tracker.consumer'].sudo()
            products_model = request.env['anker.tracker.product'].sudo()
            consumptions_model = request.env['anker.tracker.consumption'].sudo()

            consumers = consumers_model.search_read([('active', '=', True)], ['id', 'name', 'role', 'sequence'])
            if not consumers:
                consumers_model.create([{'name': 'Wolfi'}, {'name': 'Franz'}])
                consumers = consumers_model.search_read([('active', '=', True)], ['id', 'name', 'role', 'sequence'])

            products = products_model.search_read(
                [('active', '=', True)],
                ['id', 'name', 'emoji', 'manufacturer', 'volume', 'is_alcoholic', 'crate_size', 'price_per_bottle',
                 'pfand_per_bottle', 'pfand_per_crate']
            )
            if not products:
                products_model.create([
                    {'name': 'Lager Hell', 'emoji': '🍺', 'manufacturer': 'Augustiner', 'volume': 0.5, 'is_alcoholic': True, 'crate_size': 20, 'price_per_bottle': 0.97},
                    {'name': 'Spezi', 'emoji': '🥤', 'manufacturer': 'Paulaner', 'volume': 0.33, 'is_alcoholic': False, 'crate_size': 24, 'price_per_bottle': 0.72},
                    {'name': 'Holderweisse', 'emoji': '🌾', 'manufacturer': 'Schaffler', 'volume': 0.5, 'is_alcoholic': True, 'crate_size': 1, 'price_per_bottle': 2.18},
                    {'name': 'Mineralwasser medium', 'emoji': '💧', 'manufacturer': 'Gerolsteiner', 'volume': 1.0, 'is_alcoholic': False, 'crate_size': 12, 'price_per_bottle': 0.79},
                ])
                products = products_model.search_read(
                    [('active', '=', True)],
                    ['id', 'name', 'emoji', 'manufacturer', 'volume', 'is_alcoholic', 'crate_size', 'price_per_bottle']
                )

            consumptions_records = consumptions_model.search([('billed', '=', False)], limit=500, order='timestamp desc')
            consumptions = []
            for c in consumptions_records:
                timestamp_ms = int(c.timestamp.timestamp() * 1000) if c.timestamp else 0
                consumptions.append({
                    'id': c.id,
                    'consumerId': c.consumer_id.id,
                    'productId': c.product_id.id,
                    'timestamp': timestamp_ms,
                    'unitType': c.unit_type or 'bottle',
                    'quantity': c.quantity or 1,
                })

            # --- Consumption rankings for smart sorting ---
            # Global consumption count per product (by total bottles)
            global_counts = {}  # product_id → total bottles
            global_crates = {}  # product_id → crate count
            for c in consumptions_records:
                pid = c.product_id.id
                qty = c.quantity or 1
                global_counts[pid] = global_counts.get(pid, 0) + qty
                if c.unit_type == 'crate':
                    global_crates[pid] = global_crates.get(pid, 0) + 1

            # Per-consumer counts for personalized ranking
            consumer_counts = {}  # consumer_id → {product_id → total bottles}
            for c in consumptions_records:
                cid = c.consumer_id.id
                pid = c.product_id.id
                qty = c.quantity or 1
                if cid not in consumer_counts:
                    consumer_counts[cid] = {}
                consumer_counts[cid][pid] = consumer_counts[cid].get(pid, 0) + qty

            # Enrich products with entnahme data
            for p in products:
                pid = p['id']
                p['consumed_bottles'] = global_counts.get(pid, 0)
                p['consumed_crates'] = global_crates.get(pid, 0)

            return {
                'consumers': consumers,
                'products': products,
                'consumptions': consumptions,
                'consumer_counts': consumer_counts,
            }
        except Exception as e:
            _logger.error("Anker Tracker get_data error: %s", e)
            return {'error': str(e)}

    @http.route('/anker_tracker/consume', type='jsonrpc', auth='public', methods=['POST'])
    def consume(self, consumer_id, product_id, unit_type='bottle', quantity=1, **kwargs):
        """Records a drink consumption. unit_type: 'bottle' or 'crate'.
        For crate: quantity is auto-set to crate_size."""
        self._check_kiosk_auth()
        try:
            consumption_model = request.env['anker.tracker.consumption'].sudo()
            product = request.env['anker.tracker.product'].sudo().browse(int(product_id))

            # Auto-set quantity for crate
            if unit_type == 'crate':
                quantity = product.crate_size or 20

            record = consumption_model.create({
                'consumer_id': int(consumer_id),
                'product_id': int(product_id),
                'unit_type': unit_type,
                'quantity': int(quantity),
            })
            _logger.info(
                "Anker Tracker: Consumption ID %s (%s, %s, %s, qty=%s)",
                record.id, consumer_id, product.name, unit_type, quantity
            )

            return {'status': 'success', 'id': record.id, 'quantity': quantity}
        except Exception as e:
            _logger.error("Anker Tracker consume error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/add_consumer', type='jsonrpc', auth='public', methods=['POST'])
    def add_consumer(self, name, **kwargs):
        """Adds a new consumer/person."""
        self._check_kiosk_auth()
        try:
            record = request.env['anker.tracker.consumer'].sudo().create({'name': name})
            return {'status': 'success', 'id': record.id}
        except Exception as e:
            _logger.error("Anker Tracker add_consumer error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/add_product', type='jsonrpc', auth='public', methods=['POST'])
    def add_product(self, name, emoji, manufacturer, volume, is_alcoholic, crate_size, price_per_bottle=0.0, **kwargs):
        """Adds a new beverage product."""
        self._check_kiosk_auth()
        try:
            record = request.env['anker.tracker.product'].sudo().create({
                'name': name,
                'emoji': emoji or '🥤',
                'manufacturer': manufacturer,
                'volume': float(volume),
                'is_alcoholic': bool(is_alcoholic),
                'crate_size': int(crate_size),
                'price_per_bottle': float(price_per_bottle or 0),
            })
            return {'status': 'success', 'id': record.id}
        except Exception as e:
            _logger.error("Anker Tracker add_product error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/delete_item', type='jsonrpc', auth='public', methods=['POST'])
    def delete_item(self, model_type, item_id, **kwargs):
        self._check_kiosk_auth()
        try:
            if model_type not in ['consumers', 'products', 'consumptions']:
                return {'status': 'error', 'message': 'Invalid model type'}
            model_map = {'consumers': 'anker.tracker.consumer', 'products': 'anker.tracker.product', 'consumptions': 'anker.tracker.consumption'}
            record = request.env[model_map[model_type]].sudo().browse(int(item_id))
            if record.exists():
                record.unlink()
            return {'status': 'success'}
        except Exception as e:
            _logger.error("Anker Tracker delete_item error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/bill_now', type='jsonrpc', auth='public', methods=['POST'])
    def bill_now(self, **kwargs):
        """Marks all unbilled consumption records as billed with purchase summary logging."""
        self._check_kiosk_auth()
        try:
            result = request.env['anker.tracker.consumption'].sudo().bill_now()
            return result
        except Exception as e:
            _logger.error("Anker Tracker bill_now error: %s", e)
            return {'status': 'error', 'message': str(e)}

    @http.route('/anker_tracker/get_purchase_summary', type='jsonrpc', auth='public', methods=['POST'])
    def get_purchase_summary(self, **kwargs):
        """Returns purchase summary with MwSt breakdown (read-only, does not bill)."""
        self._check_kiosk_auth()
        try:
            return request.env['anker.tracker.consumption'].sudo().generate_purchase_summary()
        except Exception as e:
            _logger.error("Anker Tracker get_purchase_summary error: %s", e)
            return {'error': str(e)}

    @http.route('/anker_tracker/health', type='http', auth='none', methods=['GET'], csrf=False)
    def health(self, **kwargs):
        """Lightweight health endpoint for Uptime Kuma / external monitoring.
        Returns JSON with status, product count, consumer count, and timestamp.
        Bewusst ohne Kiosk-Token: Uptime Kuma fragt ohne Token ab, und es werden
        nur aggregierte Zähler zurückgegeben — keine Personen- oder Buchungsdaten.
        """
        import json
        from datetime import datetime
        try:
            product_count = request.env['anker.tracker.product'].sudo().search_count([('active', '=', True)])
            consumer_count = request.env['anker.tracker.consumer'].sudo().search_count([('active', '=', True)])
            unbilled_count = request.env['anker.tracker.consumption'].sudo().search_count([('billed', '=', False)])
            body = json.dumps({
                'status': 'ok',
                'products': product_count,
                'consumers': consumer_count,
                'unbilled': unbilled_count,
                'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            })
            return request.make_response(body, headers=[
                ('Content-Type', 'application/json'),
                ('Cache-Control', 'no-cache'),
            ])
        except Exception as e:
            _logger.error("Anker Tracker health check error: %s", e)
            body = json.dumps({'status': 'error', 'message': str(e)})
            return request.make_response(body, status=500, headers=[
                ('Content-Type', 'application/json'),
            ])

