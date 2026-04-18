import base64

# IDs
COMPANY_ID = 1
WEBSITE_ID = 1

def update_branding():
    try:
        # 1. Load Images
        with open('/tmp/frawo_logo.png', 'rb') as f:
            logo_data = base64.b64encode(f.read())
        
        with open('/tmp/frawo_hero.png', 'rb') as f:
            hero_data = base64.b64encode(f.read())

        # 2. Update Company
        company = env['res.company'].browse(COMPANY_ID)
        company.write({
            'name': 'FraWo GbR',
            'company_registry': 'Homeserver 2027 Infrastructure',
            'report_header': 'FraWo GbR - Souveräne IT-Infrastruktur',
            'logo': logo_data,
        })
        print(f"Updated Company: {company.name}")

        # 3. Update Website
        website = env['website'].browse(WEBSITE_ID)
        website.write({
            'social_twitter': 'https://twitter.com/frawo',
            'social_facebook': 'https://facebook.com/frawo',
            'social_linkedin': 'https://linkedin.com/company/frawo',
            'logo': logo_data,
        })
        print(f"Updated Website Logo and Social Links")

        # 4. Update Website Slogan (Company-wide if possible)
        # Note: In some versions this is tied to the website record
        env.cr.execute("UPDATE website SET name = 'FraWo GbR' WHERE id = %s", (WEBSITE_ID,))

        # 5. Homepage Content "Injection" 
        # We target the 'website.homepage' and look for blocks.
        # This is a bit advanced via shell, so we focus on the visible metadata first.
        
        env.cr.commit()
        print("Branding injection completed successfully.")
        
    except Exception as e:
        print(f"Error during injection: {e}")
        env.cr.rollback()

update_branding()
