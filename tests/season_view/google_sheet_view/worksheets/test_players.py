from season_view.google_sheet_view.worksheets.players import _canonicalize_player_name

STUB_EVENTS = ["Baylands", "Corica"]


def test_canonicalize_sortable_name() -> None:
    name = "Doe, John"

    assert _canonicalize_player_name(name) == "John Doe"


def canonicalize_already_canonical_name_does_nothing() -> None:
    name = "John Doe"
    assert _canonicalize_player_name(name) == name
