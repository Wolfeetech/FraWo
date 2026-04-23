import os
import sys

def create_or_update_view(key, name, arch, is_page=False, url=None):
    View = env['ir.ui.view']
    Page = env['website.page']
    
    views = View.search([('key', '=', key)])
    if not views:
        print(f"Creating new view: {key}")
        view = View.create({
            'name': name,
            'key': key,
            'type': 'qweb',
            'arch_db': arch,
        })
    else:
        print(f"Updating existing views: {key}")
        for view in views:
            view.write({'arch_db': arch})
        view = views[0]

    if is_page and url:
        page = Page.search([('view_id', '=', view.id)], limit=1)
        if not page:
            print(f"Creating website.page for {url}")
            Page.create({
                'url': url,
                'view_id': view.id,
                'is_published': True,
                'website_indexed': True,
            })
        else:
            page.write({
                'url': url,
                'is_published': True,
            })

def deploy_website():
    print("Starting deployment of Website Redesign...")

    def ensure_image(name, b64_data):
        Attachment = env['ir.attachment']
        att = Attachment.search([('name', '=', name), ('res_model', '=', 'ir.ui.view')], limit=1)
        if not att:
            print(f"Uploading new image: {name}")
            att = Attachment.create({
                'name': name,
                'type': 'binary',
                'datas': b64_data,
                'public': True,
                'res_model': 'ir.ui.view',
                'mimetype': 'image/jpeg',
            })
        elif b64_data:
            att.write({'datas': b64_data})
        return f"/web/image/{att.id}"

    # Load contents
    # We will read these from the local file system on the StudioPC before sending this script.
    # Since this script runs INSIDE the container, we need to embed the strings directly.
    # The PowerShell wrapper will replace the placeholders.

    css_content = """__CSS_CONTENT__"""
    home_content = """__HOME_CONTENT__"""
    b2b_content = """__B2B_CONTENT__"""
    b2c_content = """__B2C_CONTENT__"""
    contact_content = """__CONTACT_CONTENT__"""

    # Images
    img_about_console = ensure_image("about-console.jpg", """__B64_ABOUT_CONSOLE__""")
    img_hero_bodensee = ensure_image("hero-bodensee.jpg", """__B64_HERO_BODENSEE__""")
    img_reference_event = ensure_image("reference-event.jpg", """__B64_REFERENCE_EVENT__""")
    img_service_audio = ensure_image("service-audio.jpg", """__B64_SERVICE_AUDIO__""")
    img_service_stage = ensure_image("service-stage.jpg", """__B64_SERVICE_STAGE__""")

    home_content = home_content.replace('__IMG_HERO_BODENSEE__', img_hero_bodensee).replace('__IMG_REFERENCE_EVENT__', img_reference_event).replace('__IMG_SERVICE_AUDIO__', img_service_audio)
    b2b_content = b2b_content.replace('__IMG_ABOUT_CONSOLE__', img_about_console)
    b2c_content = b2c_content.replace('__IMG_SERVICE_STAGE__', img_service_stage)

    # 1. Custom CSS
    css_arch = f"<style>\n{css_content}\n</style>"
    website = env['website'].search([], limit=1)
    if website:
        website.write({'custom_code_head': css_arch})
        print("Updated Custom CSS via website.custom_code_head.")
    else:
        create_or_update_view('website.user_custom_css', 'Custom CSS', css_arch)

    # 2. Homepage
    home_arch = f'<t name="Homepage" t-name="website.homepage">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty">\n            {home_content}\n        </div>\n    </t>\n</t>'
    create_or_update_view('website.homepage', 'Home', home_arch)

    # 3. B2C Page
    b2c_arch = f'<t name="Privatkunden" t-name="website.page_b2c">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty">\n            {b2c_content}\n        </div>\n    </t>\n</t>'
    create_or_update_view('website.page_b2c', 'Privatkunden', b2c_arch, is_page=True, url='/b2c')

    # 4. B2B Page
    b2b_arch = f'<t name="Business" t-name="website.page_b2b">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty">\n            {b2b_content}\n        </div>\n    </t>\n</t>'
    create_or_update_view('website.page_b2b', 'Business', b2b_arch, is_page=True, url='/b2b')

    # 5. Contact Us
    contact_arch = f'<t name="Contact Us" t-name="website.contactus">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty">\n            {contact_content}\n        </div>\n    </t>\n</t>'

    view = env['ir.ui.view'].search([('key', 'ilike', 'contactus')], limit=1)
    if view:
        view.write({'arch_db': contact_arch})
        print("Updated Contact Us.")
    else:
        create_or_update_view('website.contactus', 'Contact Us', contact_arch)

    # Update web.base.url just to be sure
    env['ir.config_parameter'].set_param('web.base.url', 'https://frawo-tech.de')

    env.cr.commit()
    print("Deployment completed successfully!")

deploy_website()
