from typing import NamedTuple

import courses
from season_common.player import PlayerGender

from .. import config, handicap


class _Matchup(NamedTuple):
    team_1_pair: config.PlayerPair
    team_2_pair: config.PlayerPair
    handicap_calc: handicap.HandicapCalculator

    HANDICAP_ALLOWANCE: float = 0.9

    def display(self) -> None:
        team_1_playing_handicaps = self.team_playing_handicaps(self.team_1_pair)
        team_2_playing_handicaps = self.team_playing_handicaps(self.team_2_pair)

        lowest_handicap = self.lowest_playing_handicap(team_1_playing_handicaps, team_2_playing_handicaps)
        team_1_handicaps_normalized = self.normalize_team_playing_handicaps(
            team_playing_handicaps=team_1_playing_handicaps,
            lowest_playing_handicap=lowest_handicap,
        )
        team_2_handicaps_normalized = self.normalize_team_playing_handicaps(
            team_playing_handicaps=team_2_playing_handicaps,
            lowest_playing_handicap=lowest_handicap,
        )

        print(f"{team_1_playing_handicaps} vs. {team_2_playing_handicaps}")
        print(f"- {team_1_handicaps_normalized} vs. {team_2_handicaps_normalized}")

    def team_playing_handicaps(self, team: config.PlayerPair) -> dict[str, int]:
        playing_handicaps: dict[str, int] = {}
        for player in team.players():
            playing_handicaps[player.name] = self.handicap_calc.playing_handicap(
                player_handicap_index=player.handicap_index,
                handicap_allowance=self.HANDICAP_ALLOWANCE,
            )

        return playing_handicaps

    def lowest_playing_handicap(
        self,
        team_1_playing_handicaps: dict[str, int],
        team_2_playing_handicaps: dict[str, int],
    ) -> int:
        return min(list(team_1_playing_handicaps.values()) + list(team_2_playing_handicaps.values()))

    def normalize_team_playing_handicaps(
        self,
        team_playing_handicaps: dict[str, int],
        lowest_playing_handicap: int,
    ) -> dict[str, int]:
        return {
            name: playing_handicap - lowest_playing_handicap
            for name, playing_handicap in team_playing_handicaps.items()
        }


class BestBall18HoleMatches(NamedTuple):
    team_1: config.TeamPairs
    team_2: config.TeamPairs
    course_name: str
    tee_name: str

    def display_matchups(self) -> None:
        course_provider = courses.build_default_concrete_course_provider()
        course = course_provider.get_course(course_name=self.course_name)
        course_tee = course.get_tee_info(tee_name=self.tee_name, player_gender=PlayerGender.MALE)

        handicap_calc = handicap.HandicapCalculator(
            course_rating=course_tee.rating,
            course_slope=course_tee.slope,
            course_par=course.par,
        )

        print("Players and player handicaps:")
        print("- Match strokes received.")
        print("")

        matchups = self._matchups(handicap_calc)
        for matchup in matchups:
            matchup.display()
            print("")

    def _matchups(
        self,
        handicap_calc: handicap.HandicapCalculator,
    ) -> tuple[_Matchup, _Matchup, _Matchup, _Matchup]:
        return (
            _Matchup(
                team_1_pair=self.team_1.pair_1,
                team_2_pair=self.team_2.pair_1,
                handicap_calc=handicap_calc,
            ),
            _Matchup(
                team_1_pair=self.team_1.pair_2,
                team_2_pair=self.team_2.pair_2,
                handicap_calc=handicap_calc,
            ),
            _Matchup(
                team_1_pair=self.team_1.pair_3,
                team_2_pair=self.team_2.pair_3,
                handicap_calc=handicap_calc,
            ),
            _Matchup(
                team_1_pair=self.team_1.pair_4,
                team_2_pair=self.team_2.pair_4,
                handicap_calc=handicap_calc,
            ),
        )
