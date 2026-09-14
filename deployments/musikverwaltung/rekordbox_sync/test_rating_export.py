from types import SimpleNamespace

import rating_export as re_


def _content(title, artist, rating=0, cid=1):
    return SimpleNamespace(ID=cid, Title=title, Artist=SimpleNamespace(Name=artist), Rating=rating)


def test_match_content_exact_and_case_insensitive():
    rows = [{"track_id": "Artist|Song", "artist": "Artist", "title": "Song", "stars": 5, "count": 2, "average": 4.5},
            {"track_id": "Nobody|Nothing", "artist": "Nobody", "title": "Nothing", "stars": 3, "count": 2, "average": 3.0}]
    contents = [_content("song", "ARTIST", cid=7)]
    matches, unmatched = re_.match_content(rows, contents)
    assert len(matches) == 1 and matches[0][1].ID == 7
    assert [r["track_id"] for r in unmatched] == ["Nobody|Nothing"]


def test_apply_ratings_sets_only_changed():
    c1 = _content("A", "X", rating=5, cid=1)
    c2 = _content("B", "X", rating=2, cid=2)
    matches = [({"stars": 5}, c1), ({"stars": 4}, c2)]
    changed = re_.apply_ratings(None, matches)
    assert changed == 1
    assert c2.Rating == 4 and c1.Rating == 5


def test_rekordbox_running_detects_process_name():
    assert re_.rekordbox_running(["rekordbox.exe"], tasklist_output="rekordbox.exe  1234 Console") is True
    assert re_.rekordbox_running(["rekordbox.exe"], tasklist_output="explorer.exe  99 Console") is False
