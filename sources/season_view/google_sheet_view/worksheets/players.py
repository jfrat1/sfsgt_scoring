import google_sheet
import pandas as pd
from season_common import player

from season_view.api import read_data

HEADER_ROW = 2

PLAYER_COLUMN = "Golfer"
GENDER_COLUMN = "Gender"
FINALE_COLUMN = "Finale"


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
        raw_data = self.worksheet_controller.to_df(header_row=HEADER_ROW)

        data = PlayersWorksheetData(raw_data=raw_data, events=self.events)

        return read_data.SeasonViewReadPlayers(
            players=data.read_players(),
            are_finale_hcps_available=data.are_finale_handicaps_available(),
        )


class PlayersWorksheetData:
    def __init__(self, raw_data: pd.DataFrame, events: list[str]) -> None:
        self._raw_data = raw_data
        self._events = events

        self._available_columns_lower = self._available_columns_lower_case()
        self._are_genders_available = GENDER_COLUMN.lower() in self._available_columns_lower
        self._are_finale_handicaps_available = FINALE_COLUMN.lower() in self._available_columns_lower

        if self._are_finale_handicaps_available:
            self._events.append(FINALE_COLUMN)

        self._verify_available_columns()
        self._cleanse_raw_data()

    def _available_columns_lower_case(self) -> list[str]:
        return [column.lower() for column in self._raw_data.columns]

    def _verify_available_columns(self) -> None:
        required_columns = self._events + [PLAYER_COLUMN]
        required_columns_lower = set(item.lower() for item in required_columns)

        missing_columns = required_columns_lower.difference(self._available_columns_lower)

        if len(missing_columns) != 0:
            raise PlayersWorksheetError(f"Players worksheet is missing required columns: {missing_columns}")

    def _cleanse_raw_data(self) -> None:
        self._raw_data.columns = pd.Index(self._available_columns_lower)
        self._raw_data.set_index(keys=PLAYER_COLUMN.lower(), inplace=True)

    def read_players(self) -> list[read_data.SeasonViewReadPlayer]:
        _players: list[read_data.SeasonViewReadPlayer] = []

        for player_name, player_data in self._raw_data.iterrows():
            player_gender = (
                player.PlayerGender(player_data[GENDER_COLUMN.lower()])
                if self._are_genders_available
                else player.PlayerGender.MALE  # Assume all players are male if there's no gender column.
            )
            _players.append(
                read_data.SeasonViewReadPlayer(
                    player=player.Player(
                        name=str(player_name),
                        gender=player_gender,
                    ),
                    event_handicap_indices=read_data.SeasonViewEventHandicapIndices(
                        {event: player_data[event.lower()] for event in self._events}
                    ),
                )
            )

        return _players

    def are_finale_handicaps_available(self) -> bool:
        return self._are_finale_handicaps_available
