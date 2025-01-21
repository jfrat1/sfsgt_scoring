import pandas as pd

import google_sheet
from season_common import player
from season_view.api import read_data

PLAYER_COLUMN = "Golfer"
GENDER_COLUMN = "Gender"


class PlayersWorksheetError(Exception):
    pass


class PlayersWorksheet:
    def __init__(
        self,
        worksheet_controller: google_sheet.GoogleWorksheet,
        events: list[str],
    ) -> None:
        self.worksheet_controller = worksheet_controller
        self.events = events

    def read(self) -> read_data.SeasonViewReadPlayers:
        raw_data = self.worksheet_controller.to_df(header_row=2)
        self._verify_columns_case_insensitive(raw_data)

        headers_lower = [col.lower() for col in raw_data.columns]
        raw_data.columns = pd.Index(headers_lower)
        raw_data.set_index(keys=PLAYER_COLUMN.lower(), inplace=True)

        are_finale_hcps_available = "finale" in headers_lower
        events = self.events + ["Finale"] if are_finale_hcps_available else self.events

        _players: list[read_data.SeasonViewReadPlayer] = []
        for player_name, player_data in raw_data.iterrows():
            _players.append(
                read_data.SeasonViewReadPlayer(
                    player=player.Player(
                        name=str(player_name),
                        gender=player.PlayerGender(player_data[GENDER_COLUMN.lower()]),
                    ),
                    event_handicap_indices=read_data.SeasonViewEventHandicapIndices(
                        {event: player_data[event.lower()] for event in events}
                    ),
                )
            )

        return read_data.SeasonViewReadPlayers(
            players=_players,
            are_finale_hcps_available=are_finale_hcps_available,
        )

    def _verify_columns_case_insensitive(self, raw_data: pd.DataFrame) -> None:
        required_columns = set(item.lower() for item in self.events + [PLAYER_COLUMN, GENDER_COLUMN])
        available_columns = set(column.lower() for column in raw_data.columns)

        missing_columns = required_columns.difference(available_columns)

        if len(missing_columns) != 0:
            raise PlayersWorksheetError(f"Players worksheet is missing required columns: {missing_columns}")
