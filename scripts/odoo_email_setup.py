#!/usr/bin/env python3
"""
Odoo Sender Email Configuration Setup

This script helps configure the sender email address in Odoo to fix the
"Invalid Operation: Message cannot be sent, please configure sender email" error.

Usage:
    python scripts/odoo_email_setup.py

Requirements:
    - Odoo XML-RPC API access
    - Admin credentials

Stand: 2026-04-22
"""

import xmlrpc.client
import getpass
import sys
from typing import Optional, Dict, Any


class OdooEmailSetup:
    """Configure Odoo sender email settings via XML-RPC API"""

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid: Optional[int] = None
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    def authenticate(self) -> bool:
        """Authenticate with Odoo"""
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                print(f"✅ Authenticated as user ID: {self.uid}")
                return True
            else:
                print("❌ Authentication failed - invalid credentials")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def get_company_info(self) -> Optional[Dict[str, Any]]:
        """Get current company information"""
        try:
            companies = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.company', 'search_read',
                [[]], {'fields': ['name', 'email', 'phone'], 'limit': 1}
            )
            if companies:
                return companies[0]
            return None
        except Exception as e:
            print(f"❌ Error fetching company info: {e}")
            return None

    def set_company_email(self, email: str) -> bool:
        """Set company email address"""
        try:
            company_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.company', 'search',
                [[]], {'limit': 1}
            )

            if not company_id:
                print("❌ No company found")
                return False

            self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.company', 'write',
                [company_id, {'email': email}]
            )
            print(f"✅ Company email set to: {email}")
            return True
        except Exception as e:
            print(f"❌ Error setting company email: {e}")
            return False

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user information"""
        try:
            users = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.users', 'search_read',
                [[('id', '=', self.uid)]], {'fields': ['name', 'login', 'email']}
            )
            if users:
                return users[0]
            return None
        except Exception as e:
            print(f"❌ Error fetching user info: {e}")
            return None

    def set_user_email(self, email: str) -> bool:
        """Set user email address"""
        try:
            self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.users', 'write',
                [[self.uid], {'email': email}]
            )
            print(f"✅ User email set to: {email}")
            return True
        except Exception as e:
            print(f"❌ Error setting user email: {e}")
            return False

    def test_mail_server(self) -> bool:
        """Test outgoing mail server connection"""
        try:
            # Get mail servers
            mail_servers = self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.mail_server', 'search_read',
                [[]], {'fields': ['name', 'smtp_host', 'smtp_port', 'smtp_user']}
            )

            if not mail_servers:
                print("⚠️  No mail servers configured")
                return False

            print("\n📧 Configured Mail Servers:")
            for server in mail_servers:
                print(f"   - {server['name']}: {server['smtp_host']}:{server['smtp_port']}")
                print(f"     User: {server['smtp_user']}")

            return True
        except Exception as e:
            print(f"❌ Error checking mail servers: {e}")
            return False


def main():
    """Main setup workflow"""
    print("=" * 60)
    print("Odoo Sender Email Configuration Setup")
    print("=" * 60)
    print()

    # Configuration
    url = input("Odoo URL [http://odoo.hs27.internal]: ").strip() or "http://odoo.hs27.internal"
    db = input("Database name [odoo]: ").strip() or "odoo"
    username = input("Username [admin]: ").strip() or "admin"
    password = getpass.getpass("Password: ")

    print()
    print("Connecting to Odoo...")

    # Initialize setup
    setup = OdooEmailSetup(url, db, username, password)

    # Authenticate
    if not setup.authenticate():
        sys.exit(1)

    print()
    print("-" * 60)
    print("Current Configuration")
    print("-" * 60)

    # Get current company info
    company = setup.get_company_info()
    if company:
        print(f"\n🏢 Company: {company['name']}")
        print(f"   Email: {company.get('email') or '(not set)'}")
        print(f"   Phone: {company.get('phone') or '(not set)'}")

    # Get current user info
    user = setup.get_user_info()
    if user:
        print(f"\n👤 User: {user['name']}")
        print(f"   Login: {user['login']}")
        print(f"   Email: {user.get('email') or '(not set)'}")

    # Check mail servers
    print()
    setup.test_mail_server()

    print()
    print("-" * 60)
    print("Configuration Steps")
    print("-" * 60)

    # Step 1: Set company email
    print("\n1️⃣  Set Company Email")
    company_email = input("   Company email [noreply@frawo-tech.de]: ").strip() or "noreply@frawo-tech.de"
    if setup.set_company_email(company_email):
        print("   ✅ Company email configured")
    else:
        print("   ⚠️  Failed to set company email")

    # Step 2: Set user email
    print("\n2️⃣  Set User Email")
    user_email = input("   User email [wolf@frawo-tech.de]: ").strip() or "wolf@frawo-tech.de"
    if setup.set_user_email(user_email):
        print("   ✅ User email configured")
    else:
        print("   ⚠️  Failed to set user email")

    print()
    print("=" * 60)
    print("✅ Configuration Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Test email sending in Odoo (Settings → Technical → Email → Send Email)")
    print("2. Try canceling a quote to verify the error is fixed")
    print("3. Check SMTP server connection in Odoo settings")
    print()
    print("Documentation: DOCS/ODOO_SENDER_EMAIL_FIX.md")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
