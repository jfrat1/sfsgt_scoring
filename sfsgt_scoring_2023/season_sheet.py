import numbers
import pandas as pd
from typing import Any, Dict, List

from sfsgt_scoring_2023 import (
    course,
    dataframe_utils,
    # TODO: see if we can eliminate the dependency on event, player, and season here
    # This class shouldn't need to know about all of those
    # It can take dataframes to write to sheets and it can return either a dataframe
    # or a class of this module when reading a sheet
    event,
    player,
    season,
    sheets,
)

class SeasonSheetException(Exception):
    """Exception related to interactions with a season sheet."""


class SeasonSheet:
    """SFSGT Season worksheet controller. Implements interactions with the season worksheet."""

    def __init__(self, sheet_controller: sheets.SheetController) -> None:
        self.sheet_controller = sheet_controller

    def read_players_sheet(self) -> player.PlayerGroup:
        """Read the 'Players' worksheet in the 2023 SFSGT sheet.

        The 'Players' tab should have 2 columns with the headers 'Player' and 'Handicap'. Values in
        the 'Player' column should be strings. Values in the 'Handicap' column should be integers
        or floats.

        Returns a PlayerGroup with data for all players in the sheet.
        """
        df = self.sheet_controller.worksheet_to_df("Players")
        df_columns = set(df.columns)

        expected_column_headers = {"Player", "Handicap"}
        if not df_columns or df_columns != expected_column_headers:
            raise SeasonSheetException(
                f"Malformed 'Players' sheet. Expected columns {expected_column_headers}, "
                f"but found columns {df_columns}."
            )

        if not are_series_values_string_type(df["Player"]):
            raise SeasonSheetException(
                "Malformed 'Players' sheet. Values in the 'Player' column should be strings."
            )

        if not are_series_values_int_or_float_type(df["Handicap"]):
            raise SeasonSheetException(
                "Malformed 'Players' sheet. Values in the 'Handicap' column should be integers "
                "or floats."
            )

        return player.PlayerGroup(
            player_list=[
                player.Player(
                    name=series.Player,
                    handicap=series.Handicap or 0  # empty handicaps are set to 0
                )
                for _, series in df.iterrows()
            ]
        )

    def read_player_handicaps_sheet(self, expected_events: List[str]) -> "season.SeasonPlayerGroup":
        """Read the 'Player Handicaps' worksheet in the 2023 SFSGT sheet.

        The 'Player Handicaps' tab should have a 'Player' heading in the first column with following
        column headers matching strings in the `expected_events` list argument. Values in the
        'Player' column should be strings. Values in each of the event column should be integers
        or floats.

        Returns a SeasonPlayerGroup with data for all players in the sheet.
        """
        df = self.sheet_controller.worksheet_to_df(worksheet_name="Player Handicaps")
        df_columns = df.columns

        if not len(df_columns) >= 2:
            raise SeasonSheetException(
                "Malformed 'Player Handicaps' sheet. There must be 2 or more columns."
            )

        if not df_columns[0] == "Player":
            raise SeasonSheetException(
                "Malformed 'Player Handicaps' sheet. The first column header should be 'Player'"
            )

        if (found_events := set(df_columns[1:])) != set(expected_events):
            raise SeasonSheetException(
                f"Malformed 'Player Handicaps' sheet. Expected events {expected_events} "
                f"but found {found_events}."
            )

        if not are_series_values_string_type(df["Player"]):
            raise SeasonSheetException(
                "Malformed 'Player Handicaps' sheet. Values in the 'Player' column should be strings."
            )

        for event_name in expected_events:
            if not are_series_values_int_or_float_type(df[event_name]):
                raise SeasonSheetException(
                    f"Malformed 'Player Handicaps' sheet. Values in the '{event_name}' column "
                    "should be integer or float."
                )

        # Raise the 'Player' column to the index to ease iteration
        df.set_index('Player', inplace=True)
        return season.SeasonPlayerGroup(
            player_list=[
                season.SeasonPlayer(
                    name=str(idx),
                    handicap_by_event=series.to_dict(),
                ) for idx, series in df.iterrows()
            ]
        )

    def read_courses_sheet(self) -> course.CourseGroup:
        """Read the 'Courses' worksheet in the 2023 SFSGT sheet.

        The 'Courses' tab should have the following columns with the listed types:
          Course: string
          Par: int
          Rating: float
          Slope: int
          Tee: string
          Distance: int

        Returns a CourseGroup with data for all players in the sheet.
        """
        df = self.sheet_controller.worksheet_to_df("Courses")

        df_columns = set(df.columns)

        expected_column_types = {
            "Course": str,
            "Par": int,
            "Rating": float,
            "Slope": int,
            "Tee": str,
            "Distance": int,
        }
        expected_column_headers = set(expected_column_types.keys())

        if not df_columns or df_columns != expected_column_headers:
            raise SeasonSheetException(
                f"Malformed 'Courses' sheet. Expected columns {expected_column_headers}, "
                f"but found columns {df_columns}."
            )

        for col, type_ in expected_column_types.items():
            if not df[col].apply(lambda x: isinstance(x, type_)).all():
                raise SeasonSheetException(
                    f"Malformed 'Courses' sheet. The '{col}' column values should "
                    f"all be {str(type_)} type."
                )

        return course.CourseGroup(
            course_list=[
                course.Course(
                    course_name=series.Course,
                    tee_name=series.Tee,
                    par=series.Par,
                    rating=series.Rating,
                    slope=series.Slope,
                    distance=series.Distance,
                )
                for _, series in df.iterrows()
            ]
        )

    def read_event_scorecard_sheet(
        self, worksheet_name: str, expected_players: List[str]
    ) -> event.EventScorecard:
        df = self.sheet_controller.worksheet_to_df(worksheet_name)

        expected_column_headers = set(
            ["Player", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Out", ""] +
            ["10", "11", "12", "13", "14", "15", "16", "17", "18", "In", "Total"]
        )

        if set(df.columns) != expected_column_headers:
            raise SeasonSheetException(
                f"Malformed '{worksheet_name}' sheet. Column headers do not match expectations.\n"
                f"\tExpected: {expected_column_headers} \n\tFound: {list(df.columns)}"
            )

        required_row_indices = {"Par", "Max"}
        # The first column (Player) acts as the header column for this check
        found_row_indices = set(df["Player"])
        if len(required_row_indices - found_row_indices) != 0:
            raise SeasonSheetException(
                f"Malformed '{worksheet_name}' sheet. The sheet must have a 'Par' "
                "and 'Max' row header. \n"
                f"\tExpected: {expected_column_headers}\n"
                f"\tFound:    {list(df.columns)}"
            )

        # Pull the Player column into the index so that we can easily identify
        # the "Max" and "Par" rows later
        df.set_index(keys="Player", inplace=True)

        # Drop unwanted rows and columns
        df.drop(["Max", "Par"], axis="index", inplace=True)
        df.drop(["Out", "", "In", "Total"], axis="columns", inplace=True)

        # Check that the players in this scorecard match the expectation. This must be done
        # after the unnecessary rows are removed.
        found_players = df.index.to_list()  # players are in the index at this point
        if (len(found_players) != len(expected_players)) or (found_players != expected_players):
            raise SeasonSheetException(
                f"Malformed '{worksheet_name}' sheet. Player names do not match the "
                "expected players list.\n"
                f"\tExpected Players: {expected_players}\n"
                f"\tFound Players:    {found_players}"
            )

        final_column_labels = ["1", "2", "3", "4", "5", "6", "7", "8", "9"] + [
            "10", "11", "12", "13", "14", "15", "16", "17", "18"
        ]
        if (len(final_column_labels) != len(df.columns) or any(df.columns != final_column_labels)):
            raise ValueError(f"Final column labels for sheet {worksheet_name} do not match expectations.")

        # Convert columns to dict
        df.columns = df.columns.astype(dtype=int)

        player_scorecards: Dict[str, event.EventPlayerScorecard] = {}
        for player_name, hole_scores in df.iterrows():
            # Replace empty scores with None values to better identify them later
            hole_scores.replace("", None, inplace=True)
            player_scorecards[player_name] = (
                event.EventPlayerScorecard(hole_scores=hole_scores.to_dict())
            )

        return event.EventScorecard(player_scorecards=player_scorecards)

    def write_sheet(self, workshet_name: str, worksheet_data_df: pd.DataFrame | pd.Series) -> None:
        """Write a dataframe to a worksheet.

        If the index is a column that you want in the table, it needs to be
        set into a column of the dataframe before calling this function.
        """
        self.sheet_controller.write_df_to_worksheet(
            worksheet_name=workshet_name, data=worksheet_data_df
        )

    def write_course_handicaps(self, course_handicaps_df: pd.DataFrame) -> None:
        self.sheet_controller.write_df_to_worksheet(worksheet_name="Course Handicaps", data=course_handicaps_df)

    def write_event_results(self, worksheet_name: str, results_df: pd.DataFrame) -> None:
        results_df = results_df.copy()
        # Raise the index into a 'Player' column for writing to the sheet
        results_df.reset_index(names=["Player"], inplace=True)
        results_df = dataframe_utils.fill_na_dtype_safe(
            df=results_df, fill_value="No Score",
        )

        def round_numerics(val: Any) -> Any:
            if isinstance(val, numbers.Real):
                if val % 1 == 0:
                    return round(val, 0)
                else:
                    return round(val, 2)
            else:
                return val

        results_df = results_df.map(round_numerics)

        self.sheet_controller.write_df_to_worksheet(worksheet_name=worksheet_name, data=results_df)

    def write_leaderboard(self, leaderboard_df: pd.DataFrame) -> None:
        self.sheet_controller.write_df_to_worksheet(
            worksheet_name="Leaderboard", data=leaderboard_df
        )

    def write_finale_handicaps(self, finale_handicaps_df: pd.DataFrame) -> None:
        self.sheet_controller.write_df_to_worksheet(
            worksheet_name="Finale Handicaps", data=finale_handicaps_df
        )


def are_series_values_string_type(ser: pd.Series) -> bool:
    return ser.apply(lambda x: isinstance(x, str)).all()


def are_series_values_int_or_float_type(ser: pd.Series) -> bool:
    return ser.apply(lambda x: isinstance(x, int) or isinstance(x, float)).all()

