UPDATE ir_ui_view SET active = true, arch_db = '<?xml version="1.0"?>
<t name="Homepage" t-name="website.homepage">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty"></div>
    </t>
</t>' WHERE key = 'website.homepage';

UPDATE ir_ui_view SET active = true, arch_db = '<?xml version="1.0"?>
<t name="Contact us" t-name="website.contactus">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty"></div>
    </t>
</t>' WHERE key = 'website.contactus';

UPDATE ir_ui_view SET active = false, arch_db = '<style></style>' WHERE key = 'website.user_custom_css';
