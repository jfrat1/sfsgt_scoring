from unittest import mock

import pytest
from google_sheet import GoogleSheetController
from season_view.api import read_data, write_data
from season_view.google_sheet_view.core import (
    GoogleSheetSeasonView,
    GoogleSheetSeasonViewConfig,
    GoogleSheetSeasonViewError,
    GoogleSheetSeasonViewEventConfig,
)


class TestGoogleSheetSeasonViewEventConfig:
    def test_construction_and_properties(self):
        """Test basic construction and property access."""
        config = GoogleSheetSeasonViewEventConfig(
            event_number=1,
            event_name="Test Event",
            worksheet_name="Event1_Sheet",
            scorecard_start_cell="B5",
        )

        assert config.event_number == 1
        assert config.event_name == "Test Event"
        assert config.worksheet_name == "Event1_Sheet"
        assert config.scorecard_start_cell == "B5"

    def test_equality(self):
        """Test equality comparison between configs."""
        config1 = GoogleSheetSeasonViewEventConfig(
            event_number=1,
            event_name="Test Event",
            worksheet_name="Event1_Sheet",
            scorecard_start_cell="B5",
        )
        config2 = GoogleSheetSeasonViewEventConfig(
            event_number=1,
            event_name="Test Event",
            worksheet_name="Event1_Sheet",
            scorecard_start_cell="B5",
        )
        config3 = GoogleSheetSeasonViewEventConfig(
            event_number=2,
            event_name="Different Event",
            worksheet_name="Event2_Sheet",
            scorecard_start_cell="B6",
        )

        assert config1 == config2
        assert config1 != config3

    def test_immutability(self):
        """Test that config is immutable (NamedTuple behavior)."""
        config = GoogleSheetSeasonViewEventConfig(
            event_number=1,
            event_name="Test Event",
            worksheet_name="Event1_Sheet",
            scorecard_start_cell="B5",
        )

        with pytest.raises(AttributeError):
            config.event_number = 2


class TestGoogleSheetSeasonViewConfig:
    @pytest.fixture
    def sample_event_configs(self):
        """Create sample event configurations."""
        return [
            GoogleSheetSeasonViewEventConfig(
                event_number=2,
                event_name="Event B",
                worksheet_name="EventB_Sheet",
                scorecard_start_cell="B6",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Event A",
                worksheet_name="EventA_Sheet",
                scorecard_start_cell="B5",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=3,
                event_name="Event C",
                worksheet_name="EventC_Sheet",
                scorecard_start_cell="B7",
            ),
        ]

    @pytest.fixture
    def sample_config(self, sample_event_configs):
        """Create sample season view configuration."""
        return GoogleSheetSeasonViewConfig(
            leaderboard_worksheet_name="Leaderboard",
            players_worksheet_name="Players",
            event_worksheet_configs=sample_event_configs,
        )

    def test_construction(self, sample_config):
        """Test basic construction."""
        assert sample_config.leaderboard_worksheet_name == "Leaderboard"
        assert sample_config.players_worksheet_name == "Players"
        assert len(sample_config.event_worksheet_configs) == 3

    def test_worksheet_names_returns_unique_names(self, sample_config):
        """Test worksheet_names returns unique list of all worksheet names."""
        worksheet_names = sample_config.worksheet_names()

        expected_names = {
            "Leaderboard",
            "Players",
            "EventA_Sheet",
            "EventB_Sheet",
            "EventC_Sheet",
        }

        assert set(worksheet_names) == expected_names
        assert len(worksheet_names) == 5

    def test_event_names_property(self, sample_config):
        """Test event_names property returns event names in original order."""
        event_names = sample_config.event_names

        # Should match the order of event_worksheet_configs
        assert event_names == ["Event B", "Event A", "Event C"]

    def test_ordered_event_names_property(self, sample_config):
        """Test ordered_event_names property sorts by event_number."""
        ordered_names = sample_config.ordered_event_names

        # Should be sorted by event_number: 1, 2, 3
        assert ordered_names == ["Event A", "Event B", "Event C"]

    def test_ordered_event_names_with_mixed_numbers(self):
        """Test ordered_event_names with non-sequential event numbers."""
        event_configs = [
            GoogleSheetSeasonViewEventConfig(
                event_number=5,
                event_name="Event E",
                worksheet_name="EventE_Sheet",
                scorecard_start_cell="B5",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Event A",
                worksheet_name="EventA_Sheet",
                scorecard_start_cell="B6",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=3,
                event_name="Event C",
                worksheet_name="EventC_Sheet",
                scorecard_start_cell="B7",
            ),
        ]

        config = GoogleSheetSeasonViewConfig(
            leaderboard_worksheet_name="Leaderboard",
            players_worksheet_name="Players",
            event_worksheet_configs=event_configs,
        )

        ordered_names = config.ordered_event_names
        assert ordered_names == ["Event A", "Event C", "Event E"]

    def test_event_config_returns_correct_config(self, sample_config):
        """Test event_config returns the correct event configuration."""
        event_config = sample_config.event_config("Event A")

        assert event_config.event_number == 1
        assert event_config.event_name == "Event A"
        assert event_config.worksheet_name == "EventA_Sheet"
        assert event_config.scorecard_start_cell == "B5"

    def test_event_config_raises_error_for_missing_event(self, sample_config):
        """Test event_config raises ValueError for non-existent event."""
        with pytest.raises(ValueError) as exc_info:
            sample_config.event_config("Nonexistent Event")

        assert "No event named Nonexistent Event can be found." in str(exc_info.value)

    def test_empty_event_configs(self):
        """Test configuration with no events."""
        config = GoogleSheetSeasonViewConfig(
            leaderboard_worksheet_name="Leaderboard",
            players_worksheet_name="Players",
            event_worksheet_configs=[],
        )

        assert config.event_names == []
        assert config.ordered_event_names == []
        assert set(config.worksheet_names()) == {"Leaderboard", "Players"}

    def test_single_event_config(self):
        """Test configuration with single event."""
        event_configs = [
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Solo Event",
                worksheet_name="Solo_Sheet",
                scorecard_start_cell="B5",
            )
        ]

        config = GoogleSheetSeasonViewConfig(
            leaderboard_worksheet_name="Leaderboard",
            players_worksheet_name="Players",
            event_worksheet_configs=event_configs,
        )

        assert config.event_names == ["Solo Event"]
        assert config.ordered_event_names == ["Solo Event"]
        assert len(config.worksheet_names()) == 3

    def test_duplicate_event_names_raises_error(self):
        """Test that duplicate event names in configuration raise an error."""
        event_configs = [
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Duplicate Event",  # Same name
                worksheet_name="Event1_Sheet",
                scorecard_start_cell="B5",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=2,
                event_name="Duplicate Event",  # Same name
                worksheet_name="Event2_Sheet",
                scorecard_start_cell="B6",
            ),
        ]

        with pytest.raises(ValueError) as exc_info:
            GoogleSheetSeasonViewConfig(
                leaderboard_worksheet_name="Leaderboard",
                players_worksheet_name="Players",
                event_worksheet_configs=event_configs,
            )

        error_msg = str(exc_info.value)
        assert "duplicate event names" in error_msg.lower()
        assert "Duplicate Event" in error_msg

    def test_duplicate_worksheet_names_raises_error(self):
        """Test that duplicate worksheet names in event configs raise an error."""
        event_configs = [
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Event A",
                worksheet_name="Shared_Sheet",  # Same worksheet
                scorecard_start_cell="B5",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=2,
                event_name="Event B",
                worksheet_name="Shared_Sheet",  # Same worksheet
                scorecard_start_cell="B10",
            ),
        ]

        with pytest.raises(ValueError) as exc_info:
            GoogleSheetSeasonViewConfig(
                leaderboard_worksheet_name="Leaderboard",
                players_worksheet_name="Players",
                event_worksheet_configs=event_configs,
            )

        error_msg = str(exc_info.value)
        assert "duplicate worksheet names" in error_msg.lower()
        assert "Shared_Sheet" in error_msg

    def test_worksheet_name_conflicts_with_leaderboard_raises_error(self):
        """Test that event worksheet name conflicting with leaderboard worksheet raises error."""
        event_configs = [
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Event A",
                worksheet_name="Leaderboard",  # Conflicts with leaderboard worksheet
                scorecard_start_cell="B5",
            ),
        ]

        with pytest.raises(ValueError) as exc_info:
            GoogleSheetSeasonViewConfig(
                leaderboard_worksheet_name="Leaderboard",
                players_worksheet_name="Players",
                event_worksheet_configs=event_configs,
            )

        error_msg = str(exc_info.value)
        assert "worksheet name conflicts" in error_msg.lower()
        assert "Leaderboard" in error_msg

    def test_worksheet_name_conflicts_with_players_raises_error(self):
        """Test that event worksheet name conflicting with players worksheet raises error."""
        event_configs = [
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Event A",
                worksheet_name="Players",  # Conflicts with players worksheet
                scorecard_start_cell="B5",
            ),
        ]

        with pytest.raises(ValueError) as exc_info:
            GoogleSheetSeasonViewConfig(
                leaderboard_worksheet_name="Leaderboard",
                players_worksheet_name="Players",
                event_worksheet_configs=event_configs,
            )

        error_msg = str(exc_info.value)
        assert "worksheet name conflicts" in error_msg.lower()
        assert "Players" in error_msg

    def test_valid_unique_configuration_succeeds(self):
        """Test that valid configuration with unique names succeeds."""
        event_configs = [
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Unique Event A",
                worksheet_name="EventA_Sheet",
                scorecard_start_cell="B5",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=2,
                event_name="Unique Event B",
                worksheet_name="EventB_Sheet",
                scorecard_start_cell="B6",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=3,
                event_name="Unique Event C",
                worksheet_name="EventC_Sheet",
                scorecard_start_cell="B7",
            ),
        ]

        # This should not raise any errors
        config = GoogleSheetSeasonViewConfig(
            leaderboard_worksheet_name="Leaderboard",
            players_worksheet_name="Players",
            event_worksheet_configs=event_configs,
        )

        # Verify the configuration works correctly
        assert len(config.event_names) == 3
        assert len(set(config.event_names)) == 3  # All unique
        assert len(config.worksheet_names()) == 5  # 3 events + players + leaderboard
        assert len(set(config.worksheet_names())) == 5  # All unique

    def test_complex_duplicate_scenario(self):
        """Test complex scenario with multiple types of duplicates."""
        event_configs = [
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Event A",
                worksheet_name="Event_Sheet",
                scorecard_start_cell="B5",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=2,
                event_name="Event A",  # Duplicate event name
                worksheet_name="Event_Sheet",  # Also duplicate worksheet name
                scorecard_start_cell="B6",
            ),
        ]

        with pytest.raises(ValueError) as exc_info:
            GoogleSheetSeasonViewConfig(
                leaderboard_worksheet_name="Leaderboard",
                players_worksheet_name="Players",
                event_worksheet_configs=event_configs,
            )

        error_msg = str(exc_info.value)
        # Should catch the first validation error (likely event names since that would be checked first)
        assert ("duplicate event names" in error_msg.lower()) or ("duplicate worksheet names" in error_msg.lower())


class TestGoogleSheetSeasonView:
    @pytest.fixture
    def sample_event_configs(self):
        """Create sample event configurations."""
        return [
            GoogleSheetSeasonViewEventConfig(
                event_number=1,
                event_name="Event A",
                worksheet_name="EventA_Sheet",
                scorecard_start_cell="B5",
            ),
            GoogleSheetSeasonViewEventConfig(
                event_number=2,
                event_name="Event B",
                worksheet_name="EventB_Sheet",
                scorecard_start_cell="B6",
            ),
        ]

    @pytest.fixture
    def sample_config(self, sample_event_configs):
        """Create sample season view configuration."""
        return GoogleSheetSeasonViewConfig(
            leaderboard_worksheet_name="Leaderboard",
            players_worksheet_name="Players",
            event_worksheet_configs=sample_event_configs,
        )

    @pytest.fixture
    def mock_sheet_controller(self):
        """Create mock GoogleSheetController."""
        controller = mock.MagicMock(spec=GoogleSheetController)
        controller.worksheet_titles.return_value = [
            "Players",
            "Leaderboard",
            "EventA_Sheet",
            "EventB_Sheet",
        ]
        return controller

    @pytest.fixture
    def season_view(self, sample_config, mock_sheet_controller):
        """Create GoogleSheetSeasonView instance."""
        return GoogleSheetSeasonView(
            config=sample_config,
            sheet_controller=mock_sheet_controller,
        )

    def test_initialization_success(self, sample_config, mock_sheet_controller):
        """Test successful initialization with valid worksheets."""
        season_view = GoogleSheetSeasonView(
            config=sample_config,
            sheet_controller=mock_sheet_controller,
        )

        assert season_view._config == sample_config
        assert season_view._sheet_controller == mock_sheet_controller
        assert season_view._event_worksheets == {}

        # Verify worksheet verification was called
        mock_sheet_controller.worksheet_titles.assert_called_once()

    def test_initialization_missing_worksheets_raises_error(self, sample_config):
        """Test initialization raises error when required worksheets are missing."""
        mock_controller = mock.MagicMock(spec=GoogleSheetController)
        mock_controller.worksheet_titles.return_value = [
            "Players",
            # Missing "Leaderboard", "EventA_Sheet", "EventB_Sheet"
        ]

        with pytest.raises(GoogleSheetSeasonViewError) as exc_info:
            GoogleSheetSeasonView(
                config=sample_config,
                sheet_controller=mock_controller,
            )

        error_msg = str(exc_info.value)
        assert "Some required worksheets are not available" in error_msg
        assert "Missing worksheets:" in error_msg

    def test_verify_available_worksheets_success(self, season_view):
        """Test _verify_available_worksheets with all required worksheets present."""
        # This is tested implicitly in successful initialization
        # No exception should be raised
        pass

    def test_verify_available_worksheets_partial_missing(self, sample_config):
        """Test _verify_available_worksheets with some missing worksheets."""
        mock_controller = mock.MagicMock(spec=GoogleSheetController)
        mock_controller.worksheet_titles.return_value = [
            "Players",
            "EventA_Sheet",
            # Missing "Leaderboard", "EventB_Sheet"
        ]

        with pytest.raises(GoogleSheetSeasonViewError) as exc_info:
            GoogleSheetSeasonView(
                config=sample_config,
                sheet_controller=mock_controller,
            )

        error_msg = str(exc_info.value)
        missing_sheets = {"Leaderboard", "EventB_Sheet"}
        for sheet in missing_sheets:
            assert sheet in error_msg

    @mock.patch("season_view.google_sheet_view.worksheets.PlayersWorksheet")
    def test_read_players_worksheet(self, mock_players_worksheet_class, season_view, mock_sheet_controller):
        """Test _read_players_worksheet creates and calls PlayersWorksheet correctly."""
        mock_players_worksheet = mock.MagicMock()
        mock_players_data = mock.MagicMock(spec=read_data.SeasonViewReadPlayers)
        mock_players_worksheet.read.return_value = mock_players_data
        mock_players_worksheet_class.return_value = mock_players_worksheet

        mock_worksheet_controller = mock.MagicMock()
        mock_sheet_controller.worksheet.return_value = mock_worksheet_controller

        result = season_view._read_players_worksheet()

        # Verify PlayersWorksheet was created correctly
        mock_players_worksheet_class.assert_called_once_with(
            worksheet_controller=mock_worksheet_controller,
            events=["Event A", "Event B"],
        )

        # Verify worksheet controller was requested
        mock_sheet_controller.worksheet.assert_called_with("Players")

        # Verify read was called and result returned
        mock_players_worksheet.read.assert_called_once()
        assert result == mock_players_data

    @mock.patch("season_view.google_sheet_view.worksheets.EventWorksheet")
    def test_generate_event_worksheets(self, mock_event_worksheet_class, season_view, mock_sheet_controller):
        """Test _generate_event_worksheets creates EventWorksheet for each event."""
        mock_event_worksheet_a = mock.MagicMock()
        mock_event_worksheet_b = mock.MagicMock()
        mock_event_worksheet_class.side_effect = [mock_event_worksheet_a, mock_event_worksheet_b]

        mock_worksheet_controller_a = mock.MagicMock()
        mock_worksheet_controller_b = mock.MagicMock()
        mock_sheet_controller.worksheet.side_effect = [mock_worksheet_controller_a, mock_worksheet_controller_b]

        players = ["Player 1", "Player 2", "Player 3"]
        result = season_view._generate_event_worksheets(players)

        # Verify EventWorksheet created for each event
        assert len(mock_event_worksheet_class.call_args_list) == 2

        # Check Event A worksheet creation
        call_args_a = mock_event_worksheet_class.call_args_list[0]
        assert call_args_a[1]["event_name"] == "Event A"
        assert call_args_a[1]["worksheet_controller"] == mock_worksheet_controller_a
        assert call_args_a[1]["scorecard_start_cell"] == "B5"
        assert call_args_a[1]["players"] == players

        # Check Event B worksheet creation
        call_args_b = mock_event_worksheet_class.call_args_list[1]
        assert call_args_b[1]["event_name"] == "Event B"
        assert call_args_b[1]["worksheet_controller"] == mock_worksheet_controller_b
        assert call_args_b[1]["scorecard_start_cell"] == "B6"
        assert call_args_b[1]["players"] == players

        # Verify result structure
        assert result == {
            "Event A": mock_event_worksheet_a,
            "Event B": mock_event_worksheet_b,
        }

        # Verify worksheet controllers were requested
        mock_sheet_controller.worksheet.assert_any_call("EventA_Sheet")
        mock_sheet_controller.worksheet.assert_any_call("EventB_Sheet")

    def test_read_event_worksheets(self, season_view):
        """Test _read_event_worksheets reads from all event worksheets."""
        # Set up mock event worksheets
        mock_event_worksheet_a = mock.MagicMock()
        mock_event_worksheet_b = mock.MagicMock()
        mock_event_data_a = mock.MagicMock(spec=read_data.SeasonViewReadEvent)
        mock_event_data_b = mock.MagicMock(spec=read_data.SeasonViewReadEvent)
        mock_event_worksheet_a.read.return_value = mock_event_data_a
        mock_event_worksheet_b.read.return_value = mock_event_data_b

        season_view._event_worksheets = {
            "Event A": mock_event_worksheet_a,
            "Event B": mock_event_worksheet_b,
        }

        result = season_view._read_event_worksheets()

        # Verify read called on all event worksheets
        mock_event_worksheet_a.read.assert_called_once()
        mock_event_worksheet_b.read.assert_called_once()

        # Verify result is correct type with expected data
        assert isinstance(result, read_data.SeasonViewReadEvents)
        assert result["Event A"] == mock_event_data_a
        assert result["Event B"] == mock_event_data_b

    @mock.patch("season_view.google_sheet_view.worksheets.PlayersWorksheet")
    @mock.patch("season_view.google_sheet_view.worksheets.EventWorksheet")
    def test_read_season_complete_workflow(
        self, mock_event_worksheet_class, mock_players_worksheet_class, season_view, mock_sheet_controller
    ):
        """Test complete read_season workflow integration."""
        # Set up mock players worksheet
        mock_players_worksheet = mock.MagicMock()
        mock_players_data = mock.MagicMock(spec=read_data.SeasonViewReadPlayers)
        mock_players_data.player_names = ["Player 1", "Player 2"]
        mock_players_worksheet.read.return_value = mock_players_data
        mock_players_worksheet_class.return_value = mock_players_worksheet

        # Set up mock event worksheets
        mock_event_worksheet_a = mock.MagicMock()
        mock_event_worksheet_b = mock.MagicMock()
        mock_event_data_a = mock.MagicMock(spec=read_data.SeasonViewReadEvent)
        mock_event_data_b = mock.MagicMock(spec=read_data.SeasonViewReadEvent)
        mock_event_worksheet_a.read.return_value = mock_event_data_a
        mock_event_worksheet_b.read.return_value = mock_event_data_b
        mock_event_worksheet_class.side_effect = [mock_event_worksheet_a, mock_event_worksheet_b]

        # Set up sheet controller mocks
        mock_worksheet_controllers = [mock.MagicMock() for _ in range(3)]
        mock_sheet_controller.worksheet.side_effect = mock_worksheet_controllers

        result = season_view.read_season()

        # Verify result structure
        assert isinstance(result, read_data.SeasonViewReadData)
        assert result.players == mock_players_data
        assert isinstance(result.events, read_data.SeasonViewReadEvents)

        # Verify event worksheets were stored
        assert len(season_view._event_worksheets) == 2
        assert season_view._event_worksheets["Event A"] == mock_event_worksheet_a
        assert season_view._event_worksheets["Event B"] == mock_event_worksheet_b

    def test_write_season_before_read_raises_error(self, season_view):
        """Test write_season raises error when called before read_season."""
        mock_write_data = mock.MagicMock(spec=write_data.SeasonViewWriteData)

        with pytest.raises(GoogleSheetSeasonViewError) as exc_info:
            season_view.write_season(mock_write_data)

        error_msg = str(exc_info.value)
        assert "An unexpected error has occurred" in error_msg
        assert "read before it was written to" in error_msg

    @mock.patch("season_view.google_sheet_view.worksheets.LeaderboardWorksheet")
    def test_write_season_complete_workflow(self, mock_leaderboard_worksheet_class, season_view, mock_sheet_controller):
        """Test complete write_season workflow."""
        # Set up event worksheets (simulate after read)
        mock_event_worksheet_a = mock.MagicMock()
        mock_event_worksheet_b = mock.MagicMock()
        season_view._event_worksheets = {
            "Event A": mock_event_worksheet_a,
            "Event B": mock_event_worksheet_b,
        }

        # Set up write data
        mock_write_data = mock.MagicMock(spec=write_data.SeasonViewWriteData)
        mock_event_data_a = mock.MagicMock()
        mock_event_data_b = mock.MagicMock()
        mock_write_data.get_event.side_effect = lambda event_name: {
            "Event A": mock_event_data_a,
            "Event B": mock_event_data_b,
        }[event_name]
        mock_leaderboard_data = mock.MagicMock()
        mock_write_data.leaderboard = mock_leaderboard_data

        # Set up leaderboard worksheet
        mock_leaderboard_worksheet = mock.MagicMock()
        mock_leaderboard_worksheet_class.return_value = mock_leaderboard_worksheet
        mock_leaderboard_controller = mock.MagicMock()
        mock_sheet_controller.worksheet.return_value = mock_leaderboard_controller

        season_view.write_season(mock_write_data)

        # Verify event data writing
        mock_write_data.get_event.assert_any_call(event_name="Event A")
        mock_write_data.get_event.assert_any_call(event_name="Event B")
        mock_event_worksheet_a.write.assert_called_once_with(data=mock_event_data_a)
        mock_event_worksheet_b.write.assert_called_once_with(data=mock_event_data_b)

        # Verify leaderboard writing
        mock_sheet_controller.worksheet.assert_called_with("Leaderboard")
        mock_leaderboard_worksheet_class.assert_called_once_with(
            data=mock_leaderboard_data,
            worksheet_controller=mock_leaderboard_controller,
            ordered_event_names=["Event A", "Event B"],
        )
        mock_leaderboard_worksheet.write.assert_called_once()

    def test_write_season_missing_event_data(self, season_view):
        """Test write_season when write data is missing an event."""
        # Set up event worksheets (simulate after read)
        mock_event_worksheet_a = mock.MagicMock()
        mock_event_worksheet_b = mock.MagicMock()
        season_view._event_worksheets = {
            "Event A": mock_event_worksheet_a,
            "Event B": mock_event_worksheet_b,
        }

        # Set up write data missing Event B
        mock_write_data = mock.MagicMock(spec=write_data.SeasonViewWriteData)

        def mock_get_event(event_name):
            if event_name == "Event A":
                return mock.MagicMock()
            elif event_name == "Event B":
                raise KeyError(f"No event data for {event_name}")

        mock_write_data.get_event.side_effect = mock_get_event

        # Should propagate the error from get_event
        with pytest.raises(KeyError):
            season_view.write_season(mock_write_data)

    def test_large_number_of_events(self):
        """Test configuration and workflow with many events."""
        # Create 10 events
        event_configs = [
            GoogleSheetSeasonViewEventConfig(
                event_number=i,
                event_name=f"Event {i}",
                worksheet_name=f"Event{i}_Sheet",
                scorecard_start_cell="B5",
            )
            for i in range(1, 11)
        ]

        config = GoogleSheetSeasonViewConfig(
            leaderboard_worksheet_name="Leaderboard",
            players_worksheet_name="Players",
            event_worksheet_configs=event_configs,
        )

        # Test ordered event names
        ordered_names = config.ordered_event_names
        expected_names = [f"Event {i}" for i in range(1, 11)]
        assert ordered_names == expected_names

        # Test worksheet names
        worksheet_names = config.worksheet_names()
        assert len(worksheet_names) == 12  # 10 events + players + leaderboard

    def test_empty_configuration_edge_case(self):
        """Test behavior with empty event configurations."""
        config = GoogleSheetSeasonViewConfig(
            leaderboard_worksheet_name="Leaderboard",
            players_worksheet_name="Players",
            event_worksheet_configs=[],
        )

        mock_controller = mock.MagicMock(spec=GoogleSheetController)
        mock_controller.worksheet_titles.return_value = ["Players", "Leaderboard"]

        season_view = GoogleSheetSeasonView(
            config=config,
            sheet_controller=mock_controller,
        )

        # Test that empty events don't break anything
        assert season_view._config.event_names == []
        assert season_view._config.ordered_event_names == []
