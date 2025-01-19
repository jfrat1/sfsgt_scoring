import courses
import season_config
import season_model
import season_view
from season_controller import delegate


class SeasonController:
    def __init__(
        self,
        model: season_model.SeasonModel,
        view: season_view.SeasonView,
        config: season_config.SeasonConfig,
        course_provider: courses.CourseProvider,
    ) -> None:
        self.model = model
        self.view = view
        self.config = config
        self.course_db = course_provider

    def run_season(self) -> None:
        view_read_data = self.view.read_season()

        model_input = delegate.SeasonViewToModelDelegate(
            view_read_data=view_read_data,
            course_provider=self.course_db,
            config=self.config,
        ).generate_model_input()

        pass

        # model_results = self.model.calculate_results(model_input)

        # if self.config.is_finale_enabled():
        #     finale_data = season_finale.ConcreteFinaleDataGenerator(
        #         season_results=model_results
        #     ).generate()
        #     # TODO: DO something with the finale data. Maybe modify the write data
        #     # to add it. Maybe have a separate method in the SeasonView to write
        #     # the finale sheet.

        # view_write_data = SeasonModelToViewDelegate(model_results).generate_view_write_data()

        # self.view.write_season(view_write_data)
