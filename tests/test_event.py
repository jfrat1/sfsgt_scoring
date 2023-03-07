import pytest

from ..src.event import Event
from . import test_data

def presidio_event_blue_tees() -> Event:
    return Event(
        course=test_data.courses.PRESIDIO,
        players=[
            test_data.players.JOHN_FRATELLO,
            test_data.players.STANTON_TURNER,
            test_data.players.ERIK_PETRICH,
        ],
        tee_name="Blue"
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
            tee_name="UnavailableTee"
        )

def test_get_course_tee():
    event = presidio_event_blue_tees()
    tee = event._get_course_tee()
    assert tee == test_data.courses.PRESIDIO_BLUE_TEE


def test_set_course_tee():
    event = presidio_event_blue_tees()
    event.set_course_tee('Black')

def test_set_course_tee_unavailable():
    event = presidio_event_blue_tees()
    with pytest.raises(ValueError, match="UnavailableTee"):
        event.set_course_tee('UnavailableTee')

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
    
    event.set_course_tee('Black')
    assert event.course_handicaps() == {
        "John Fratello": 23,
        "Stanton Turner": 22,
        "Erik Petrich": 24,
    }
