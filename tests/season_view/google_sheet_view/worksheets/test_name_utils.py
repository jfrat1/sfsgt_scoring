from unittest.mock import patch

import pytest
from season_view.google_sheet_view.features import NameCase
from season_view.google_sheet_view.worksheets.name_utils import _canonicalize_player_name, process_raw_player_name


class TestCanonicalizePlayerName:
    def test_canonicalize_sortable_name(self) -> None:
        name = "Doe, John"
        assert _canonicalize_player_name(name) == "John Doe"

    def test_canonicalize_already_canonical_name_does_nothing(self) -> None:
        name = "John Doe"
        assert _canonicalize_player_name(name) == name

    def test_canonicalize_name_with_multiple_commas_raises_error(self) -> None:
        name = "Doe, John, Jr"
        with pytest.raises(ValueError, match="Player names with commas.*should have only 1 comma"):
            _canonicalize_player_name(name)

    def test_canonicalize_name_with_extra_whitespace(self) -> None:
        name = "  Doe  ,  John  "
        assert _canonicalize_player_name(name) == "John Doe"

    def test_canonicalize_single_name(self) -> None:
        name = "Madonna"
        assert _canonicalize_player_name(name) == "Madonna"


class TestProcessRawPlayerName:
    def test_process_with_title_case(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.TITLE),
        ):
            result = process_raw_player_name("doe, john")
            assert result == "John Doe"

    def test_process_with_upper_case(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.UPPER),
        ):
            result = process_raw_player_name("doe, john")
            assert result == "JOHN DOE"

    def test_process_with_lower_case(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.LOWER),
        ):
            result = process_raw_player_name("Doe, John")
            assert result == "john doe"

    def test_process_without_canonicalization_title_case(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", False),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.TITLE),
        ):
            result = process_raw_player_name("doe, john")
            assert result == "Doe, John"

    def test_process_without_canonicalization_upper_case(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", False),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.UPPER),
        ):
            result = process_raw_player_name("doe, john")
            assert result == "DOE, JOHN"

    def test_process_without_canonicalization_lower_case(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", False),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.LOWER),
        ):
            result = process_raw_player_name("DOE, JOHN")
            assert result == "doe, john"

    def test_process_canonical_name_with_title_case(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.TITLE),
        ):
            result = process_raw_player_name("john doe")
            assert result == "John Doe"

    def test_process_canonical_name_with_upper_case(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.UPPER),
        ):
            result = process_raw_player_name("John Doe")
            assert result == "JOHN DOE"

    def test_process_canonical_name_with_lower_case(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.LOWER),
        ):
            result = process_raw_player_name("John Doe")
            assert result == "john doe"

    def test_process_empty_string(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.TITLE),
        ):
            result = process_raw_player_name("")
            assert result == ""

    def test_process_single_name_with_case_transformation(self) -> None:
        with (
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_CANONICALIZE_PLAYER_NAMES", True),
            patch("season_view.google_sheet_view.worksheets.name_utils.features.FTR_PLAYER_NAME_CASE", NameCase.UPPER),
        ):
            result = process_raw_player_name("madonna")
            assert result == "MADONNA"
