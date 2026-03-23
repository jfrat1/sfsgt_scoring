import logging

import courses
import season_config
import season_finale
import season_model
import season_view
from courses.provider import CourseProviderError

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

        finale_data = None
        if self.config.is_finale_enabled():
            if view_read_data.are_finale_hcps_available:
                finale_course = self.get_finale_course()
                if finale_course is not None:
                    finale_data = season_finale.FinaleDataGenerator(
                        players=view_read_data.players,
                        season_handicaps_by_player=model_results.season_handicaps_by_player(),
                        finale_ghin_handicaps_by_player=view_read_data.finale_handicaps_by_player(),
                        course=finale_course,
                        tees=self.config.finale_tees,
                    ).generate()

            else:
                logger.warning(
                    "Calculations for the finale are configured to run, but finale handicaps are not available in the "
                    "sheet. Calculations and sheet updates will be skipped."
                )

        view_write_data = delegate.SeasonModelToViewDelegate(model_results, finale_data).generate_view_write_data()

        logger.info("👩🏾‍💻 Writing results")
        self.view.write_season(view_write_data)

    def get_finale_course(self) -> courses.Course | None:
        finale_course_name = self.config.finale_course

        try:
            return self.course_provider.get_course(finale_course_name)
        except CourseProviderError:
            # Report the error to the user and then swallow it
            logger.error(
                f"The configured finale course named {finale_course_name} could not be found by the course "
                "provider. Finale calculations will be skipped."
            )
            return

    # def finale_data(self, view_read_data: )
