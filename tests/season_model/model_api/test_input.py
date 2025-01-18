from unittest import mock

import pytest

from season_model.api import input


def test_season_model_event_inputs_iter() -> None:
    """Test that the __iter__ method of SeasonModelEventInputs works correctly."""
    stub_event_input_1 = mock.MagicMock(spec=input.SeasonModelEventInput, autospec=True)
    stub_event_input_1.event_name = "Event 1"
    stub_event_input_2 = mock.MagicMock(spec=input.SeasonModelEventInput, autospec=True)
    stub_event_input_2.event_name = "Event 2"

    event_inputs = input.SeasonModelEventInputs(events=[stub_event_input_1, stub_event_input_2])

    for idx, event_input in enumerate(event_inputs):
        assert event_input.event_name == f"Event {idx + 1}"


def test_season_model_input_constructor_verify_input_consistency_ok() -> None:
    player_names = ["Charlie Brown", "Snoopy"]

    stub_event_input_1 = mock.MagicMock(spec=input.SeasonModelEventInput, autospec=True)
    stub_event_input_1.player_names.return_value = player_names.copy()

    stub_event_input_2 = mock.MagicMock(spec=input.SeasonModelEventInput, autospec=True)
    stub_event_input_2.player_names.return_value = player_names.copy()

    event_inputs = input.SeasonModelEventInputs(events=[stub_event_input_1, stub_event_input_2])

    input.SeasonModelInput(
        player_names=player_names,
        events=event_inputs,
    )


def test_season_model_input_constructor_verify_input_consistency_out_of_order_names_ok() -> None:
    player_names = ["Charlie Brown", "Snoopy", "Linus"]

    stub_event_input_1 = mock.MagicMock(spec=input.SeasonModelEventInput, autospec=True)
    stub_event_input_1.player_names.return_value = ["Snoopy", "Linus", "Charlie Brown"]

    stub_event_input_2 = mock.MagicMock(spec=input.SeasonModelEventInput, autospec=True)
    stub_event_input_2.player_names.return_value = ["Linus", "Charlie Brown", "Snoopy"]

    event_inputs = input.SeasonModelEventInputs(events=[stub_event_input_1, stub_event_input_2])

    input.SeasonModelInput(
        player_names=player_names,
        events=event_inputs,
    )


def test_season_model_input_constructor_verify_input_consistency_fails() -> None:
    player_names = ["Charlie Brown", "Snoopy"]

    stub_event_input_1 = mock.MagicMock(spec=input.SeasonModelEventInput, autospec=True)
    stub_event_input_1.player_names.return_value = player_names.copy()

    stub_event_input_2 = mock.MagicMock(spec=input.SeasonModelEventInput, autospec=True)
    stub_event_input_2.player_names.return_value = ["Wrong Player"]

    event_inputs = input.SeasonModelEventInputs(events=[stub_event_input_1, stub_event_input_2])

    with pytest.raises(input.SeasonModelInputConsistencyError):
        input.SeasonModelInput(
            player_names=player_names,
            events=event_inputs,
        )
