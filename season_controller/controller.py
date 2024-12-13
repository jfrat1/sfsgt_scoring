import course_database
import season_config
import season_model
import season_view
from season_controller.delegate import (
    SeasonModelToViewDelegate,
    SeasonViewToModelDelegate,
)


class SeasonController:
    def __init__(
        self,
        model: season_model.SeasonModel,
        view: season_view.SeasonView,
        config: season_config.SeasonConfig,
        course_db: course_database.CourseDatabase,
    ) -> None:
        self.model = model
        self.view = view
        self.config = config
        self.course_db = course_db

    def run_season(self) -> None:
        view_read_data = self.view.read()

        model_input = SeasonViewToModelDelegate(
            view_read_data=view_read_data,
            course_db=self.course_db,
            config=self.config,
        ).generate_model_input()

        model_results = self.model.calculate_results(model_input)

        view_write_data = SeasonModelToViewDelegate(model_results).generate_view_write_data()

        self.view.write(view_write_data)
