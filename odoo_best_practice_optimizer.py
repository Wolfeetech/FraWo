from odoo_masterplan_sync import main


if __name__ == "__main__":
    print("Hinweis: odoo_best_practice_optimizer.py ist jetzt nur noch ein Wrapper fuer den kanonischen Sync.")
    raise SystemExit(main(["--apply"]))
