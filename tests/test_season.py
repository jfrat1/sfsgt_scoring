from ..src.season import Season

from . import test_data

def test_season_init():
    season = Season(
        year=2022,
        events=[
            test_data.courses.PRESIDIO,
            
        ]
    )