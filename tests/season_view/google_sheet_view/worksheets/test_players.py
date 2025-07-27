import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from season_view.google_sheet_view.worksheets.players import PlayersWorksheetData
from season_view.google_sheet_view.features import NameCase
from season_common import player

STUB_EVENTS = ["Baylands", "Corica"]


class TestPlayersWorksheetDataNameProcessing:
    def test_read_players_applies_name_processing_with_title_case(self) -> None:
        raw_data = pd.DataFrame({
            "Gender": ["Male", "Female"],
            "Baylands": [15.2, 18.5],
            "Corica": [14.8, 17.9]
        }, index=["doe, john", "SMITH, JANE"])
        
        worksheet_data = PlayersWorksheetData(
            raw_data=raw_data,
            events=STUB_EVENTS
        )
        
        with patch("season_view.google_sheet_view.worksheets.utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True), \
             patch("season_view.google_sheet_view.worksheets.utils.features.FTR_PLAYER_NAME_CASE", NameCase.TITLE):
            players = worksheet_data.read_players()
            
        player_names = [p.player_name for p in players]
        assert "John Doe" in player_names
        assert "Jane Smith" in player_names
        assert "doe, john" not in player_names
        assert "SMITH, JANE" not in player_names

    def test_read_players_applies_name_processing_with_upper_case(self) -> None:
        raw_data = pd.DataFrame({
            "Gender": ["Male"],
            "Baylands": [15.2],
            "Corica": [14.8]
        }, index=["doe, john"])
        
        worksheet_data = PlayersWorksheetData(
            raw_data=raw_data,
            events=STUB_EVENTS
        )
        
        with patch("season_view.google_sheet_view.worksheets.utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True), \
             patch("season_view.google_sheet_view.worksheets.utils.features.FTR_PLAYER_NAME_CASE", NameCase.UPPER):
            players = worksheet_data.read_players()
            
        assert players[0].player_name == "JOHN DOE"

    def test_read_players_without_canonicalization(self) -> None:
        raw_data = pd.DataFrame({
            "Gender": ["Male"],
            "Baylands": [15.2],
            "Corica": [14.8]
        }, index=["doe, john"])
        
        worksheet_data = PlayersWorksheetData(
            raw_data=raw_data,
            events=STUB_EVENTS
        )
        
        with patch("season_view.google_sheet_view.worksheets.utils.features.FTR_CANONICALIZE_PLAYER_NAMES", False), \
             patch("season_view.google_sheet_view.worksheets.utils.features.FTR_PLAYER_NAME_CASE", NameCase.TITLE):
            players = worksheet_data.read_players()
            
        assert players[0].player_name == "Doe, John"

    def test_read_players_preserves_other_data_with_name_processing(self) -> None:
        raw_data = pd.DataFrame({
            "Gender": ["Male"],
            "Baylands": [15.2],
            "Corica": [14.8]
        }, index=["doe, john"])
        
        worksheet_data = PlayersWorksheetData(
            raw_data=raw_data,
            events=STUB_EVENTS
        )
        
        with patch("season_view.google_sheet_view.worksheets.utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True), \
             patch("season_view.google_sheet_view.worksheets.utils.features.FTR_PLAYER_NAME_CASE", NameCase.TITLE):
            players = worksheet_data.read_players()
            
        assert len(players) == 1
        player_data = players[0]
        assert player_data.player_name == "John Doe"
        assert player_data.player.gender == player.PlayerGender.MALE
        assert player_data.event_handicap_indices["Baylands"] == 15.2
        assert player_data.event_handicap_indices["Corica"] == 14.8
