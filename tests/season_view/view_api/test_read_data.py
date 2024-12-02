import pytest

from season_view.view_api import read_data


def test_season_view_event_handicap_indices_get_player_not_found_raises_error() -> None:
    indices = read_data.SeasonViewEventHandicapIndices(
        {"Snoopy": 12.0, "Charlie": 14.4}
    )

    indices["Snoopy"]

    with pytest.raises(read_data.SeasonViewReadDataResourceNotFoundError):
        indices["foobar"]
