from odoo import models, fields, api
import requests
import logging
import random
import string
import urllib3

# Suppress insecure certificate warnings for internal API call
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    has_radio_access = fields.Boolean(
        string="FraWo Funk Zugang",
        default=True,
        help="Ermöglicht dem Benutzer das Wünschen von Songs und Interaktion im Radio."
    )

    @api.model
    def _cron_sync_azuracast_users(self):
        _logger.info("Starting Odoo-AzuraCast User Synchronization...")
        
        # Fetch configurations from System Parameters
        get_param = self.env['ir.config_parameter'].sudo().get_param
        base_url = get_param('frawo_agent.azuracast_api_url', 'https://10.1.0.38').rstrip('/')
        api_key = get_param('frawo_agent.azuracast_api_key', '')
        
        api_url = f"{base_url}/api/admin/users"
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        # 1. Fetch all users from AzuraCast
        try:
            r = requests.get(api_url, headers=headers, verify=False, timeout=10)
            if r.status_code != 200:
                _logger.error("Failed to fetch users from AzuraCast (status %s): %s", r.status_code, r.text)
                return
            az_users = r.json()
        except Exception as e:
            _logger.error("Error connecting to AzuraCast API: %s", str(e))
            return
            
        az_emails = {u.get("email", "").lower().strip() for u in az_users if u.get("email")}
        _logger.info("Found %s active users in AzuraCast.", len(az_emails))
        
        # 2. Fetch Odoo users (excluding public/portals that are inactive, and matching active emails)
        # We only sync users with a valid email who are not the public/guest template
        odoo_users = self.search([
            ("email", "!=", False),
            ("share", "=", True), # portal users
            ("active", "=", True)
        ])
        
        # Also include Wolf / internal staff who might want access
        staff_users = self.search([
            ("email", "!=", False),
            ("login", "in", ["wolf@frawo.tech", "wolf@frawo-tech.de"]),
            ("active", "=", True)
        ])
        
        users_to_sync = odoo_users | staff_users
        
        for user in users_to_sync:
            email = user.email.lower().strip()
            if not email:
                continue
                
            # If user does not exist in AzuraCast, create them
            if email not in az_emails:
                _logger.info("Creating user %s (%s) in AzuraCast...", user.name, email)
                
                # Generate a secure random password for the AzuraCast account
                chars = string.ascii_letters + string.digits + "!@#$%^&*"
                rand_password = "".join(random.choice(chars) for _ in range(16))
                
                payload = {
                    "email": email,
                    "authPassword": rand_password,
                    "name": user.name,
                    "timezone": "Europe/Berlin",
                    "locale": "de_DE",
                    "theme": "dark",
                    "roles": [] # Default listener roles
                }
                
                try:
                    res = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
                    if res.status_code in [200, 201]:
                        _logger.info("Successfully created AzuraCast user for %s", email)
                    else:
                        _logger.error("Failed to create AzuraCast user for %s (status %s): %s", email, res.status_code, res.text)
                except Exception as e:
                    _logger.error("Exception during user creation in AzuraCast for %s: %s", email, str(e))
            else:
                # User exists - we could sync password or rights if needed,
                # but since we authenticate via Odoo session on the frontend,
                # the Odoo login handles the frontend auth.
                pass
                
        _logger.info("Odoo-AzuraCast User Synchronization completed.")
