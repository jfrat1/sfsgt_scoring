from typing import NamedTuple

from .. import config, handicap


class _Matchup(NamedTuple):
    player_1: config.Player
    player_2: config.Player
    handicap_calc: handicap.HandicapCalculator

    HANDICAP_ALLOWANCE: float = 1.0

    def display(self) -> None:
        player_1_playing_handicap = self.handicap_calc.playing_handicap(
            player_handicap_index=self.player_9_hole_handicap_index(self.player_1),
            handicap_allowance=self.HANDICAP_ALLOWANCE,
        )
        player_2_playing_handicap = self.handicap_calc.playing_handicap(
            player_handicap_index=self.player_9_hole_handicap_index(self.player_2),
            handicap_allowance=self.HANDICAP_ALLOWANCE,
        )

        print(
            f"{self.player_1.name}: {player_1_playing_handicap} vs. {self.player_2.name}: {player_2_playing_handicap}"  # noqa: E501
        )

        if player_1_playing_handicap == player_2_playing_handicap:
            print("- Heads Up")
        else:
            stroke_differential = abs(player_1_playing_handicap - player_2_playing_handicap)

            is_player_1_lower_handicap = player_1_playing_handicap < player_2_playing_handicap

            lower_handicap_player = (
                self.player_1.name if is_player_1_lower_handicap else self.player_2.name
            )
            higher_handicap_player = (
                self.player_2.name if is_player_1_lower_handicap else self.player_1.name
            )

            print(
                f"- {higher_handicap_player} receives {stroke_differential} strokes from {lower_handicap_player}."  # noqa: E501
            )

    def player_9_hole_handicap_index(self, player: config.Player) -> float:
        return round(player.handicap_index / 2, 1)


class Individual9HoleMatches(NamedTuple):
    team_1: config.TeamIndividuals
    team_2: config.TeamIndividuals
    course_rating: float
    course_slope: int
    course_par: int

    def display_matchups(self) -> None:
        handicap_calc = handicap.HandicapCalculator(
            course_rating=self.course_rating,
            course_slope=self.course_slope,
            course_par=self.course_par,
        )

        print("Players and player handicaps:")
        print("- Match Strokes Received.")
        print("")

        matchups = self._matchups(handicap_calc)
        for matchup in matchups:
            matchup.display()
            print("")

    def _matchups(
        self,
        handicap_calc: handicap.HandicapCalculator,
    ) -> tuple[_Matchup, ...]:
        return tuple(
            _Matchup(player_1=player_1, player_2=player_2, handicap_calc=handicap_calc)
            for (player_1, player_2) in zip(self.team_1.players(), self.team_2.players())
        )
