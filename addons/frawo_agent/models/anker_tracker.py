# -*- coding: utf-8 -*-
import json
import logging
import os

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class AnkerTrackerConsumer(models.Model):
    _name = 'anker.tracker.consumer'
    _description = 'Anker Tracker Consumer'
    _order = 'sequence, name asc'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Aktiv', default=True)
    added_at = fields.Datetime(string='Hinzugefügt am', default=fields.Datetime.now)
    role = fields.Selection([
        ('master', 'Master'),
        ('guest', 'Gast'),
    ], string='Rolle', default='guest',
        help='Master = Wolf/Franz (Inhaber). Gast = Besucher.')
    sequence = fields.Integer(string='Reihenfolge', default=10,
        help='Master-User werden zuerst angezeigt (niedrigere Zahl = weiter oben)')

class AnkerTrackerProduct(models.Model):
    _name = 'anker.tracker.product'
    _description = 'Anker Tracker Product'
    _order = 'name asc'

    name = fields.Char(string='Getränkename', required=True)
    emoji = fields.Char(string='Emoji', default='🥤')
    manufacturer = fields.Char(string='Hersteller')
    volume = fields.Float(string='Flaschengröße (L)', default=0.5)
    is_alcoholic = fields.Boolean(string='Alkoholisch', default=False)
    crate_size = fields.Integer(string='Flaschen pro Kiste', default=20)
    price_per_bottle = fields.Float(string='Preis/Flasche (€)', digits=(10, 2), default=0.0)
    active = fields.Boolean(string='Aktiv', default=True)

    # ── Pfand ──
    pfand_per_bottle = fields.Float(string='Flaschenpfand (€)', digits=(10, 2), default=0.08,
        help='Mehrweg-Flaschenpfand, Standard 0,08€')
    pfand_per_crate = fields.Float(string='Kastenpfand (€)', digits=(10, 2), default=1.50,
        help='Kastenpfand, Standard 1,50€. Fällt nur bei Kistenentnahme an.')

    # ── Computed: Entnahme-Zusammenfassung ──
    unbilled_bottles = fields.Integer(
        string='Offene Flaschen', compute='_compute_entnahme', store=False)
    unbilled_crates = fields.Integer(
        string='Offene Kisten', compute='_compute_entnahme', store=False)

    @api.depends_context('force_recompute')
    def _compute_entnahme(self):
        Consumption = self.env['anker.tracker.consumption']
        for product in self:
            records = Consumption.search([
                ('product_id', '=', product.id),
                ('billed', '=', False),
            ])
            total_bottles = sum(r.quantity for r in records)
            total_crates = sum(1 for r in records if r.unit_type == 'crate')
            product.unbilled_bottles = total_bottles
            product.unbilled_crates = total_crates

class AnkerTrackerConsumption(models.Model):
    _name = 'anker.tracker.consumption'
    _description = 'Anker Tracker Consumption'
    _order = 'timestamp desc'

    consumer_id = fields.Many2one('anker.tracker.consumer', string='Person', required=True, ondelete='cascade')
    product_id = fields.Many2one('anker.tracker.product', string='Getränk', required=True, ondelete='cascade')
    timestamp = fields.Datetime(string='Zeitstempel', default=fields.Datetime.now)
    billed = fields.Boolean(string='Abgerechnet', default=False)
    unit_type = fields.Selection([
        ('bottle', 'Einzelflasche'),
        ('crate', 'Kiste'),
    ], string='Entnahme-Art', default='bottle', required=True,
        help='Kiste = volle Kiste mit Kastenpfand. Einzelflasche = nur Flaschenpfand.')
    quantity = fields.Integer(string='Anzahl Flaschen', default=1,
        help='Bei Kiste automatisch = Flaschen pro Kiste. Bei Einzelflasche = 1 (oder Mehrfachentnahme).')

    # ──────────────────────────────────────────────
    #  Helpers
    # ──────────────────────────────────────────────

    def _get_data_dir(self):
        """Return (and create if needed) the persistent data directory."""
        data_dir = '/mnt/extra-addons/frawo_agent/data'
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir, exist_ok=True)
            except Exception:
                data_dir = '/tmp'
        return data_dir

    # ──────────────────────────────────────────────
    #  Telegram: Stündlicher Entnahme-Bericht (Cron)
    # ──────────────────────────────────────────────

    @api.model
    def cron_telegram_hourly_summary(self):
        """Hourly cron: sends Telegram summary of all unbilled entnahmen grouped by person.
        Only sends if there are any unbilled records."""
        import urllib.request
        from datetime import datetime

        try:
            ICP = self.env['ir.config_parameter'].sudo()
            bot_token = (ICP.get_param('frawo_agent.telegram_bot_token') or '').strip()
            chat_id = (ICP.get_param('frawo_agent.telegram_chat_id') or '').strip()
            if not bot_token or not chat_id:
                _logger.warning("Anker Tracker Telegram: bot_token or chat_id not configured")
                return

            # All unbilled consumption records
            records = self.search([('billed', '=', False)], order='consumer_id, product_id')
            if not records:
                return  # Nothing to report

            lines = [
                f"📊 Anker Tracker – Stand {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                "",
            ]

            # Group by consumer
            consumers = {}
            for r in records:
                cid = r.consumer_id.id
                if cid not in consumers:
                    consumers[cid] = {
                        'name': r.consumer_id.name,
                        'role': r.consumer_id.role or 'guest',
                        'products': {},
                    }
                pid = r.product_id.id
                if pid not in consumers[cid]['products']:
                    consumers[cid]['products'][pid] = {
                        'name': r.product_id.name,
                        'emoji': '🍺' if r.product_id.is_alcoholic else '🥤',
                        'price': r.product_id.price_per_bottle or 0,
                        'pfand_bottle': r.product_id.pfand_per_bottle or 0.08,
                        'pfand_crate': r.product_id.pfand_per_crate or 1.50,
                        'crate_size': r.product_id.crate_size or 20,
                        'bottles': 0,
                        'crates': 0,
                    }
                consumers[cid]['products'][pid]['bottles'] += r.quantity or 1
                if r.unit_type == 'crate':
                    consumers[cid]['products'][pid]['crates'] += 1

            total_bottles = 0
            total_cost = 0.0
            total_pfand = 0.0

            # Sort: masters first
            sorted_consumers = sorted(
                consumers.values(),
                key=lambda c: (0 if c['role'] == 'master' else 1, c['name'])
            )

            for c in sorted_consumers:
                icon = '👑' if c['role'] == 'master' else '👤'
                person_bottles = 0
                person_cost = 0.0
                person_pfand = 0.0
                prod_lines = []

                for pd in c['products'].values():
                    cost = pd['bottles'] * pd['price']
                    pfand = (pd['bottles'] * pd['pfand_bottle']) + (pd['crates'] * pd['pfand_crate'])
                    person_bottles += pd['bottles']
                    person_cost += cost
                    person_pfand += pfand

                    parts = []
                    if pd['crates'] > 0:
                        parts.append(f"{pd['crates']}📦")
                    loose = pd['bottles'] - (pd['crates'] * pd['crate_size'])
                    if loose > 0:
                        parts.append(f"{loose}🍾")
                    amt = ' + '.join(parts) if parts else f"{pd['bottles']}🍾"
                    prod_lines.append(f"  {pd['emoji']} {pd['name']}: {amt} = {self._fmt_eur(cost)}")

                lines.append(f"{icon} {c['name']}: {person_bottles} Fl. = {self._fmt_eur(person_cost)}")
                lines.extend(prod_lines)
                lines.append("")
                total_bottles += person_bottles
                total_cost += person_cost
                total_pfand += person_pfand

            lines.append("━━━━━━━━━━━━━━━━━━")
            lines.append(f"Σ {total_bottles} Fl. = {self._fmt_eur(total_cost)}")
            if total_pfand > 0:
                lines.append(f"📎 Pfand: {self._fmt_eur(total_pfand)}")
            lines.append(f"💰 Gesamt: {self._fmt_eur(total_cost + total_pfand)}")

            msg = "\n".join(lines)
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = json.dumps({'chat_id': chat_id, 'text': msg}).encode('utf-8')
            req = urllib.request.Request(
                url, data=payload,
                headers={'Content-Type': 'application/json'}, method='POST'
            )
            urllib.request.urlopen(req, timeout=10)
            _logger.info("Anker Tracker: Hourly Telegram summary sent (%d bottles)", total_bottles)
        except Exception as e:
            _logger.warning("Anker Tracker: Hourly Telegram summary failed: %s", e)

    @staticmethod
    def _fmt_eur(value):
        """Format a float as German-locale Euro string, e.g. '12,34 €'."""
        return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + " €"

    # ──────────────────────────────────────────────
    #  1. Telegram Daily Summary
    # ──────────────────────────────────────────────

    @api.model
    def cron_telegram_daily_summary(self):
        """Daily cron: compile unbilled stats per person and send via Telegram Bot API."""
        import urllib.request
        import urllib.parse
        from datetime import datetime

        ICP = self.env['ir.config_parameter'].sudo()
        bot_token = (ICP.get_param('frawo_agent.telegram_bot_token') or '').strip()
        chat_id = (ICP.get_param('frawo_agent.telegram_chat_id') or '').strip()

        if not bot_token or not chat_id:
            _logger.warning(
                "Telegram daily summary skipped – "
                "frawo_agent.telegram_bot_token or frawo_agent.telegram_chat_id not configured."
            )
            self.env['frawo.agent.log'].sudo().create({
                'name': 'Telegram Tagesbericht',
                'level': 'warning',
                'message': 'Bot-Token oder Chat-ID nicht konfiguriert – Versand übersprungen.',
            })
            return False

        # Gather unbilled consumptions
        unbilled = self.search([('billed', '=', False)])
        if not unbilled:
            _logger.info("Telegram daily summary: no unbilled records – nothing to report.")
            return True

        today_str = datetime.now().strftime('%d.%m.%Y')

        # Group by consumer → product
        consumer_map = {}  # consumer_id → {name, products: {product_id → {…}}}
        for rec in unbilled:
            cid = rec.consumer_id.id
            if cid not in consumer_map:
                consumer_map[cid] = {
                    'name': rec.consumer_id.name,
                    'products': {},
                }
            pid = rec.product_id.id
            if pid not in consumer_map[cid]['products']:
                p = rec.product_id
                consumer_map[cid]['products'][pid] = {
                    'name': p.name,
                    'emoji': p.emoji or '🥤',
                    'is_alcoholic': p.is_alcoholic,
                    'price': p.price_per_bottle or 0.0,
                    'count': 0,
                }
            consumer_map[cid]['products'][pid]['count'] += 1

        # Build message
        lines = [f"🍺 Anker Tracker – Tagesbericht {today_str}", ""]

        grand_bottles = 0
        grand_cost = 0.0
        total_alc_brutto = 0.0
        total_free_brutto = 0.0

        for _cid, cdata in sorted(consumer_map.items(), key=lambda x: x[1]['name']):
            lines.append(f"👤 {cdata['name']}:")
            person_bottles = 0
            person_cost = 0.0
            for _pid, pdata in sorted(cdata['products'].items(), key=lambda x: x[1]['name']):
                emoji = '🍺' if pdata['is_alcoholic'] else '🥤'
                subtotal = pdata['count'] * pdata['price']
                lines.append(
                    f"  {emoji} {pdata['name']} × {pdata['count']} = "
                    f"{self._fmt_eur(subtotal)}"
                )
                person_bottles += pdata['count']
                person_cost += subtotal
                if pdata['is_alcoholic']:
                    total_alc_brutto += subtotal
                else:
                    total_free_brutto += subtotal
            lines.append(f"  Σ {person_bottles} Fl. = {self._fmt_eur(person_cost)}")
            lines.append("")
            grand_bottles += person_bottles
            grand_cost += person_cost

        # MwSt breakdown
        alc_netto = round(total_alc_brutto / 1.19, 2)
        alc_mwst = round(total_alc_brutto - alc_netto, 2)
        free_netto = round(total_free_brutto / 1.07, 2)
        free_mwst = round(total_free_brutto - free_netto, 2)

        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append(f"📊 GESAMT: {grand_bottles} Fl. = {self._fmt_eur(grand_cost)}")
        lines.append("")
        lines.append(
            f"🍺 Alkoholisch: {self._fmt_eur(total_alc_brutto)} "
            f"(netto {self._fmt_eur(alc_netto)} + {self._fmt_eur(alc_mwst)} MwSt 19%)"
        )
        lines.append(
            f"💧 Alkoholfrei:  {self._fmt_eur(total_free_brutto)} "
            f"(netto {self._fmt_eur(free_netto)} + {self._fmt_eur(free_mwst)} MwSt 7%)"
        )

        # CSV backup status
        backup_ok = self.cron_backup_consumption_neutral()
        lines.append("")
        lines.append(f"🗄 DB-Backup: {'✅ CSV geschrieben' if backup_ok else '❌ Fehler'}")

        message_text = "\n".join(lines)

        # Send via Telegram Bot API
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = json.dumps({
            'chat_id': chat_id,
            'text': message_text,
            'parse_mode': '',  # plain text, emoji render natively
        }).encode('utf-8')

        req = urllib.request.Request(
            url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_body = resp.read().decode('utf-8')
                _logger.info("Telegram daily summary sent successfully. Response: %s", resp_body)
            self.env['frawo.agent.log'].sudo().create({
                'name': 'Telegram Tagesbericht',
                'level': 'info',
                'message': f'Tagesbericht erfolgreich an Chat {chat_id} gesendet.\n\n{message_text}',
            })
            return True
        except Exception as e:
            _logger.error("Telegram daily summary failed: %s", e)
            self.env['frawo.agent.log'].sudo().create({
                'name': 'Telegram Tagesbericht Fehler',
                'level': 'error',
                'message': f'Telegram-Versand fehlgeschlagen: {e}',
            })
            return False

    # ──────────────────────────────────────────────
    #  2. Enhanced Backup (CSV + JSON snapshot)
    # ──────────────────────────────────────────────

    @api.model
    def cron_backup_consumption_neutral(self):
        """Daily cron job to backup consumption statistics to CSV and a JSON snapshot."""
        import csv
        from datetime import datetime

        data_dir = self._get_data_dir()
        file_path = os.path.join(data_dir, 'consumption_neutral.csv')
        file_exists = os.path.exists(file_path)

        products = self.env['anker.tracker.product'].search([])
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        rows = []
        snapshot_products = []

        for product in products:
            unbilled_count = self.search_count([('product_id', '=', product.id), ('billed', '=', False)])
            billed_count = self.search_count([('product_id', '=', product.id), ('billed', '=', True)])
            total_count = unbilled_count + billed_count
            price = product.price_per_bottle or 0.0
            row = {
                'Date': now_str,
                'Product ID': product.id,
                'Product Name': product.name,
                'Manufacturer': product.manufacturer or '',
                'Crate Size': product.crate_size,
                'Price Per Bottle': f"{price:.2f}",
                'Total Consumed Bottles': total_count,
                'Billed Bottles': billed_count,
                'Unbilled Bottles': unbilled_count,
                'Unbilled Cost': f"{unbilled_count * price:.2f}",
                'Billed Cost': f"{billed_count * price:.2f}",
            }
            rows.append(row)
            snapshot_products.append({
                'product_id': product.id,
                'product_name': product.name,
                'manufacturer': product.manufacturer or '',
                'is_alcoholic': product.is_alcoholic,
                'volume': product.volume,
                'crate_size': product.crate_size,
                'price_per_bottle': price,
                'total_consumed': total_count,
                'billed': billed_count,
                'unbilled': unbilled_count,
                'unbilled_cost': round(unbilled_count * price, 2),
                'billed_cost': round(billed_count * price, 2),
            })

        fieldnames = [
            'Date', 'Product ID', 'Product Name', 'Manufacturer',
            'Crate Size', 'Price Per Bottle',
            'Total Consumed Bottles', 'Billed Bottles', 'Unbilled Bottles',
            'Unbilled Cost', 'Billed Cost',
        ]

        try:
            # CSV backup (append)
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(rows)

            # JSON daily snapshot
            date_tag = now.strftime('%Y-%m-%d')
            json_path = os.path.join(data_dir, f'consumption_daily_snapshot_{date_tag}.json')

            # Build per-consumer detail for snapshot
            consumers = self.env['anker.tracker.consumer'].search([('active', '=', True)])
            consumer_snapshot = []
            for consumer in consumers:
                recs = self.search([('consumer_id', '=', consumer.id), ('billed', '=', False)])
                prod_counts = {}
                for rec in recs:
                    pid = rec.product_id.id
                    if pid not in prod_counts:
                        prod_counts[pid] = {
                            'product_id': pid,
                            'product_name': rec.product_id.name,
                            'is_alcoholic': rec.product_id.is_alcoholic,
                            'price_per_bottle': rec.product_id.price_per_bottle or 0.0,
                            'count': 0,
                        }
                    prod_counts[pid]['count'] += 1
                if prod_counts:
                    consumer_snapshot.append({
                        'consumer_id': consumer.id,
                        'consumer_name': consumer.name,
                        'items': list(prod_counts.values()),
                    })

            snapshot = {
                'timestamp': now_str,
                'products': snapshot_products,
                'consumers_unbilled': consumer_snapshot,
            }
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump(snapshot, jf, ensure_ascii=False, indent=2)

            self.env['frawo.agent.log'].sudo().create({
                'name': 'Anker Tracker Backup',
                'level': 'info',
                'message': (
                    f'Tägliches Backup erfolgreich.\n'
                    f'  CSV: {file_path}\n'
                    f'  JSON: {json_path}'
                ),
            })
            return True
        except Exception as e:
            self.env['frawo.agent.log'].sudo().create({
                'name': 'Anker Tracker Backup Fehler',
                'level': 'error',
                'message': f'Fehler beim Schreiben des Backups: {e}',
            })
            return False

    # ──────────────────────────────────────────────
    #  3. Purchase Billing Summary (read-only)
    # ──────────────────────────────────────────────

    @api.model
    def generate_purchase_summary(self):
        """Return a dict summarising unbilled consumption with MwSt breakdown.

        This is read-only – it does NOT mark anything as billed.
        """
        unbilled = self.search([('billed', '=', False)])
        if not unbilled:
            return {
                'items_alc': [],
                'items_free': [],
                'total_alc_brutto': 0.0,
                'total_alc_netto': 0.0,
                'total_alc_mwst': 0.0,
                'total_free_brutto': 0.0,
                'total_free_netto': 0.0,
                'total_free_mwst': 0.0,
                'grand_total_brutto': 0.0,
                'grand_total_netto': 0.0,
                'grand_total_mwst': 0.0,
                'date_range': '',
            }

        # Aggregate by product
        product_agg = {}  # product.id → {…}
        earliest = None
        latest = None
        for rec in unbilled:
            pid = rec.product_id.id
            if pid not in product_agg:
                p = rec.product_id
                product_agg[pid] = {
                    'name': p.name,
                    'manufacturer': p.manufacturer or '',
                    'is_alcoholic': p.is_alcoholic,
                    'bottles_per_crate': p.crate_size or 1,
                    'unit_price': p.price_per_bottle or 0.0,
                    'count': 0,
                }
            product_agg[pid]['count'] += 1
            ts = rec.timestamp
            if ts:
                if earliest is None or ts < earliest:
                    earliest = ts
                if latest is None or ts > latest:
                    latest = ts

        items_alc = []
        items_free = []
        total_alc_brutto = 0.0
        total_free_brutto = 0.0

        for _pid, agg in sorted(product_agg.items(), key=lambda x: x[1]['name']):
            crate_size = agg['bottles_per_crate']
            crates = agg['count'] // crate_size
            loose = agg['count'] % crate_size
            subtotal = round(agg['count'] * agg['unit_price'], 2)
            item = {
                'name': agg['name'],
                'manufacturer': agg['manufacturer'],
                'count': agg['count'],
                'bottles_per_crate': crate_size,
                'crates': crates,
                'loose': loose,
                'unit_price': agg['unit_price'],
                'subtotal': subtotal,
            }
            if agg['is_alcoholic']:
                items_alc.append(item)
                total_alc_brutto += subtotal
            else:
                items_free.append(item)
                total_free_brutto += subtotal

        total_alc_brutto = round(total_alc_brutto, 2)
        total_free_brutto = round(total_free_brutto, 2)
        total_alc_netto = round(total_alc_brutto / 1.19, 2)
        total_alc_mwst = round(total_alc_brutto - total_alc_netto, 2)
        total_free_netto = round(total_free_brutto / 1.07, 2)
        total_free_mwst = round(total_free_brutto - total_free_netto, 2)

        grand_total_brutto = round(total_alc_brutto + total_free_brutto, 2)
        grand_total_netto = round(total_alc_netto + total_free_netto, 2)
        grand_total_mwst = round(total_alc_mwst + total_free_mwst, 2)

        # Date range string
        date_range = ''
        if earliest and latest:
            fmt = '%d.%m.%Y %H:%M'
            date_range = f"{earliest.strftime(fmt)} – {latest.strftime(fmt)}"
        elif earliest:
            date_range = earliest.strftime('%d.%m.%Y %H:%M')

        return {
            'items_alc': items_alc,
            'items_free': items_free,
            'total_alc_brutto': total_alc_brutto,
            'total_alc_netto': total_alc_netto,
            'total_alc_mwst': total_alc_mwst,
            'total_free_brutto': total_free_brutto,
            'total_free_netto': total_free_netto,
            'total_free_mwst': total_free_mwst,
            'grand_total_brutto': grand_total_brutto,
            'grand_total_netto': grand_total_netto,
            'grand_total_mwst': grand_total_mwst,
            'date_range': date_range,
        }

    # ──────────────────────────────────────────────
    #  4. Bill Now (enhanced – logs summary first)
    # ──────────────────────────────────────────────

    @api.model
    def bill_now(self):
        """Mark all unbilled records as billed.

        Before marking, generates and logs the purchase summary JSON
        so there is an auditable record of what was billed.
        Returns dict with status and count.
        """
        unbilled = self.search([('billed', '=', False)])
        count = len(unbilled)
        if not count:
            return {'status': 'success', 'count': 0}

        # Generate summary BEFORE marking as billed
        summary = self.generate_purchase_summary()

        # Log the summary
        self.env['frawo.agent.log'].sudo().create({
            'name': 'Anker Tracker Abrechnung',
            'level': 'info',
            'message': (
                f'Abrechnung über {count} Buchungen.\n'
                f'Zeitraum: {summary.get("date_range", "–")}\n'
                f'Gesamt brutto: {self._fmt_eur(summary["grand_total_brutto"])}\n'
                f'  Alkoholisch: {self._fmt_eur(summary["total_alc_brutto"])} '
                f'(netto {self._fmt_eur(summary["total_alc_netto"])} + '
                f'{self._fmt_eur(summary["total_alc_mwst"])} MwSt 19%)\n'
                f'  Alkoholfrei: {self._fmt_eur(summary["total_free_brutto"])} '
                f'(netto {self._fmt_eur(summary["total_free_netto"])} + '
                f'{self._fmt_eur(summary["total_free_mwst"])} MwSt 7%)\n\n'
                f'--- JSON ---\n{json.dumps(summary, ensure_ascii=False, indent=2)}'
            ),
        })

        # Mark as billed
        unbilled.write({'billed': True})

        # Trigger backup after billing
        self.cron_backup_consumption_neutral()

        _logger.info("Anker Tracker: Billed %s consumption records.", count)
        return {'status': 'success', 'count': count}
