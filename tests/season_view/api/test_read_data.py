import math

import pytest
from season_common.player import Player, PlayerGender
from season_view.api.read_data import (
    SeasonViewEventHandicapIndices,
    SeasonViewReadDataInitError,
    SeasonViewReadDataResourceNotFoundError,
    SeasonViewReadPlayer,
)


class TestSeasonViewEventHandicapIndices:
    def test_get_player_not_found_raises_error(self) -> None:
        indices = SeasonViewEventHandicapIndices({"Snoopy": 12.0, "Charlie": 14.4})

        indices["Snoopy"]

        with pytest.raises(SeasonViewReadDataResourceNotFoundError):
            indices["foobar"]

    def test_init_raises_error_for_non_float_handicap_value(self) -> None:
        with pytest.raises(SeasonViewReadDataInitError):
            SeasonViewEventHandicapIndices({"Snoopy": ""})  # type: ignore

    def test_init_with_nan_values_does_not_raise(self) -> None:
        SeasonViewEventHandicapIndices({"Snoopy": math.nan, "Charlie": 14.4})


class TestSeasonViewReadPlayer:
    def build_test_read_player(self, handicaps: SeasonViewEventHandicapIndices) -> SeasonViewReadPlayer:
        return SeasonViewReadPlayer(
            player=Player(name="John Doe", gender=PlayerGender.MALE),
            event_handicap_indices=handicaps,
        )

    def test_is_handicap_available(self) -> None:
        player = self.build_test_read_player(
            handicaps=SeasonViewEventHandicapIndices({"Baylands": 15.2, "Corica": math.nan})
        )

        assert player.is_handicap_available(event_name="Baylands")
        assert not player.is_handicap_available(event_name="Corica")
