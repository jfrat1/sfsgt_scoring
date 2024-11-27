from typing import NamedTuple

from .. import config, handicap


class _Matchup(NamedTuple):
    team_1_pair: config.PlayerPair
    team_2_pair: config.PlayerPair
    handicap_calc: handicap.HandicapCalculator

    LOWER_HANDICAP_ALLOWANCE: float = 0.35
    HIGHER_HANDICAP_ALLOWANCE: float = 0.15

    def display(self) -> None:
        team_1_playing_handicap = self.team_playing_handicap(self.team_1_pair)
        team_2_playing_handicap = self.team_playing_handicap(self.team_2_pair)

        team_1_players = self.team_player_names(self.team_1_pair)
        team_2_players = self.team_player_names(self.team_2_pair)

        print(
            f"{team_1_players}: {team_1_playing_handicap} vs. {team_2_players}: {team_2_playing_handicap}"  # noqa: E501
        )

        if team_1_playing_handicap == team_2_playing_handicap:
            print("- Heads Up")
        else:
            stroke_differential = abs(team_1_playing_handicap - team_2_playing_handicap)

            is_team_1_lower_handicap = team_1_playing_handicap < team_2_playing_handicap
            lower_handicap_team = team_1_players if is_team_1_lower_handicap else team_2_players
            higher_handicap_team = team_2_players if is_team_1_lower_handicap else team_1_players
            print(
                f"- {higher_handicap_team} receive {stroke_differential} strokes from {lower_handicap_team}"  # noqa: E501
            )

    def team_playing_handicap(self, team: config.PlayerPair) -> int:
        team_9_hole_handicap_indices = (
            self.player_9_hole_handicap_index(team.player_1),
            self.player_9_hole_handicap_index(team.player_2),
        )

        team_playing_handicap = self.handicap_calc.two_person_scramble_playing_handicap(
            player_handicap_indices=team_9_hole_handicap_indices,
            lower_handicap_allowance=self.LOWER_HANDICAP_ALLOWANCE,
            higher_handicap_allowance=self.HIGHER_HANDICAP_ALLOWANCE,
        )

        return team_playing_handicap

    def team_player_names(self, team: config.PlayerPair) -> str:
        return f"{team.player_1.name}/{team.player_2.name}"

    def player_9_hole_handicap_index(self, player: config.Player) -> float:
        return round(player.handicap_index / 2, 1)


class Scramble9HoleMatch(NamedTuple):
    team_1: config.TeamPairs
    team_2: config.TeamPairs
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
