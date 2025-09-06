import logging

import courses
import season_config
import season_model
import season_view

from season_controller import delegate
from season_controller.read_data_normalizer import SeasonReadDataNormalizer

logger = logging.getLogger(__name__)


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
        self.course_provider = course_provider

    def run_season(self) -> None:
        logger.info("📚 Reading season data")
        view_read_data = self.view.read_season()
        read_data_normalized = SeasonReadDataNormalizer(read_data=view_read_data).normalize()

        model_input = delegate.SeasonViewToModelDelegate(
            view_read_data=read_data_normalized,
            course_provider=self.course_provider,
            config=self.config,
        ).generate_model_input()

        logger.info("🏌️‍♂️ Grinding")
        model_results = self.model.calculate_results(model_input)

        if view_read_data.are_finale_hcps_available and self.config.is_finale_enabled():
            # finale_course = self.course_provider.get_course("Callippe Preserve")
            # TODO: Several things
            #  - Players need to be passed in. Including gender.
            #  - A finale course needs to be configurable along with tees by gender.
            #  - Create a finale worksheet controller, finale write data, etc.
            #  - Consider making a delegate to convert data for the view
            # finale_data = season_finale.FinaleDataGenerator(
            #     season_handicaps_by_player=model_results.season_handicaps_by_player(),
            #     finale_ghin_handicaps_by_player=view_read_data.finale_handicaps_by_player(),
            #     course=finale_course,
            # ).generate()
            pass

        view_write_data = delegate.SeasonModelToViewDelegate(model_results).generate_view_write_data()

        logger.info("✍️ Writing results")
        self.view.write_season(view_write_data)
