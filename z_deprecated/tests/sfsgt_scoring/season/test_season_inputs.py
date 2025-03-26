import pytest
from sfsgt_scoring.season import event, season

POPPY_RIDGE_EVENT_INPUT = event.EventInput(
    course=event.CourseInput(
        name="Poppy Ridge",
        tee=event.CourseTeeData(
            name="White",
            rating=70.2,
            slope=128,
        ),
        hole_pars=event.CourseHolePars(
            {
                1: 4,
                2: 4,
                3: 3,
                4: 4,
                5: 5,
                6: 4,
                7: 3,
                8: 4,
                9: 5,
                10: 4,
                11: 3,
                12: 4,
                13: 4,
                14: 5,
                15: 4,
                16: 3,
                17: 5,
                18: 4,
            }
        ),
    ),
    type=event.EventType.STANDARD,
    players={
        "Stanton Turner": event.EventPlayerInput(
            handicap_index=14,
            scorecard=event.Scorecard(
                strokes_per_hole={
                    1: 5,
                    2: 4,
                    3: 5,
                    4: 6,
                    5: 5,
                    6: 6,
                    7: 4,
                    8: 4,
                    9: 5,
                    10: 6,
                    11: 6,
                    12: 5,
                    13: 4,
                    14: 4,
                    15: 4,
                    16: 4,
                    17: 4,
                    18: 5,
                }  # noqa: E501
            ),
        ),
        "John Fratello": event.EventPlayerInput(
            handicap_index=15.8,
            scorecard=event.Scorecard(
                strokes_per_hole={
                    1: 5,
                    2: 7,
                    3: 6,
                    4: 3,
                    5: 5,
                    6: 6,
                    7: 3,
                    8: 5,
                    9: 6,
                    10: 7,
                    11: 6,
                    12: 4,
                    13: 3,
                    14: 5,
                    15: 3,
                    16: 4,
                    17: 5,
                    18: 6,
                }  # noqa: E501
            ),
        ),
    },
)

HARDING_PARK_EVENT_INPUT = event.EventInput(
    course=event.CourseInput(
        name="Harding Park",
        tee=event.CourseTeeData(
            name="Blue",
            rating=73.5,
            slope=131,
        ),
        hole_pars=event.CourseHolePars(
            {
                1: 4,
                2: 4,
                3: 3,
                4: 5,
                5: 4,
                6: 4,
                7: 4,
                8: 3,
                9: 5,
                10: 5,
                11: 3,
                12: 5,
                13: 4,
                14: 4,
                15: 4,
                16: 4,
                17: 3,
                18: 4,
            }
        ),
    ),
    type=event.EventType.MAJOR,
    players={
        "Stanton Turner": event.EventPlayerInput(
            handicap_index=14.2,
            scorecard=event.Scorecard(
                strokes_per_hole={
                    1: 5,
                    2: 4,
                    3: 5,
                    4: 6,
                    5: 5,
                    6: 6,
                    7: 4,
                    8: 4,
                    9: 5,
                    10: 6,
                    11: 6,
                    12: 5,
                    13: 4,
                    14: 4,
                    15: 4,
                    16: 4,
                    17: 4,
                    18: 5,
                },  # noqa: E501
            ),
        ),
        "John Fratello": event.EventPlayerInput(
            handicap_index=15.4,
            scorecard=event.Scorecard(
                strokes_per_hole={
                    1: 5,
                    2: 7,
                    3: 6,
                    4: 3,
                    5: 5,
                    6: 6,
                    7: 3,
                    8: 5,
                    9: 6,
                    10: 7,
                    11: 6,
                    12: 4,
                    13: 3,
                    14: 5,
                    15: 3,
                    16: 4,
                    17: 5,
                    18: 6,
                },  # noqa: E501
            ),
        ),
    },
)


def test_season_inputs_construct() -> None:
    events_input: season.EventsInput = {
        "Poppy Ridge": POPPY_RIDGE_EVENT_INPUT,
        "Harding Park": HARDING_PARK_EVENT_INPUT,
    }

    season_input = season.SeasonInput(
        events=events_input,
        player_names=["Stanton Turner", "John Fratello"],
    )

    assert season_input.events["Harding Park"].course.name == "Harding Park"
    assert season_input.events["Poppy Ridge"].course.tee.name == "White"

    assert season_input.events["Harding Park"].players["Stanton Turner"].handicap_index == 14.2
    assert season_input.events["Harding Park"].players["Stanton Turner"].scorecard.strokes_per_hole()[1] == 5
    assert season_input.events["Poppy Ridge"].players["John Fratello"].handicap_index == 15.8
    assert season_input.events["Poppy Ridge"].players["John Fratello"].scorecard.strokes_per_hole()[6] == 6

    assert season_input.player_names == ["Stanton Turner", "John Fratello"]


def test_season_inputs_event_missing_player_raises_error() -> None:
    harding_park_event_input_players = HARDING_PARK_EVENT_INPUT.players.copy()
    harding_park_event_input_players.pop("John Fratello", None)

    harding_park_event_input_local = event.EventInput(
        course=HARDING_PARK_EVENT_INPUT.course,
        type=HARDING_PARK_EVENT_INPUT.type,
        players=harding_park_event_input_players,
    )

    events_input: season.EventsInput = {
        "Poppy Ridge": POPPY_RIDGE_EVENT_INPUT,
        "Harding Park": harding_park_event_input_local,
    }

    with pytest.raises(season.SeasonInputConsistencyError):
        season.SeasonInput(
            events=events_input,
            player_names=["Stanton Turner", "John Fratello"],
        )
