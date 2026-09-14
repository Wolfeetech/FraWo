"""
FraWo Funk - Ingest Rescued Master FLACs into Beets & Curated Radio Shows

1. Moves 52 validated FLAC tracks from /mnt/music/_GERETTET_aus_Quarantaene
   into /mnt/music/Master_Library/<Genre>/<Artist>/...
2. Updates SQLite /var/lib/beets/musik.db paths for all moved tracks.
3. Creates curated symbolic links in /mnt/music/Curated_Playlists/ for FraWo Radio shows.
4. Removes temporary _GERETTET_aus_Quarantaene directory once empty.
"""
import os
import shutil
import sqlite3
import subprocess
import sys

BASE_SRC = "/mnt/music/_GERETTET_aus_Quarantaene"
BASE_DST = "/mnt/music/Master_Library"
BASE_SHOWS = "/mnt/music/Curated_Playlists"
BEETS_DB = "/var/lib/beets/musik.db"

TRACK_MAPPINGS = {
    # Gemi
    "01. Gemi - Buggin.flac": "Electronic/Gemi/Einzeltitel/01. Gemi - Buggin.flac",
    "02. Gemi - Together.flac": "Electronic/Gemi/Einzeltitel/02. Gemi - Together.flac",
    # Actual Life 3
    "01. January 1st 2022.flac": "Electronic/Fred again../Actual Life 3/01. January 1st 2022.flac",
    "02. Eyelar (shutters).flac": "Electronic/Fred again../Actual Life 3/02. Eyelar (shutters).flac",
    "03. Delilah (pull me out of this).flac": "Electronic/Fred again../Actual Life 3/03. Delilah (pull me out of this).flac",
    "04. Kammy (like i do).flac": "Electronic/Fred again../Actual Life 3/04. Kammy (like i do).flac",
    "05. Berwyn (all that i got is you).flac": "Electronic/Fred again../Actual Life 3/05. Berwyn (all that i got is you).flac",
    "06. Bleu (better with time).flac": "Electronic/Fred again../Actual Life 3/06. Bleu (better with time).flac",
    "07. Nathan (still breathing).flac": "Electronic/Fred again../Actual Life 3/07. Nathan (still breathing).flac",
    "08. Danielle (smile on my face).flac": "Electronic/Fred again../Actual Life 3/08. Danielle (smile on my face).flac",
    "09. Kelly (end of a nightmare).flac": "Electronic/Fred again../Actual Life 3/09. Kelly (end of a nightmare).flac",
    "10. Mustafa (time to move you).flac": "Electronic/Fred again../Actual Life 3/10. Mustafa (time to move you).flac",
    "11. Clara (the night is dark).flac": "Electronic/Fred again../Actual Life 3/11. Clara (the night is dark).flac",
    "12. Winnie (end of me).flac": "Electronic/Fred again../Actual Life 3/12. Winnie (end of me).flac",
    "13. September 9th 2022.flac": "Electronic/Fred again../Actual Life 3/13. September 9th 2022.flac",
    # Other Fred again..
    "11 - Turn On The Lights again.. (feat. Future).flac": "Electronic/Fred again../USB/11 - Turn On The Lights again.. (feat. Future).flac",
    "Fred again.., Sammy Virji, Reggie - Talk of the Town - 1 - Talk of the Town.flac": "Electronic/Fred again../Einzeltitel/Fred again.., Sammy Virji, Reggie - Talk of the Town.flac",
    "Fred again. - two more days - 01 - light dark light.flac": "Electronic/Fred again../two more days/Fred again. - two more days - 01 - light dark light.flac",
    "Fred again. - two more days - 02 - little mystery.flac": "Electronic/Fred again../two more days/Fred again. - two more days - 02 - little mystery.flac",
    # ten days album
    "Fred again. - ten days - 01 - one.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 01 - one.flac",
    "Fred again. - ten days - 02 - adore u.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 02 - adore u.flac",
    "Fred again. - ten days - 03 - two.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 03 - two.flac",
    "Fred again. - ten days - 04 - ten.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 04 - ten.flac",
    "Fred again. - ten days - 05 - three.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 05 - three.flac",
    "Fred again. - ten days - 06 - fear less.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 06 - fear less.flac",
    "Fred again. - ten days - 08 - just stand there.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 08 - just stand there.flac",
    "Fred again. - ten days - 09 - five.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 09 - five.flac",
    "Fred again. - ten days - 10 - places to be.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 10 - places to be.flac",
    "Fred again. - ten days - 11 - six.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 11 - six.flac",
    "Fred again. - ten days - 12 - glow.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 12 - glow.flac",
    "Fred again. - ten days - 13 - seven.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 13 - seven.flac",
    "Fred again. - ten days - 14 - i saw you.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 14 - i saw you.flac",
    "Fred again. - ten days - 15 - eight.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 15 - eight.flac",
    "Fred again. - ten days - 16 - where will i be.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 16 - where will i be.flac",
    "Fred again. - ten days - 17 - nine.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 17 - nine.flac",
    "Fred again. - ten days - 18 - peace u need.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 18 - peace u need.flac",
    "Fred again. - ten days - 19 - ten.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 19 - ten.flac",
    "Fred again. - ten days - 20 - backseat.flac": "Electronic/Fred again../ten days/Fred again. - ten days - 20 - backseat.flac",
    # Singles & Collaborations
    "04 Nella - Why Can't I Remember feat. Exit 47.flac": "House/Nella/Einzeltitel/Nella - Why Can't I Remember feat. Exit 47.flac",
    "05 Seasons.flac": "Electronic/Lil Silva/Einzeltitel/Lil Silva - Seasons.flac",
    "11. Oppidan - Mr. Sandman.flac": "Electronic/Oppidan/Einzeltitel/Oppidan - Mr. Sandman.flac",
    "12. Sammy Virji, Flowdan - Sheila Verse.flac": "House/Sammy Virji/Einzeltitel/Sammy Virji, Flowdan - Sheila Verse.flac",
    "Adam Pits, Space Cadets, Lisene - Warp Drive.flac": "Electronic/Adam Pits/Einzeltitel/Adam Pits, Space Cadets, Lisene - Warp Drive.flac",
    "Andre Zimmer - Synthetic Station (Jex Opolis Remix).flac": "House/Andre Zimmer/Einzeltitel/Andre Zimmer - Synthetic Station (Jex Opolis Remix).flac",
    "BLND (UK) - UR LUV (Original Mix)www.electronicfresh.com.flac": "House/BLND/Einzeltitel/BLND (UK) - UR LUV (Original Mix).flac",
    "Bullet Tooth - Bounce.flac": "House/Bullet Tooth/Einzeltitel/Bullet Tooth - Bounce.flac",
    "Disclosure - one2three - 01 - one2three.flac": "House/Disclosure/Einzeltitel/Disclosure - one2three.flac",
    "Fast Eddie, Andre Zimmer - Yo Yo Get Funky (Andre Zimmer Extended Remix).flac": "House/Andre Zimmer/Einzeltitel/Fast Eddie, Andre Zimmer - Yo Yo Get Funky (Andre Zimmer Extended Remix).flac",
    "Sammy Virji - If U Need It (Extended Mix).flac": "House/Sammy Virji/Einzeltitel/Sammy Virji - If U Need It (Extended Mix).flac",
    "Sammy Virji, Skepta - Cops & Robbers.flac": "House/Sammy Virji/Einzeltitel/Sammy Virji, Skepta - Cops & Robbers.flac",
    "test_01 - Faithless - Insomnia.flac": "Electronic/Faithless/Einzeltitel/Faithless - Insomnia.flac",
    "test_03 - One More Time (club mix).flac": "Electronic/Daft Punk/Einzeltitel/Daft Punk - One More Time (club mix).flac",
}

# Radio show assignments for curated rotation
SHOW_ASSIGNMENTS = {
    "04_Afternoon_Flow": [
        "Electronic/Fred again../ten days/Fred again. - ten days - 02 - adore u.flac",
        "Electronic/Fred again../ten days/Fred again. - ten days - 06 - fear less.flac",
        "Electronic/Fred again../ten days/Fred again. - ten days - 10 - places to be.flac",
        "Electronic/Fred again../Actual Life 3/03. Delilah (pull me out of this).flac",
        "Electronic/Fred again../Actual Life 3/06. Bleu (better with time).flac",
        "Electronic/Fred again../Actual Life 3/08. Danielle (smile on my face).flac",
        "Electronic/Fred again../Actual Life 3/05. Berwyn (all that i got is you).flac",
        "Electronic/Lil Silva/Einzeltitel/Lil Silva - Seasons.flac",
    ],
    "05_Evening_Warmup": [
        "House/Sammy Virji/Einzeltitel/Sammy Virji - If U Need It (Extended Mix).flac",
        "House/Sammy Virji/Einzeltitel/Sammy Virji, Skepta - Cops & Robbers.flac",
        "House/Sammy Virji/Einzeltitel/Sammy Virji, Flowdan - Sheila Verse.flac",
        "House/Disclosure/Einzeltitel/Disclosure - one2three.flac",
        "House/Andre Zimmer/Einzeltitel/Andre Zimmer - Synthetic Station (Jex Opolis Remix).flac",
        "House/Andre Zimmer/Einzeltitel/Fast Eddie, Andre Zimmer - Yo Yo Get Funky (Andre Zimmer Extended Remix).flac",
        "Electronic/Gemi/Einzeltitel/01. Gemi - Buggin.flac",
        "Electronic/Gemi/Einzeltitel/02. Gemi - Together.flac",
        "House/Bullet Tooth/Einzeltitel/Bullet Tooth - Bounce.flac",
        "Electronic/Oppidan/Einzeltitel/Oppidan - Mr. Sandman.flac",
    ],
    "07_Peak_Time_Club": [
        "Electronic/Daft Punk/Einzeltitel/Daft Punk - One More Time (club mix).flac",
        "Electronic/Faithless/Einzeltitel/Faithless - Insomnia.flac",
        "Electronic/Fred again../Einzeltitel/Fred again.., Sammy Virji, Reggie - Talk of the Town.flac",
        "Electronic/Fred again../USB/11 - Turn On The Lights again.. (feat. Future).flac",
        "Electronic/Adam Pits/Einzeltitel/Adam Pits, Space Cadets, Lisene - Warp Drive.flac",
    ],
    "08_Sunday_Roadtrip": [
        "Electronic/Fred again../ten days/Fred again. - ten days - 20 - backseat.flac",
        "Electronic/Fred again../ten days/Fred again. - ten days - 18 - peace u need.flac",
        "Electronic/Fred again../ten days/Fred again. - ten days - 12 - glow.flac",
        "Electronic/Fred again../two more days/Fred again. - two more days - 01 - light dark light.flac",
        "Electronic/Fred again../two more days/Fred again. - two more days - 02 - little mystery.flac",
    ]
}


def run():
    print(f"=== Starting Ingestion of {len(TRACK_MAPPINGS)} Rescued FLACs ===")
    conn = sqlite3.connect(BEETS_DB)
    c = conn.cursor()

    moved_count = 0
    for src_name, rel_dst in TRACK_MAPPINGS.items():
        src_path = os.path.join(BASE_SRC, src_name)
        dst_path = os.path.join(BASE_DST, rel_dst)

        if not os.path.exists(src_path):
            print(f"Warning: {src_path} not found on disk, skipping.")
            continue

        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.move(src_path, dst_path)
        moved_count += 1

        # Update Beets DB item path
        dst_bytes = dst_path.encode("utf-8")
        src_bytes = src_path.encode("utf-8")
        c.execute("UPDATE items SET path = ? WHERE path = ? OR path LIKE ?;",
                  (dst_bytes, src_bytes, b"%" + src_name.encode("utf-8")))

    conn.commit()
    print(f"Successfully moved {moved_count} tracks into Master_Library and updated Beets DB.")

    # Create Symlinks for Radio Shows
    symlinks_count = 0
    for show_name, rel_paths in SHOW_ASSIGNMENTS.items():
        show_dir = os.path.join(BASE_SHOWS, show_name)
        os.makedirs(show_dir, exist_ok=True)
        for rel_p in rel_paths:
            target_path = os.path.join(BASE_DST, rel_p)
            link_name = os.path.basename(target_path)
            link_path = os.path.join(show_dir, link_name)

            if os.path.lexists(link_path):
                try:
                    os.remove(link_path)
                except Exception:
                    pass

            if os.path.exists(target_path):
                os.symlink(target_path, link_path)
                symlinks_count += 1
            else:
                print(f"Warning: Target {target_path} does not exist for symlink {link_path}")

    print(f"Successfully created {symlinks_count} show symlinks across {len(SHOW_ASSIGNMENTS)} shows.")

    # Clean up quarantine directory if empty
    remaining_files = [f for f in os.listdir(BASE_SRC) if not f.startswith(".")]
    if not remaining_files:
        os.rmdir(BASE_SRC)
        print(f"Removed empty quarantine directory: {BASE_SRC}")
    else:
        print(f"Note: {len(remaining_files)} remaining items in {BASE_SRC}: {remaining_files}")

    print("=== Ingestion Completed Successfully ===")


if __name__ == "__main__":
    run()
