# -*- coding: utf-8 -*-
import xmlrpc.client

url = 'http://172.21.0.3:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# IHK-Compliant Contact Page
arch_contact = """
<data name="Contact Us" inherit_id="website.contactus">
    <xpath expr="//div[@id='wrap']" position="replace">
        <div id="wrap" class="oe_structure oe_empty" style="background-color: #0d1117; color: #fff;">
            <section class="s_title py-5">
                <div class="container text-center">
                    <h1 style="font-weight: 800;">Lassen Sie uns starten.</h1>
                    <p class="lead">Für professionelle Personalanfragen im Bereich Eventtechnik oder technische Privat-Projekte.</p>
                </div>
            </section>
            <div class="container pb-5">
                <div class="row">
                    <div class="col-lg-8 offset-lg-2">
                        <div class="p-4 rounded shadow" style="background-color: #161b22; border: 1px solid #30363d;">
                             <p class="mb-4">Bitte kontaktieren Sie uns direkt unter <strong>info@frawo-tech.de</strong> oder nutzen Sie unser Projekt-Portal.</p>
                             <div class="text-center">
                                <a href="mailto:info@frawo-tech.de" class="btn btn-primary px-4">E-Mail senden</a>
                             </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </xpath>
</data>
"""

models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[3637], {'arch_db': arch_contact}])
print("Contact page updated.")
