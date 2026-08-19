#!/usr/bin/env python3
# FraWo - Radio-Kurationspipeline (vereinfacht 19.08.2026)
#
# Vorher kopierte dieses Skript importierte Titel zusaetzlich nach
# /mnt/musicstick/yourparty.radio/<genre>/ - das war ein Ueberbleibsel
# des alten Raspberry-Pi-Aufbaus (vor der gemeinsamen beets-Bibliothek).
# AzuraCast liest seine Musik heute direkt aus //10.1.0.94/music
# (derselbe Datentraeger, den beets ueber /mnt/music_hdd verwaltet) -
# der Kopierschritt war seither nicht nur kaputt (Ziel war der
# gefaelschte, nicht eingehaengte USB-Stick), sondern auch unnoetig.
import os
import subprocess
import sys

def run_cmd(cmd_list):
    res = subprocess.run(cmd_list, capture_output=True, text=True, errors='ignore')
    return res.stdout, res.stderr

def run_pct(container_id, cmd_list):
    full_cmd = ["/usr/sbin/pct", "exec", str(container_id), "--"] + cmd_list
    return run_cmd(full_cmd)

def run_ssh_vm(vm_ip, cmd_string):
    full_cmd = ["/usr/bin/ssh", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", f"root@{vm_ip}", cmd_string]
    return run_cmd(full_cmd)

def main():
    inbox_radio_container = "/mnt/music/Inbox/Radio"
    inbox_radio_host = "/mnt/music_hdd/Inbox/Radio"

    print("--- Starting Radio Curation Pipeline ---")

    os.makedirs(inbox_radio_host, exist_ok=True)

    radio_files = [f for f in os.listdir(inbox_radio_host) if f != "." and f != ".."]

    if not radio_files:
        print("Inbox/Radio is empty. No new tracks to curate.")
        return

    print(f"Found new files/directories in Inbox/Radio. Starting beets import in fileserver (LXC 120)...")

    # 1. Beets standard autotag import
    import_out, import_err = run_pct(120, ["beet", "import", "-q", "-s", "--noresume", inbox_radio_container])
    print("Beets Autotag Import Output:")
    print(import_out)
    if import_err.strip():
        print("Beets Autotag Import Errors:")
        print(import_err)

    # Check if files still remain in Inbox/Radio (meaning autotag skipped them)
    remaining_files = [f for f in os.listdir(inbox_radio_host) if f != "." and f != ".."]
    if remaining_files:
        print(f"Some files could not be matched by beets. Running fallback non-autotagged import for remaining files...")
        fallback_out, fallback_err = run_pct(120, ["beet", "import", "-q", "-A", "-s", "--noresume", inbox_radio_container])
        print("Beets Fallback Import Output:")
        print(fallback_out)
        if fallback_err.strip():
            print("Beets Fallback Import Errors:")
            print(fallback_err)

    # 2. Confirm something was actually imported before triggering AzuraCast
    still_remaining = [f for f in os.listdir(inbox_radio_host) if f != "." and f != ".."]
    imported_count = len(radio_files) - len(still_remaining)

    if imported_count <= 0:
        print("No tracks were successfully imported by beets. Skipping AzuraCast rescan.")
        return

    print(f"{imported_count} track(s) imported into the shared library. "
          "AzuraCast reads the same storage directly - no copy step needed.")

    # 3. Trigger AzuraCast media rescan so it picks up the newly imported tracks
    print("Triggering AzuraCast media rescan...")
    scan_out, scan_err = run_ssh_vm("10.1.0.38", "docker exec azuracast azuracast_cli azuracast:media:reprocess frawo_funk")
    print("AzuraCast Rescan Output:")
    print(scan_out)
    if scan_err.strip():
        print("AzuraCast Rescan Errors:")
        print(scan_err)

    print("--- Radio Curation Pipeline Finished ---")

if __name__ == "__main__":
    main()
