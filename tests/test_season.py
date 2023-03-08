from ..src.season import Season
from ..src.event import Event

from . import test_data

def test_season_init():
    players = test_data.players.TestPlayers.to_list()
    
    season = Season(
        year=2022,
        events=[
            Event(
                course=test_data.courses.PRESIDIO,
                players=players,
                tee_name="Blue"
            ),
            Event(
                test_data.courses.SHARP_PARK,
                players=players,
                tee_name="White",
            )
        ]
    )

