from odoo_masterplan_sync import main


if __name__ == "__main__":
    print("Hinweis: odoo_arch_upgrade.py ist jetzt nur noch ein Wrapper fuer den kanonischen Sync.")
    raise SystemExit(main(["--apply"]))
