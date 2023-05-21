import dataclasses
import json
from typing import List

from sfsgt_scoring import handicap

indexes = {
    "steve": 10.0,
    "erik": 18,
    "tim": 22,
    "stanton": 14,
    "gropp": 22,
    "moon": 16,
    "mulligan": 16,
    "jfrat": 18,
}

# # wolf run blues
# wolf_run_rating = 70.8
# wolf_run_slope = 128

# Coyote moon whites
coyote_moon_rating = 69.20
coyote_moon_slope = 130

# Coyote moon front 9
coyote_moon_front_rating = 34.8
coyote_moon_front_slope = 124

# coyote moon back 9
coyote_moon_back_rating = 34.4
coyote_moon_back_slope = 136


coyote_moon_course_handicaps_18 = {
    player: handicap.calc_course_handicap(
        handicap_index=index,
        par=72,
        rating=coyote_moon_rating,
        slope=coyote_moon_slope,
    )
    for player, index in indexes.items()
}

coyote_moon_course_handicaps_front_9 = {
    player: handicap.calc_course_handicap_9_hole(
        handicap_index=index,
        par=36,
        rating=coyote_moon_front_rating,
        slope=coyote_moon_front_slope,
    )
    for player, index in indexes.items()
}

coyote_moon_course_handicaps_back_9 = {
    player: handicap.calc_course_handicap_9_hole(
        handicap_index=index,
        par=36,
        rating=coyote_moon_back_rating,
        slope=coyote_moon_back_slope,
    )
    for player, index in indexes.items()
}



print("Individual course handicaps, coyote 18")
print(json.dumps(coyote_moon_course_handicaps_18, indent=2))
print("Individual course handicaps, coyote front 9")
print(json.dumps(coyote_moon_course_handicaps_front_9, indent=2))
print("Individual course handicaps, coyote back 9")
print(json.dumps(coyote_moon_course_handicaps_back_9, indent=2))



# Scramble
# 35% low/15% high
# Erik + Mully vs. Steve + Gropp
# Tim + Stanton vs. Moon + Jfrat

@dataclasses.dataclass()
class Team:
    players: List[str]

@dataclasses.dataclass()
class Match:
    team_erik: Team
    team_steve: Team

    def team_match_handicap(self, team_players) -> float:
        course_handicaps_9_hole = {
            player: coyote_moon_course_handicaps_front_9[player]
            for player in team_players
        }

        lower_handicap = min(course_handicaps_9_hole.values())
        higher_handicap = max(course_handicaps_9_hole.values())
        return round(0.35 * lower_handicap + 0.15 * higher_handicap)

    def print_team_match_strokes_given(self):
        team_erik_match_handicap = self.team_match_handicap(self.team_erik.players)
        team_steve_match_handicap = self.team_match_handicap(self.team_steve.players)

        print("")
        print(f"Match: {self.team_erik.players} vs. {self.team_steve.players}")
        if team_erik_match_handicap > team_steve_match_handicap:
            strokes_given = team_erik_match_handicap - team_steve_match_handicap
            print(f"{self.team_steve.players} give {self.team_erik.players} {strokes_given} strokes")
        elif team_steve_match_handicap > team_erik_match_handicap:
            strokes_given = team_steve_match_handicap - team_erik_match_handicap
            print(f"{self.team_erik.players} give {self.team_steve.players} {strokes_given} strokes")
        else:
            print("Heads up")

        print("")

    def print_individual_matches_strokes_given(self):
        print("")

        def print_individual_match_strokes_given(player_team_erik: str, player_team_steve: str):
            print(f"Match {player_team_erik} vs. {player_team_steve}")
            handicap_player_team_erik = coyote_moon_course_handicaps_back_9[player_team_erik]
            handicap_player_team_steve = coyote_moon_course_handicaps_back_9[player_team_steve]

            if handicap_player_team_erik > handicap_player_team_steve:
                strokes_given = handicap_player_team_erik - handicap_player_team_steve
                print(f"{player_team_steve} gives {player_team_erik} {strokes_given}")
            elif handicap_player_team_steve > handicap_player_team_erik:
                strokes_given = handicap_player_team_steve - handicap_player_team_erik
                print(f"{player_team_erik} gives {player_team_steve} {strokes_given}")
            else:
                print("Heads up")

            print("")

        print_individual_match_strokes_given(self.team_erik.players[0], self.team_steve.players[0])
        print_individual_match_strokes_given(self.team_erik.players[1], self.team_steve.players[1])


match_1 = Match(
    team_erik=Team(players=["erik", "mulligan"]),
    team_steve=Team(players=["steve", "gropp"])
)

match_2 = Match(
    team_erik=Team(players=["tim", "stanton"]),
    team_steve=Team(players=["moon", "jfrat"])
)

match_1.print_team_match_strokes_given()
match_2.print_team_match_strokes_given()
match_1.print_individual_matches_strokes_given()
match_2.print_individual_matches_strokes_given()
