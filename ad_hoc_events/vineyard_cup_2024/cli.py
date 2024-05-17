import click

from ad_hoc_events.vineyard_cup_2024.config import (
    TeamPairs,
    TeamIndividuals,
    PlayerPair,
    STANTON_TURNER,
    JOHN_FRATELLO,
    CULLAN_JACKSON,
    DAVID_ALVAREZ,
    STEVE_HARASYM,
    DREW_BARRETT,
    ERIK_PETRICH,
    OTTO_THORNTON_SILVER,
    JOE_WIGNALL,
    SCOTT_YOUNG,
    ZACH_AVILA,
    THOMAS_KAUTH,
    TKS_BOY,
    WILL_DANIELS,
    WILLS_BOY,
    TKS_OTHER_BOY,
    DREW_COLLINSHAW,
)
from ad_hoc_events.vineyard_cup_2024.event import (
    best_ball_18_hole_matches,
    scramble_9_hole_matches,
    individual_9_hole_matches,
)

CHARDONNAY_HOLE_HANDICAP_RANKS = {
    1: 11,
    2: 5,
    3: 17,
    4: 7,
    5: 13,
    6: 3,
    7: 1,
    8: 15,
    9: 9,
    10: 10,
    11: 6,
    12: 8,
    13: 16,
    14: 14,
    15: 4,
    16: 18,
    17: 2,
    18: 12,
}

EAGLE_VINES_HOLE_HANDICAP_RANKS = {
    1: 10,
    2: 8,
    3: 18,
    4: 2,
    5: 12,
    6: 4,
    7: 16,
    8: 6,
    9: 14,
    10: 1,
    11: 13,
    12: 9,
    13: 5,
    14: 17,
    15: 15,
    16: 11,
    17: 3,
    18: 7,
}

TEAM_TURNER_CHARDONNAY_4_BALL = TeamPairs(
    pair_1=PlayerPair(player_1=STANTON_TURNER, player_2=OTTO_THORNTON_SILVER),
    pair_2=PlayerPair(player_1=THOMAS_KAUTH, player_2=TKS_OTHER_BOY),
    pair_3=PlayerPair(player_1=WILL_DANIELS, player_2=WILLS_BOY),
    pair_4=PlayerPair(player_1=DAVID_ALVAREZ, player_2=ZACH_AVILA),
)
TEAM_FRATELLO_CHARDONNAY_4_BALL = TeamPairs(
    pair_1=PlayerPair(player_1=JOHN_FRATELLO, player_2=JOE_WIGNALL),
    pair_2=PlayerPair(player_1=TKS_BOY, player_2=SCOTT_YOUNG),
    pair_3=PlayerPair(player_1=ERIK_PETRICH, player_2=STEVE_HARASYM),
    pair_4=PlayerPair(player_1=CULLAN_JACKSON, player_2=DREW_BARRETT),
)

TEAM_TURNER_EAGLE_VINES_FRONT_9_SCRAMBLE = TeamPairs(
    pair_1=PlayerPair(player_1=THOMAS_KAUTH, player_2=THOMAS_KAUTH),
    pair_2=PlayerPair(player_1=WILL_DANIELS, player_2=STANTON_TURNER),
    pair_3=PlayerPair(player_1=TKS_OTHER_BOY, player_2=TKS_OTHER_BOY),
    pair_4=PlayerPair(player_1=WILLS_BOY, player_2=WILLS_BOY),
)
TEAM_FRATELLO_EAGLE_VINES_FRONT_9_SCRAMBLE = TeamPairs(
    pair_1=PlayerPair(player_1=JOE_WIGNALL, player_2=SCOTT_YOUNG),
    pair_2=PlayerPair(player_1=CULLAN_JACKSON, player_2=ERIK_PETRICH),
    pair_3=PlayerPair(player_1=TKS_BOY, player_2=DREW_BARRETT),
    pair_4=PlayerPair(player_1=STEVE_HARASYM, player_2=JOHN_FRATELLO),
)

TEAM_TURNER_EAGLE_VINES_BACK_9_INDIVIDUAL_MATCHES = TeamIndividuals(
    player_1=THOMAS_KAUTH,
    player_2=THOMAS_KAUTH,
    player_3=WILL_DANIELS,
    player_4=STANTON_TURNER,
    player_5=TKS_OTHER_BOY,
    player_6=TKS_OTHER_BOY,
    player_7=WILLS_BOY,
    player_8=WILLS_BOY,
)
TEAM_FRATELLO_EAGLE_VINES_BACK_9_INDIVIDUAL_MATCHES = TeamIndividuals(
    player_1=JOE_WIGNALL,
    player_2=SCOTT_YOUNG,
    player_3=CULLAN_JACKSON,
    player_4=ERIK_PETRICH,
    player_5=TKS_BOY,
    player_6=DREW_BARRETT,
    player_7=STEVE_HARASYM,
    player_8=JOHN_FRATELLO,
)


@click.command()
def cli() -> None:
    print("EVENT 1: Chardonnay 18 Hole 4-Ball\n")
    event_1 = best_ball_18_hole_matches.BestBall18HoleMatches(
        team_1=TEAM_TURNER_CHARDONNAY_4_BALL,
        team_2=TEAM_FRATELLO_CHARDONNAY_4_BALL,
        course_name="chardonnay",
        tee_name="purple",
    )
    event_1.display_matchups()

    print("\n\nEVENT2: Eagle Vines Front 9 Scramble\n")

    EAGLE_VINES_FRONT_9_RATING = 35.8
    EAGLE_VINES_FRONT_9_SLOPE = 130
    EAGLE_VINES_FRONT_9_PAR = 37

    event_2 = scramble_9_hole_matches.Scramble9HoleMatch(
        team_1=TEAM_TURNER_EAGLE_VINES_FRONT_9_SCRAMBLE,
        team_2=TEAM_FRATELLO_EAGLE_VINES_FRONT_9_SCRAMBLE,
        course_rating=EAGLE_VINES_FRONT_9_RATING,
        course_slope=EAGLE_VINES_FRONT_9_SLOPE,
        course_par=EAGLE_VINES_FRONT_9_PAR,
    )
    event_2.display_matchups()

    print("\n\nEVENT 3: Eagle Vines Back 9 Individual Matches\n")

    EAGLE_VINES_BACK_9_RATING = 35.4
    EAGLE_VINES_BACK_9_SLOPE = 124
    EAGLE_VINES_BACK_9_PAR = 35

    event_3 = individual_9_hole_matches.Individual9HoleMatches(
        team_1=TEAM_TURNER_EAGLE_VINES_BACK_9_INDIVIDUAL_MATCHES,
        team_2=TEAM_FRATELLO_EAGLE_VINES_BACK_9_INDIVIDUAL_MATCHES,
        course_rating=EAGLE_VINES_BACK_9_RATING,
        course_slope=EAGLE_VINES_BACK_9_SLOPE,
        course_par=EAGLE_VINES_BACK_9_PAR,
    )
    event_3.display_matchups()


if __name__ == "__main__":
    cli()