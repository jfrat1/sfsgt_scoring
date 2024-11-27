"""Tests for the SeasonPlayer and SeasonPlayerGroup classes in the season module."""

import pytest

from sfsgt_scoring_2023 import player, season


def test_season_player_constructor() -> None:
    test_player = season.SeasonPlayer(
        name="Bolt",
        handicap_by_event={
            "Presidio": 15.5,
            "Harding Park": 14,
        },
    )
    assert test_player.name == "Bolt"
    assert test_player.handicap_by_event == {
        "Presidio": 15.5,
        "Harding Park": 14,
    }


def test_season_player_event_handicap() -> None:
    test_player = season.SeasonPlayer(
        name="Bolt",
        handicap_by_event={
            "Presidio": 7.5,
            "Harding Park": 6,
        },
    )

    assert test_player.event_handicap("Presidio") == 7.5
    assert test_player.event_handicap("Harding Park") == 6


def test_season_player_event_handicap_undefined_event() -> None:
    test_player = season.SeasonPlayer(
        name="Bolt",
        handicap_by_event={
            "Presidio": 7.5,
            "Harding Park": 6,
        },
    )

    with pytest.raises(KeyError, match="Can't find event Not an Event"):
        test_player.event_handicap("Not an Event")


def test_season_player_group_constructor() -> None:
    player_list = [
        season.SeasonPlayer(
            name="Bolt",
            handicap_by_event={
                "Presidio": 7.5,
                "Harding Park": 6,
            },
        ),
        season.SeasonPlayer(
            name="Geoff",
            handicap_by_event={
                "Presidio": 15.5,
                "Harding Park": 14,
            },
        ),
    ]

    player_group = season.SeasonPlayerGroup(player_list=player_list)

    assert player_group.player_list == player_list


def test_season_player_group_get_event_player_group() -> None:
    player_list = [
        season.SeasonPlayer(
            name="Bolt",
            handicap_by_event={
                "Presidio": 7.5,
                "Harding Park": 6,
            },
        ),
        season.SeasonPlayer(
            name="Geoff",
            handicap_by_event={
                "Presidio": 15.5,
                "Harding Park": 14,
            },
        ),
    ]

    season_player_group = season.SeasonPlayerGroup(player_list=player_list)

    assert season_player_group.get_event_player_group("Presidio") == player.PlayerGroup(
        player_list=[
            player.Player(
                name="Bolt",
                handicap=7.5,
            ),
            player.Player(
                name="Geoff",
                handicap=15.5,
            ),
        ]
    )

    assert season_player_group.get_event_player_group("Harding Park") == player.PlayerGroup(
        player_list=[
            player.Player(
                name="Bolt",
                handicap=6,
            ),
            player.Player(
                name="Geoff",
                handicap=14,
            ),
        ]
    )


def test_season_player_group_player_names() -> None:
    player_list = [
        season.SeasonPlayer(
            name="Bolt",
            handicap_by_event={
                "Presidio": 7.5,
                "Harding Park": 6,
            },
        ),
        season.SeasonPlayer(
            name="Geoff",
            handicap_by_event={
                "Presidio": 15.5,
                "Harding Park": 14,
            },
        ),
    ]

    season_player_group = season.SeasonPlayerGroup(player_list=player_list)

    assert set(season_player_group.player_names()) == {"Bolt", "Geoff"}
