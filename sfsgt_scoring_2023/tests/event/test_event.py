import pandas as pd
import pytest

from sfsgt_scoring_2023 import event
from sfsgt_scoring_2023 import player
from sfsgt_scoring_2023 import course


PLAYER_GROUP_BOLT_GEOFF = player.PlayerGroup(
    player_list=[
        player.Player(
            name="Bolt",
            handicap=8,
        ),
        player.Player(
            name="Geoff",
            handicap=15.5,
        )
    ]
)

COURSE_PRESIDIO = course.Course(
    course_name="Presidio",
    tee_name="Blue",
    par=72,
    rating=69.5,
    slope=129,
    distance=5746,
)

# These constants are calculated for each player using the Presidio course data
COURSE_HANDICAP_BOLT_PRESIDIO = 7
COURSE_HANDICAP_GEOFF_PRESIDIO = 15

SCORING_CONFIG_2_PLAYERS_SUM_METHOD = event.EventScoringConfig(
    points_by_rank={1: 50.0, 2: 45.0},
    points_combo_method=event.EventPointsCombinationMethod.SUM,
)


def test_constructor() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=SCORING_CONFIG_2_PLAYERS_SUM_METHOD,
    )

    assert test_event.course is COURSE_PRESIDIO
    assert test_event.players is PLAYER_GROUP_BOLT_GEOFF
    assert test_event.scoring_config is SCORING_CONFIG_2_PLAYERS_SUM_METHOD
    assert test_event.player_scores == {}


def test_points_for_rank() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=SCORING_CONFIG_2_PLAYERS_SUM_METHOD,
    )

    assert test_event._points_for_rank(rank=1) == 50.0
    assert test_event._points_for_rank(rank=2) == 45.0


def test_points_ser_no_tie() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=SCORING_CONFIG_2_PLAYERS_SUM_METHOD,
    )

    points_ser = test_event._points_ser(
        ranks_ser=pd.Series(data=[1, 2], index=["Bolt", "Geoff"])
    )
    assert set(points_ser.index) == {"Bolt", "Geoff"}
    assert points_ser["Bolt"] == 50.0
    assert points_ser["Geoff"] == 45.0


def test_points_ser_with_tie() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=SCORING_CONFIG_2_PLAYERS_SUM_METHOD,
    )

    points_ser = test_event._points_ser(
        ranks_ser=pd.Series(data=[1, 1], index=["Bolt", "Geoff"])
    )
    assert set(points_ser.index) == {"Bolt", "Geoff"}
    assert points_ser["Bolt"] == 47.5
    assert points_ser["Geoff"] == 47.5


def test_points_ser_with_tie_complex() -> None:
    players = player.PlayerGroup(
        player_list=[
            player.Player(
                name="Kermit",
                handicap=8,
            ),
            player.Player(
                name="Miss Piggy",
                handicap=15.5,
            ),
            player.Player(
                name="Gonzo",
                handicap=12,
            ),
            player.Player(
                name="Oscar",
                handicap=13,
            ),
            player.Player(
                name="Animal",
                handicap=22,
            ),
        ]
    )

    scoring_config = event.EventScoringConfig(
        points_by_rank={1: 50.0, 2: 45.0, 3: 40.0, 4: 25.0, 5: 15.0},
        points_combo_method=event.EventPointsCombinationMethod.SUM,
    )

    test_event = event.Event(
        players=players,
        course=COURSE_PRESIDIO,
        scoring_config=scoring_config,
    )

    points_ser = test_event._points_ser(
        ranks_ser=pd.Series(
            data=[2, 1, 2, 2, 3],
            index=["Kermit", "Miss Piggy", "Gonzo", "Oscar", "Animal"],
        )
    )

    assert set(points_ser.index) == {"Kermit", "Miss Piggy", "Gonzo", "Oscar", "Animal"}

    second_place_tie_score = (45 + 40 + 25) / 3

    assert points_ser["Kermit"] == pytest.approx(second_place_tie_score, abs=0.0001)
    assert points_ser["Miss Piggy"] == 50.0
    assert points_ser["Gonzo"] == pytest.approx(second_place_tie_score, abs=0.0001)
    assert points_ser["Oscar"] == pytest.approx(second_place_tie_score, abs=0.0001)
    assert points_ser["Animal"] == 40.0


def test_points_ser_all_ranks_nan() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=SCORING_CONFIG_2_PLAYERS_SUM_METHOD,
    )

    # Using an empty dict as data makes all values NaN
    points_ser = test_event._points_ser(
        ranks_ser=pd.Series(data={}, index=["Bolt", "Geoff"])
    )

    assert set(points_ser.index) == {"Bolt", "Geoff"}
    assert points_ser["Bolt"] == 0.0
    assert points_ser["Geoff"] == 0.0


def test_points_ser_some_ranks_nan() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=SCORING_CONFIG_2_PLAYERS_SUM_METHOD,
    )

    # By omitting the 'Geoff' index in the data dictionary, it will get a NaN value
    points_ser = test_event._points_ser(
        ranks_ser=pd.Series(data={"Bolt": 1}, index=["Bolt", "Geoff"])
    )

    assert set(points_ser.index) == {"Bolt", "Geoff"}
    assert points_ser["Bolt"] == 50.0
    assert points_ser["Geoff"] == 0.0


def test_combined_points_ser_incorrect_columns() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=SCORING_CONFIG_2_PLAYERS_SUM_METHOD,
    )

    points_df = pd.DataFrame(
        data=[
            [50.0, 47.5],
            [45.0, 30.0]
        ],
        columns=["gross_points", "wrong_header"],
        index=["Bolt", "Geoff"],
    )

    with pytest.raises(
        event.EventCombinedPointsException,
        match="Expected points_df to have column labels 'gross_points' and 'net_points'"
    ):
        test_event._combined_points_ser(points_df=points_df)


def test_combined_points_sum_method() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=SCORING_CONFIG_2_PLAYERS_SUM_METHOD,
    )

    points_df = pd.DataFrame(
        data=[
            [50.0, 47.5],
            [45.0, 30.0]
        ],
        columns=["gross_points", "net_points"],
        index=["Bolt", "Geoff"],
    )

    combined_points_ser = test_event._combined_points_ser(points_df=points_df)

    assert set(combined_points_ser.index) == {"Bolt", "Geoff"}
    assert combined_points_ser["Bolt"] == 97.5
    assert combined_points_ser["Geoff"] == 75.0


def test_combined_points_average_method() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=event.EventScoringConfig(
            points_by_rank={1: 50.0, 2: 45.0},
            points_combo_method=event.EventPointsCombinationMethod.AVERAGE,
        ),
    )

    points_df = pd.DataFrame(
        data=[
            [50.0, 47.5],
            [45.0, 30.0]
        ],
        columns=["gross_points", "net_points"],
        index=["Bolt", "Geoff"],
    )

    combined_points_ser = test_event._combined_points_ser(points_df=points_df)

    assert set(combined_points_ser.index) == {"Bolt", "Geoff"}
    assert combined_points_ser["Bolt"] == pytest.approx((50.0 + 47.5) / 2, abs=0.0001)
    assert combined_points_ser["Geoff"] == pytest.approx((45.0 + 30.0) / 2, abs=0.0001)


def test_combined_points_blend_method() -> None:
    test_event = event.Event(
        players=PLAYER_GROUP_BOLT_GEOFF,
        course=COURSE_PRESIDIO,
        scoring_config=event.EventScoringConfig(
            points_by_rank={1: 50.0, 2: 45.0},
            points_combo_method=event.EventPointsCombinationMethod.BLEND_60_PCT_NET,
        ),
    )

    points_df = pd.DataFrame(
        data=[
            [50.0, 47.5],
            [45.0, 30.0]
        ],
        columns=["gross_points", "net_points"],
        index=["Bolt", "Geoff"],
    )

    combined_points_ser = test_event._combined_points_ser(points_df=points_df)

    assert set(combined_points_ser.index) == {"Bolt", "Geoff"}
    assert combined_points_ser["Bolt"] == pytest.approx((0.4 * 50) + (0.6 * 47.5), abs=0.0001)
    assert combined_points_ser["Geoff"] == pytest.approx((0.4 * 45) + (0.6 * 30), abs=0.0001)

