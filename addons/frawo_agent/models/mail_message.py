import html
import re
from odoo import api, models


def _sanitize_escaped_html(body):
    if not body or not isinstance(body, str):
        return body
    if '&lt;' in body and any(
        tag in body
        for tag in (
            '&lt;p&gt;',
            '&lt;b&gt;',
            '&lt;ul&gt;',
            '&lt;li&gt;',
            '&lt;code&gt;',
            '&lt;i&gt;',
            '&lt;div&gt;',
            '&lt;span&gt;',
        )
    ):
        unescaped = html.unescape(body)
        match = re.match(
            r'^\s*<p>\s*(<(?:p|div|ul|ol|table|h[1-6]).*>.*</(?:p|div|ul|ol|table|h[1-6])>)\s*</p>\s*$',
            unescaped,
            flags=re.DOTALL,
        )
        if match:
            unescaped = match.group(1)
        return unescaped
    return body


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'body' in vals and vals.get('body'):
                vals['body'] = _sanitize_escaped_html(vals['body'])
        return super().create(vals_list)

    def write(self, vals):
        if 'body' in vals and vals.get('body'):
            vals['body'] = _sanitize_escaped_html(vals['body'])
        return super().write(vals)
