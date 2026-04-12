# -*- coding: utf-8 -*-
import xmlrpc.client

url = 'http://172.21.0.3:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# IHK-Compliant Hybrid Footer
arch_footer = """
<data name="Footer Custom" inherit_id="website.footer_custom">
    <xpath expr="//div[@id='footer']" position="replace">
        <div id="footer" class="oe_structure oe_empty" style="background-color: #0d1117; color: #94a3b8; border-top: 1px solid #30363d; padding: 3rem 0;">
            <div class="container text-center">
                <p style="color: #fff; font-weight: 600;">FraWo &#x2014; Audiovisuelle Exzellenz &#x26; technischer Service</p>
                <p>Veranstaltungstechnik | Montage technischer Sonderbauten</p>
                <p>Heimkino | HiFi | Smart Living</p>
                <p class="mt-3">Wei&#xdf;ensberg | IHK-registriert</p>
                <div class="mt-4">
                    <a href="/" class="mx-2 text-decoration-none" style="color: #94a3b8;">Home</a>
                    <a href="/contactus" class="mx-2 text-decoration-none" style="color: #94a3b8;">Kontakt</a>
                </div>
                <p class="mt-4" style="font-size: 0.8rem;">&#xa9; 2026 FraWo GbR. Alle Rechte vorbehalten.</p>
            </div>
        </div>
    </xpath>
</data>
"""

models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[4405], {'arch_db': arch_footer}])
print("Footer updated.")
