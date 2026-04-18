import odoo_rpc_client

def apply_branding():
    print("--- Applying FraWo GbR Identity ---")
        
    try:
        session = odoo_rpc_client.connect(default_user="admin")
        
        branding_data = {
            'name': 'FraWo GbR',
            'email': 'info@frawo-tech.de',
            'website': 'https://www.frawo-tech.de',
            'primary_color': '#064e3b', # Deep Forest
            'secondary_color': '#a855f7' # UV Power
        }
        
        # Update the main company (usually ID 1)
        company_id = 1
        print(f"Updating company {company_id} with branding: {branding_data['name']}")
        
        session.models.execute_kw(
            session.db, session.uid, session.secret,
            'res.company', 'write', [[company_id], branding_data]
        )
        
        print("Branding applied successfully.")
        
    except Exception as e:
        print(f"Error applying branding: {e}")

if __name__ == "__main__":
    apply_branding()
