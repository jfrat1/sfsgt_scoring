import pytest

from ..src.event import Event
from . import test_data


def presidio_event_blue_tees() -> Event:
    return Event(
        course=test_data.courses.PRESIDIO,
        players=test_data.players.TestPlayers.to_list(),
        tee_name="Blue",
    )


def test_init():
    event = presidio_event_blue_tees()


def test_init_wrong_course_tee():
    with pytest.raises(ValueError, match="UnavailableTee"):
        event = Event(
            course=test_data.courses.PRESIDIO,
            players=[
                test_data.players.JOHN_FRATELLO,
                test_data.players.STANTON_TURNER,
            ],
            tee_name="UnavailableTee",
        )


def test_get_course_tee():
    event = presidio_event_blue_tees()
    tee = event._course_tee()
    assert tee == test_data.courses.PRESIDIO_BLUE_TEE


def test_set_tee_name():
    event = presidio_event_blue_tees()
    event.set_tee_name("Black")


def test_set_tee_name_unavailable():
    event = presidio_event_blue_tees()
    with pytest.raises(ValueError, match="UnavailableTee"):
        event.set_tee_name("UnavailableTee")


def test_player_course_handicaps():
    event = presidio_event_blue_tees()
    assert event.course_handicaps() == {
        "John Fratello": 19,
        "Stanton Turner": 18,
        "Erik Petrich": 20,
    }


def test_player_course_handicaps_switch_tee():
    event = presidio_event_blue_tees()
    assert event.course_handicaps() == {
        "John Fratello": 19,
        "Stanton Turner": 18,
        "Erik Petrich": 20,
    }

    event.set_tee_name("Black")
    assert event.course_handicaps() == {
        "John Fratello": 23,
        "Stanton Turner": 22,
        "Erik Petrich": 24,
    }


def test_get_player_names():
    event = presidio_event_blue_tees()
    assert event.player_names() == ["John Fratello", "Stanton Turner", "Erik Petrich"]


def test_get_num_holes():
    event = presidio_event_blue_tees()
    assert event.num_holes() == 18


def test_set_player_score():
    event = presidio_event_blue_tees()

    # fmt: off
    SCORES = [
        5, 4, 4, 4, 5, 6, 5, 5, 6,
        7, 6, 5, 4, 7, 6, 5, 4, 6,
    ]
    # fmt: on

    event.set_player_scores(
        player_name=test_data.players.JOHN_FRATELLO.name, scores=SCORES
    )

    assert event.raw_scores[test_data.players.JOHN_FRATELLO.name] == SCORES


def test_set_player_score_unknown_player_name():
    event = presidio_event_blue_tees()

    with pytest.raises(ValueError, match="Player name 'Not A Name' not found"):
        event.set_player_scores(player_name="Not A Name", scores=[1, 2])


def test_set_player_score_wrong_num_holes():
    event = presidio_event_blue_tees()

    with pytest.raises(ValueError, match="Incorrect number of scores for player"):
        event.set_player_scores(
            player_name=test_data.players.JOHN_FRATELLO.name, scores=[5, 4, 4, 3]
        )


def test_set_player_score_bad_types():
    event = presidio_event_blue_tees()

    with pytest.raises(TypeError, match="Incorrect type for argument 'scores'"):
        event.set_player_scores(
            player_name=test_data.players.JOHN_FRATELLO.name, scores=0
        )

    with pytest.raises(TypeError, match="Incorrect type for argument 'scores'"):
        event.set_player_scores(
            player_name=test_data.players.JOHN_FRATELLO.name, scores=["foo", "bar"]
        )
