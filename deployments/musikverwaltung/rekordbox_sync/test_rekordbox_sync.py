from rekordbox_sync import read_rekordbox_playlists


def test_read_rekordbox_playlists_returns_existing_playlist():
    result = read_rekordbox_playlists()
    assert isinstance(result, dict)
    # Aus der Grundausruestung wissen wir: mindestens die 4 Radio-Kanaele
    # unter "Radio (Import 2026-08-17)" muessen existieren und Titel enthalten.
    all_names = list(result.keys())
    assert len(all_names) > 0
    first_playlist_tracks = result[all_names[0]]
    assert all(p.upper().startswith("M:") for p in first_playlist_tracks)


def test_rekordbox_path_to_azuracast_translates_correctly():
    from rekordbox_sync import rekordbox_path_to_azuracast
    # Bestaetigte Regel (siehe README.md): M:\ ist direkt die Wurzel,
    # kein Master_Library-Praefix.
    result = rekordbox_path_to_azuracast(
        r"M:\Curated_Playlists\Ch1_Acoustik_Ambient\Track.flac"
    )
    assert result == "Curated_Playlists/Ch1_Acoustik_Ambient/Track.flac"


def test_sync_creates_or_updates_playlist_and_verifies_count():
    from rekordbox_sync import sync_to_azuracast
    # Nutzt eine harmlose Testplaylist statt einer echten Sende-Playlist
    result = sync_to_azuracast({"Sync-Test-Playlist": [
        r"M:\Curated_Playlists\Ch1_Acoustik_Ambient\Mac Miller - Stoned.flac",
    ]})
    assert result["Sync-Test-Playlist"]["gesendet"] == 1
    assert result["Sync-Test-Playlist"]["bestaetigt"] == 1
