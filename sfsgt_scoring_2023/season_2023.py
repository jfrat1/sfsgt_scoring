"""2023 SFSGT Seson module

This module implements processing for the 2023 SFSGT season. It imports
data from a specifically-formatted google sheet and writes results
to the same sheet.
"""

from typing import Dict

import pandas as pd

from sfsgt_scoring_2023 import (
    course,
    dataframe_utils,
    handicap,
    season,
    season_2023_points_config,
    season_sheet,
    sheets,
)


def verify_courses_played_2023(season_: season.Season) -> None:
    """Verify that players haven't played too many courses.

    This is special for 2023 because we allowed players to choose between playing
    Monarch Bay or Sharp Park for their final round of the season. This checks that
    players don't have score entered for both.
    """
    courses_to_pick_from = ["Monarch Bay", "Sharp Park"]
    for player_ in season_.players.player_names():
        if all(season_.season_points.loc[player_, courses_to_pick_from] > 0):
            raise ValueError(
                f"Player {player_} scored points for {' and '.join(courses_to_pick_from)}. "
                "Only 1 of these courses can be played in 2023."
            )


class Season2023:
    def __init__(self) -> None:
        sheet_controller = sheets.SheetController(sheet_name="SFSGT 2023 Scores")
        self.sheet = season_sheet.SeasonSheet(sheet_controller=sheet_controller)

        normal_event_points_by_rank = season_2023_points_config.NORMAL_EVENT_POINTS_BY_RANK
        major_event_points_by_rank = season_2023_points_config.MAJOR_EVENT_POINTS_BY_RANK

        event_configs = [
            season.SeasonEventConfig(
                course_name="Presidio",
                scorecard_sheet_name="Presidio Scorecard",
                results_sheet_name="Presidio Points",
                points_by_rank=normal_event_points_by_rank,
            ),
            season.SeasonEventConfig(
                course_name="Peacock Gap",
                scorecard_sheet_name="Peacock Gap Scorecard",
                results_sheet_name="Peacock Gap Points",
                points_by_rank=normal_event_points_by_rank,
            ),
            season.SeasonEventConfig(
                course_name="Harding",
                scorecard_sheet_name="Harding Scorecard",
                results_sheet_name="Harding Points",
                points_by_rank=major_event_points_by_rank,
            ),
            season.SeasonEventConfig(
                course_name="Poplar Creek",
                scorecard_sheet_name="Poplar Creek Scorecard",
                results_sheet_name="Poplar Creek Points",
                points_by_rank=normal_event_points_by_rank,
            ),
            season.SeasonEventConfig(
                course_name="Monarch Bay",
                scorecard_sheet_name="Monarch Bay Scorecard",
                results_sheet_name="Monarch Bay Points",
                points_by_rank=normal_event_points_by_rank,
            ),
            season.SeasonEventConfig(
                course_name="Sharp Park",
                scorecard_sheet_name="Sharp Park Scorecard",
                results_sheet_name="Sharp Park Points",
                points_by_rank=normal_event_points_by_rank,
            ),
        ]

        # TODO: Should initialize the season, but won't have any player info yet
        self.season = season.Season(season_sheet=self.sheet, event_configs=event_configs)

    def process_season(self) -> None:
        # Read inputs:
        # - courses sheet, set in season object
        # - player handicaps sheet, set in season object
        # - event scorecards, set in season object
        #
        # Process events
        #
        # Write outputs:
        # - event results
        # - leaderboard
        # - scoring differentials
        # - finale handicaps

        pass


def final_finale_adjusted_handicaps(
    current_ncga_handicaps: Dict[str, float],
    season_round_handicaps: Dict[str, float],
    overridden_handicaps: Dict[str, float],
) -> pd.DataFrame:
    final_adjusted_handicaps: Dict[str, Dict[str, float]] = {}
    for player_name, ncga_hc in current_ncga_handicaps.items():
        season_hc = season_round_handicaps[player_name]

        max_finale_handicap = max(ncga_hc * 1.2, ncga_hc + 2.0)
        min_finale_handicap = min(ncga_hc * 0.8, ncga_hc - 2.0)

        average_season_and_ncga_hc = (ncga_hc + season_hc) / 2.0

        overridden_handicap = overridden_handicaps.get(player_name, "No override")
        if isinstance(overridden_handicap, str):
            finale_handicap = max(
                min(average_season_and_ncga_hc, max_finale_handicap), min_finale_handicap
            )

        else:
            finale_handicap = overridden_handicap

        final_adjusted_handicaps[player_name] = {
            "ncga_hc": ncga_hc,
            "season_hc": season_hc,
            "min_finale_handicap": min_finale_handicap,
            "max_finale_handicap": max_finale_handicap,
            "average_season_and_ncga_hc": average_season_and_ncga_hc,
            "overridden_handicap": overridden_handicap,
            "finale_handicap": finale_handicap,
        }

    return pd.DataFrame(final_adjusted_handicaps).transpose()


def finale_handicaps_south_18(final_adjusted_handicaps: Dict[str, float]) -> pd.DataFrame:
    corica_south_18 = course.Course(
        course_name="Corica South 18",
        tee_name="Blue",
        par=72,
        rating=70.4,
        slope=123,
        distance=0,
    )

    course_handicaps: Dict[str, Dict[str, int]] = {}
    for name, handicap_index in final_adjusted_handicaps.items():
        course_handicaps[name] = {
            "index": handicap.calc_course_handicap(
                handicap_index=handicap_index,
                par=corica_south_18.par,
                rating=corica_south_18.rating,
                slope=corica_south_18.slope,
            ),
        }

    return pd.DataFrame(course_handicaps).transpose()


def finale_handicaps_north_9(final_adjusted_handicaps: Dict[str, float]) -> pd.DataFrame:
    corica_north_9 = course.Course(
        course_name="Corica North 9",
        tee_name="Black",
        par=36,
        rating=34.5,  # 9-hole rating
        slope=114,  # 9-hole slope
        distance=0,
    )

    course_handicaps: Dict[str, Dict[str, int]] = {}
    for name, handicap_index in final_adjusted_handicaps.items():
        course_handicaps[name] = {
            "index": handicap.calc_course_handicap_9_hole(
                handicap_index=handicap_index,
                par=corica_north_9.par,
                rating=corica_north_9.rating,
                slope=corica_north_9.slope,
            )
        }

    return pd.DataFrame(course_handicaps).transpose()


def main() -> None:
    season_2023 = Season2023()
    season_2023.process_season()

    sheet_controller = sheets.SheetController(sheet_name="SFSGT 2023 Scores")
    sheet = season_sheet.SeasonSheet(sheet_controller)

    normal_event_points_by_rank = season_2023_points_config.NORMAL_EVENT_POINTS_BY_RANK
    major_event_points_by_rank = season_2023_points_config.MAJOR_EVENT_POINTS_BY_RANK

    event_configs = [
        season.SeasonEventConfig(
            course_name="Presidio",
            scorecard_sheet_name="Presidio Scorecard",
            results_sheet_name="Presidio Points",
            points_by_rank=normal_event_points_by_rank,
        ),
        season.SeasonEventConfig(
            course_name="Peacock Gap",
            scorecard_sheet_name="Peacock Gap Scorecard",
            results_sheet_name="Peacock Gap Points",
            points_by_rank=normal_event_points_by_rank,
        ),
        season.SeasonEventConfig(
            course_name="Harding",
            scorecard_sheet_name="Harding Scorecard",
            results_sheet_name="Harding Points",
            points_by_rank=major_event_points_by_rank,
        ),
        season.SeasonEventConfig(
            course_name="Poplar Creek",
            scorecard_sheet_name="Poplar Creek Scorecard",
            results_sheet_name="Poplar Creek Points",
            points_by_rank=normal_event_points_by_rank,
        ),
        season.SeasonEventConfig(
            course_name="Monarch Bay",
            scorecard_sheet_name="Monarch Bay Scorecard",
            results_sheet_name="Monarch Bay Points",
            points_by_rank=normal_event_points_by_rank,
        ),
        season.SeasonEventConfig(
            course_name="Sharp Park",
            scorecard_sheet_name="Sharp Park Scorecard",
            results_sheet_name="Sharp Park Points",
            points_by_rank=normal_event_points_by_rank,
        ),
    ]

    season_ = season.Season(season_sheet=sheet, event_configs=event_configs)
    season_.process_all_events()

    verify_courses_played_2023(season_=season_)

    event_scoring_diffs = season_.event_scoring_differentials().round(decimals=1)
    event_scoring_diffs = dataframe_utils.fill_na_dtype_safe(
        df=event_scoring_diffs,
        fill_value="No Score",
    )
    event_scoring_diffs.reset_index(names=["Player"], inplace=True)
    season_.sheet.write_sheet(
        workshet_name="Event Scoring Diffs", worksheet_data_df=event_scoring_diffs
    )

    finale_handicaps = season_.season_finale_player_handicaps()
    season_.sheet.write_finale_handicaps(finale_handicaps)

    season_.write_course_handicaps()
    season_.write_leaderboard()

    end_of_season_ncga_handicaps = {
        "BRENNAN KURTELA": 1.5,
        "CHRIS LEE": 10.2,
        "CULLAN JACKSON": 6.6,
        "DAVE MOON": 16,
        "ERIK PETRICH": 17.7,
        "GAREK STUART": 12.2,
        "JARED GROPP": 23,
        "JEFF MCCARTHY": 22,
        "JOE WIGNALL": 8.7,
        "JOHN FRATELLO": 17.7,
        "JONNY MULLIGAN": 14,
        "KELLAN MCNULTY": 18,
        "MATT DRUM": 16.7,
        "MATT STARNS": 23,
        "BRETT DELORENZI": 17.5,
        "OTTO THORNTON-SILVER": 14,
        "SAM GILL": 19,
        "SEAN MARRIA-NELSON": 18,
        "STANTON TURNER": 13.5,
        "ADAM COHEN": 17,
    }

    season_round_handicaps = (
        finale_handicaps.set_index("Players").loc[:, "Finale Handicap"].to_dict()
    )

    overridden_finale_handicaps = {
        "JARED GROPP": 23.5,
        "KELLAN MCNULTY": 18,
        "MATT STARNS": 24,
        "OTTO THORNTON-SILVER": 13.5,
        "SAM GILL": 20.0,
    }

    final_adjusted_handicaps = final_finale_adjusted_handicaps(
        current_ncga_handicaps=end_of_season_ncga_handicaps,
        season_round_handicaps=season_round_handicaps,
        overridden_handicaps=overridden_finale_handicaps,
    )

    season_.sheet.write_sheet(
        workshet_name="Final Finale Handicaps",
        worksheet_data_df=final_adjusted_handicaps.reset_index(names=["player"]),
    )

    finale_handicap_index_by_player = final_adjusted_handicaps.loc[:, "finale_handicap"].to_dict()

    corica_south_18_course_handicaps = finale_handicaps_south_18(finale_handicap_index_by_player)
    corica_north_9_course_handicaps = finale_handicaps_north_9(finale_handicap_index_by_player)

    season_.sheet.write_sheet(
        workshet_name="Finale South 18 Course Handicaps",
        worksheet_data_df=corica_south_18_course_handicaps.reset_index(names=["player"]),
    )
    season_.sheet.write_sheet(
        workshet_name="Finale North 9 Course Handicaps",
        worksheet_data_df=corica_north_9_course_handicaps.reset_index(names=["player"]),
    )


if __name__ == "__main__":
    main()
