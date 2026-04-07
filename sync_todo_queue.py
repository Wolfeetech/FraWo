from odoo_masterplan_sync import main


if __name__ == "__main__":
    print("Hinweis: sync_todo_queue.py ist jetzt nur noch ein Wrapper fuer den kanonischen Sync.")
    raise SystemExit(main(["--apply"]))
