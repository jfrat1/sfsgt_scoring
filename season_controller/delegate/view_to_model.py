from typing import NamedTuple

import course_database
import season_model
import season_view


class SeasonViewToModelDelegate(NamedTuple):
    view_read_data: season_view.SeasonViewReadData
    course_db: course_database.CourseDatabase

    def generate_model_input(self) -> season_model.SeasonModelInput:
        pass
