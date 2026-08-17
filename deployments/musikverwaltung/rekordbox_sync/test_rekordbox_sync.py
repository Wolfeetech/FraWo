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
