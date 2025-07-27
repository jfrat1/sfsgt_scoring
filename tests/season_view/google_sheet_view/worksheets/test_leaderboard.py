from unittest import mock

import pytest
from google_sheet import GoogleWorksheet, RangeValues
from season_view.api.write_data import SeasonViewWriteLeaderboard, SeasonViewWriteLeaderboardPlayer
from season_view.google_sheet_view.worksheets.leaderboard import (
    FIRST_PLAYER_ROW,
    LeaderboardColumns,
    LeaderboardWorksheet,
)


class TestLeaderboardColumns:
    def test_column_string_values(self):
        """Test that enum values map to correct column letters."""
        assert str(LeaderboardColumns.SEASON_RANK) == "B"
        assert str(LeaderboardColumns.PLAYER_NAME) == "C"
        assert str(LeaderboardColumns.SEASON_POINTS) == "D"
        assert str(LeaderboardColumns.NUM_BIRDIES) == "E"
        assert str(LeaderboardColumns.EVENTS_PLAYED) == "G"
        assert str(LeaderboardColumns.EVENT_WINS) == "H"
        assert str(LeaderboardColumns.EVENT_TOP_FIVES) == "I"
        assert str(LeaderboardColumns.EVENT_TOP_TENS) == "J"
        assert str(LeaderboardColumns.NET_STROKES_WINS) == "L"
        assert str(LeaderboardColumns.NET_STROKES_TOP_FIVES) == "M"
        assert str(LeaderboardColumns.NET_STROKES_TOP_TENS) == "N"
        assert str(LeaderboardColumns.FIRST_EVENT) == "P"

    def test_column_addition(self):
        """Test that columns can be concatenated with strings."""
        assert LeaderboardColumns.SEASON_RANK + "4" == "B4"
        assert LeaderboardColumns.PLAYER_NAME + "10" == "C10"
        assert LeaderboardColumns.FIRST_EVENT + "1" == "P1"


class TestLeaderboardWorksheet:
    @pytest.fixture
    def sample_players(self):
        """Create sample player data for testing."""
        return [
            SeasonViewWriteLeaderboardPlayer(
                name="John Doe",
                season_points=150.0,
                season_rank=1,
                events_played=3,
                birdies=8,
                eagles=1,
                net_strokes_wins=2,
                net_strokes_top_fives=3,
                net_strokes_top_tens=3,
                event_wins=1,
                event_top_fives=2,
                event_top_tens=3,
                event_points={"Event 1": 50.0, "Event 2": 45.0, "Event 3": 55.0},
            ),
            SeasonViewWriteLeaderboardPlayer(
                name="Jane Smith",
                season_points=135.0,
                season_rank=2,
                events_played=3,
                birdies=6,
                eagles=0,
                net_strokes_wins=1,
                net_strokes_top_fives=2,
                net_strokes_top_tens=3,
                event_wins=0,
                event_top_fives=1,
                event_top_tens=2,
                event_points={"Event 1": 45.0, "Event 2": 50.0, "Event 3": 40.0},
            ),
            SeasonViewWriteLeaderboardPlayer(
                name="Bob Wilson",
                season_points=120.0,
                season_rank=3,
                events_played=2,
                birdies=4,
                eagles=0,
                net_strokes_wins=0,
                net_strokes_top_fives=1,
                net_strokes_top_tens=2,
                event_wins=0,
                event_top_fives=0,
                event_top_tens=1,
                event_points={"Event 1": 40.0, "Event 2": 0.0, "Event 3": 80.0},
            ),
        ]

    @pytest.fixture
    def sample_leaderboard_data(self, sample_players):
        """Create sample leaderboard data."""
        return SeasonViewWriteLeaderboard(players=sample_players)

    @pytest.fixture
    def mock_worksheet(self):
        """Create a mock GoogleWorksheet."""
        return mock.MagicMock(spec=GoogleWorksheet)

    @pytest.fixture
    def ordered_events(self):
        """Sample ordered event names."""
        return ["Event 1", "Event 2", "Event 3"]

    @pytest.fixture
    def leaderboard_worksheet(self, sample_leaderboard_data, mock_worksheet, ordered_events):
        """Create a LeaderboardWorksheet instance for testing."""
        return LeaderboardWorksheet(
            data=sample_leaderboard_data,
            worksheet_controller=mock_worksheet,
            ordered_event_names=ordered_events,
        )

    def test_initialization(self, sample_leaderboard_data, mock_worksheet, ordered_events):
        """Test LeaderboardWorksheet initialization."""
        worksheet = LeaderboardWorksheet(
            data=sample_leaderboard_data,
            worksheet_controller=mock_worksheet,
            ordered_event_names=ordered_events,
        )
        assert worksheet._data == sample_leaderboard_data
        assert worksheet._worksheet_controller == mock_worksheet
        assert worksheet._ordered_event_names == ordered_events

    def test_first_player_row(self, leaderboard_worksheet):
        """Test first player row returns the constant."""
        assert leaderboard_worksheet._first_player_row() == FIRST_PLAYER_ROW
        assert leaderboard_worksheet._first_player_row() == 4

    def test_last_player_row_with_multiple_players(self, leaderboard_worksheet):
        """Test last player row calculation with multiple players."""
        # 3 players: first row = 4, last row = 4 + 3 - 1 = 6
        assert leaderboard_worksheet._last_player_row() == 6

    def test_last_player_row_with_single_player(self, mock_worksheet, ordered_events):
        """Test last player row calculation with single player."""
        single_player_data = SeasonViewWriteLeaderboard(
            players=[
                SeasonViewWriteLeaderboardPlayer(
                    name="Solo Player",
                    season_points=100.0,
                    season_rank=1,
                    events_played=1,
                    birdies=2,
                    eagles=0,
                    net_strokes_wins=1,
                    net_strokes_top_fives=1,
                    net_strokes_top_tens=1,
                    event_wins=1,
                    event_top_fives=1,
                    event_top_tens=1,
                    event_points={"Event 1": 100.0},
                )
            ]
        )
        worksheet = LeaderboardWorksheet(
            data=single_player_data,
            worksheet_controller=mock_worksheet,
            ordered_event_names=["Event 1"],
        )
        # 1 player: first row = 4, last row = 4 + 1 - 1 = 4
        assert worksheet._last_player_row() == 4

    def test_standings_write_range_format(self, leaderboard_worksheet):
        """Test standings write range formatting and data extraction."""
        sorted_players = leaderboard_worksheet._data.players_rank_sorted()
        range_values = leaderboard_worksheet._standings_write_range(sorted_players)

        # Check range format: B4:E6 (3 players, rows 4-6)
        assert range_values.range == "B4:E6"

        # Check data format and content
        expected_values = [
            [1, "John Doe", 150.0, 8],  # Rank 1 player
            [2, "Jane Smith", 135.0, 6],  # Rank 2 player
            [3, "Bob Wilson", 120.0, 4],  # Rank 3 player
        ]
        assert range_values.values == expected_values

    def test_event_finishes_write_range_format(self, leaderboard_worksheet):
        """Test event finishes write range formatting and data extraction."""
        sorted_players = leaderboard_worksheet._data.players_rank_sorted()
        range_values = leaderboard_worksheet._event_finishes_write_range(sorted_players)

        # Check range format: G4:J6 (events played through event top tens)
        assert range_values.range == "G4:J6"

        # Check data format and content
        expected_values = [
            [3, 1, 2, 3],  # John: events_played, event_wins, event_top_fives, event_top_tens
            [3, 0, 1, 2],  # Jane
            [2, 0, 0, 1],  # Bob
        ]
        assert range_values.values == expected_values

    def test_net_strokes_finishes_write_range_format(self, leaderboard_worksheet):
        """Test net strokes finishes write range formatting and data extraction."""
        sorted_players = leaderboard_worksheet._data.players_rank_sorted()
        range_values = leaderboard_worksheet._net_strokes_finishes_write_range(sorted_players)

        # Check range format: L4:N6 (net strokes wins through net strokes top tens)
        assert range_values.range == "L4:N6"

        # Check data format and content
        expected_values = [
            [2, 3, 3],  # John: net_strokes_wins, net_strokes_top_fives, net_strokes_top_tens
            [1, 2, 3],  # Jane
            [0, 1, 2],  # Bob
        ]
        assert range_values.values == expected_values

    def test_event_points_write_range_format(self, leaderboard_worksheet):
        """Test event points write range formatting with dynamic columns."""
        sorted_players = leaderboard_worksheet._data.players_rank_sorted()
        range_values = leaderboard_worksheet._event_points_write_range(sorted_players)

        # Check range format: P4:R6 (3 events: P, Q, R)
        assert range_values.range == "P4:R6"

        # Check data format and content (ordered by event names)
        expected_values = [
            [50.0, 45.0, 55.0],  # John: Event 1, Event 2, Event 3
            [45.0, 50.0, 40.0],  # Jane
            [40.0, 0.0, 80.0],  # Bob
        ]
        assert range_values.values == expected_values

    def test_event_points_write_range_with_different_event_count(self, mock_worksheet):
        """Test event points range calculation with different number of events."""
        # Create player data with 5 events
        players_with_five_events = [
            SeasonViewWriteLeaderboardPlayer(
                name="John Doe",
                season_points=250.0,
                season_rank=1,
                events_played=5,
                birdies=10,
                eagles=2,
                net_strokes_wins=3,
                net_strokes_top_fives=4,
                net_strokes_top_tens=5,
                event_wins=2,
                event_top_fives=3,
                event_top_tens=5,
                event_points={
                    "Event 1": 50.0,
                    "Event 2": 45.0,
                    "Event 3": 55.0,
                    "Event 4": 50.0,
                    "Event 5": 50.0,
                },
            ),
        ]

        five_events_data = SeasonViewWriteLeaderboard(players=players_with_five_events)
        five_events = ["Event 1", "Event 2", "Event 3", "Event 4", "Event 5"]
        worksheet = LeaderboardWorksheet(
            data=five_events_data,
            worksheet_controller=mock_worksheet,
            ordered_event_names=five_events,
        )

        sorted_players = worksheet._data.players_rank_sorted()
        range_values = worksheet._event_points_write_range(sorted_players)

        # Range should be P4:T4 (P=16, Q=17, R=18, S=19, T=20) with single player
        assert range_values.range == "P4:T4"

    def test_event_points_write_range_with_single_event(self, sample_leaderboard_data, mock_worksheet):
        """Test event points range calculation with single event."""
        single_event = ["Event 1"]
        worksheet = LeaderboardWorksheet(
            data=sample_leaderboard_data,
            worksheet_controller=mock_worksheet,
            ordered_event_names=single_event,
        )

        sorted_players = worksheet._data.players_rank_sorted()
        range_values = worksheet._event_points_write_range(sorted_players)

        # Range should be P4:P6 (single column)
        assert range_values.range == "P4:P6"

        # Data should only have Event 1 points
        expected_values = [
            [50.0],  # John
            [45.0],  # Jane
            [40.0],  # Bob
        ]
        assert range_values.values == expected_values

    def test_write_method_calls_all_ranges(self, leaderboard_worksheet, mock_worksheet):
        """Test that write method calls all range writing methods."""
        leaderboard_worksheet.write()

        # Verify write_multiple_ranges was called once
        mock_worksheet.write_multiple_ranges.assert_called_once()

        # Get the argument passed to write_multiple_ranges
        call_args = mock_worksheet.write_multiple_ranges.call_args[0][0]

        # Should have 4 range values (standings, event finishes, net strokes, event points)
        assert len(call_args) == 4

        # Verify all ranges are RangeValues objects
        for range_value in call_args:
            assert isinstance(range_value, RangeValues)

        # Verify expected ranges are present
        ranges = [rv.range for rv in call_args]
        assert "B4:E6" in ranges  # standings
        assert "G4:J6" in ranges  # event finishes
        assert "L4:N6" in ranges  # net strokes
        assert "P4:R6" in ranges  # event points

    def test_write_method_with_empty_leaderboard(self, mock_worksheet, ordered_events):
        """Test write method with empty player list."""
        empty_data = SeasonViewWriteLeaderboard(players=[])
        worksheet = LeaderboardWorksheet(
            data=empty_data,
            worksheet_controller=mock_worksheet,
            ordered_event_names=ordered_events,
        )

        worksheet.write()

        # Should still call write_multiple_ranges (with empty ranges)
        mock_worksheet.write_multiple_ranges.assert_called_once()
        call_args = mock_worksheet.write_multiple_ranges.call_args[0][0]

        # All ranges should have empty values
        for range_value in call_args:
            assert range_value.values == []

    def test_player_data_is_rank_sorted(self, leaderboard_worksheet):
        """Test that player data is sorted by rank in all range methods."""
        # Create data with players in non-rank order
        unsorted_players = [
            SeasonViewWriteLeaderboardPlayer(
                name="Third Place",
                season_points=100.0,
                season_rank=3,
                events_played=1,
                birdies=2,
                eagles=0,
                net_strokes_wins=0,
                net_strokes_top_fives=0,
                net_strokes_top_tens=1,
                event_wins=0,
                event_top_fives=0,
                event_top_tens=1,
                event_points={"Event 1": 100.0},
            ),
            SeasonViewWriteLeaderboardPlayer(
                name="First Place",
                season_points=200.0,
                season_rank=1,
                events_played=1,
                birdies=5,
                eagles=1,
                net_strokes_wins=1,
                net_strokes_top_fives=1,
                net_strokes_top_tens=1,
                event_wins=1,
                event_top_fives=1,
                event_top_tens=1,
                event_points={"Event 1": 200.0},
            ),
        ]

        # Test that standings range has players in rank order
        standings_range = leaderboard_worksheet._standings_write_range(unsorted_players)

        # First row should be rank 3 player (as passed), second should be rank 1
        assert standings_range.values[0][0] == 3  # Third Place player rank
        assert standings_range.values[0][1] == "Third Place"
        assert standings_range.values[1][0] == 1  # First Place player rank
        assert standings_range.values[1][1] == "First Place"

        # But when we use the sorted data from the leaderboard data itself
        sorted_players = leaderboard_worksheet._data.players_rank_sorted()
        sorted_standings = leaderboard_worksheet._standings_write_range(sorted_players)

        # Should be in rank order: John (1), Jane (2), Bob (3)
        assert sorted_standings.values[0][1] == "John Doe"
        assert sorted_standings.values[1][1] == "Jane Smith"
        assert sorted_standings.values[2][1] == "Bob Wilson"
