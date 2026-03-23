import math
from typing import NamedTuple

from courses import Course
from season_common import player
from season_config import EventTeeConfig
from season_view import SeasonViewReadPlayers


class FinaleDataError(Exception):
    pass


class FinalePlayerDescriptor(NamedTuple):
    name: str
    ghin_handicap_index: float
    season_handicap_index: float
    finale_handicap_index: float
    finale_course_handicap: int | None


class FinaleData:
    def __init__(self, players: list[FinalePlayerDescriptor]) -> None:
        self._players = players

    def get_player(self, player_name: str) -> FinalePlayerDescriptor:
        for player_ in self._players:
            if player_.name == player_name:
                return player_

        raise KeyError(f"Player {player_name} cannot be found in finale data.")

    def players(self) -> list[str]:
        return [player.name for player in self._players]


class FinaleDataGenerator:
    def __init__(
        self,
        players: SeasonViewReadPlayers,
        season_handicaps_by_player: dict[str, float],
        finale_ghin_handicaps_by_player: dict[str, float],
        course: Course,
        tees: EventTeeConfig,
    ) -> None:
        self._players = players
        self._season_handicaps_by_player = season_handicaps_by_player
        self._finale_ghin_handicaps_by_player = finale_ghin_handicaps_by_player

        self._verify_input_consistency()

        self._course = course
        self._tees = tees

    def generate(self) -> FinaleData:
        player_descriptors: list[FinalePlayerDescriptor] = []

        for player_ in self._players.player_names:
            player_descriptors.append(
                self._finale_player_descriptor(
                    name=player_,
                    ghin_handicap=self._finale_ghin_handicaps_by_player[player_],
                    season_handicap=self._season_handicaps_by_player[player_],
                )
            )

        return FinaleData(players=player_descriptors)

    def _verify_input_consistency(self) -> None:
        is_consistent = set(self._season_handicaps_by_player) == set(self._finale_ghin_handicaps_by_player)
        if not is_consistent:
            raise FinaleDataError(
                "Inputs to finale data generator are not consistent. Player names must match in both dictionaries."
            )

    def _finale_player_descriptor(
        self,
        name: str,
        ghin_handicap: float,
        season_handicap: float,
    ) -> FinalePlayerDescriptor:
        MIN_GHIN_RATIO = 0.90
        MAX_GHIN_RATIO = 1.10
        MAX_STROKE_OFFSET = 0.75
        MAX_FINALE_HANDICAP = 18.0

        min_finale_handicap = min(
            ghin_handicap * MIN_GHIN_RATIO,
            ghin_handicap - MAX_STROKE_OFFSET,
        )
        max_finale_handicap = max(
            ghin_handicap * MAX_GHIN_RATIO,
            ghin_handicap + MAX_STROKE_OFFSET,
        )

        # Target a 50/50 split of GHIN and season handicap
        target_finale_handicap = (ghin_handicap + season_handicap) / 2

        # Limit that to bounds around the GHIN handicap
        ghin_bounded_finale_handicap = min(max(target_finale_handicap, min_finale_handicap), max_finale_handicap)

        # Cap that to a max overall handicap
        capped_finale_handicap = min(ghin_bounded_finale_handicap, MAX_FINALE_HANDICAP)

        # Round to 1 decimal place
        finale_handicap = round(capped_finale_handicap, 1)

        # TODO: The tee needs to be gender-specific and we should do something better to handle the nullability.
        # Maybe it just shouldn't be nullable in the config.
        tee = self._tees.mens_tee or ""

        # Set the course handicap to None if the player's handicap index is NaN
        course_handicap = None
        if not math.isnan(finale_handicap):
            course_handicap = self._course.course_handicap(
                tee=tee, player_hcp_index=finale_handicap, player_gender=player.PlayerGender.MALE
            )

        return FinalePlayerDescriptor(
            name=name,
            ghin_handicap_index=ghin_handicap,
            season_handicap_index=season_handicap,
            finale_handicap_index=finale_handicap,
            finale_course_handicap=course_handicap,
        )
