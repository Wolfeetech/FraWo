# -*- coding: utf-8 -*-
import os, xmlrpc.client
from dotenv import load_dotenv

load_dotenv(r"C:\Users\StudioPC\.ai-tools-shared\.env")
url = os.getenv("ODOO_URL", "http://10.1.0.112:8069")
db = os.getenv("ODOO_DB_GBR", "FraWo_GbR")
pwd = os.getenv("ODOO_PASSWORD_ALT")

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)

arch = """<data>
    <xpath expr="//filter[@name='open_tasks']" position="before">
        <filter string="🎪 Event/Verleih" name="frawo_lane_event" domain="[('tag_ids', 'in', [149])]"/>
        <filter string="🧑‍🔧 Dienstleistung" name="frawo_lane_service" domain="[('tag_ids', 'in', [150])]"/>
        <filter string="🔨 Bauvorhaben" name="frawo_lane_craft" domain="[('tag_ids', 'in', [151])]"/>
        <filter string="🏢 Intern" name="frawo_lane_internal" domain="[('tag_ids', 'in', [152])]"/>
        <separator/>
        <filter string="🔥 Überfällig" name="frawo_overdue" domain="[('date_deadline', '&lt;', context_today().strftime('%%Y-%%m-%%d')), ('is_closed', '=', False)]"/>
        <filter string="⏰ Frist 7 Tage" name="frawo_deadline_7d" domain="[('date_deadline', '&gt;=', context_today().strftime('%%Y-%%m-%%d')), ('date_deadline', '&lt;=', (context_today() + datetime.timedelta(days=7)).strftime('%%Y-%%m-%%d')), ('is_closed', '=', False)]"/>
        <separator/>
    </xpath>
    <xpath expr="//group" position="inside">
        <filter string="Spur (Tags)" name="group_frawo_lane" context="{'group_by': 'tag_ids'}"/>
    </xpath>
    <xpath expr="//search" position="inside">
        <searchpanel>
            <field name="stage_id" icon="fa-tasks" select="multi" enable_counters="1"/>
        </searchpanel>
    </xpath>
</data>"""

models.execute_kw(db, 6, pwd, "ir.ui.view", "write", [[3453], {"arch_db": arch}])
print("Successfully wrote UTF-8 arch_db with searchpanel to view #3453!")
