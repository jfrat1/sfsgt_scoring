from season_model.api.input import SeasonModelEventType

STANDARD_EVENT_POINTS_BY_RANK = {
    1: 50.0,
    2: 45.0,
    3: 37.5,
    4: 30.0,
    5: 25.0,
    6: 20.0,
    7: 19.5,
    8: 19.0,
    9: 18.5,
    10: 18.0,
    11: 17.5,
    12: 17.0,
    13: 16.5,
    14: 16.0,
    15: 15.5,
    16: 15.0,
    17: 14.5,
    18: 14.0,
    19: 13.5,
    20: 13.0,
    21: 12.5,
    22: 12.0,
    23: 11.5,
    24: 11.0,
    25: 10.5,
    26: 10.0,
    27: 9.5,
    28: 9.0,
    29: 8.5,
    30: 8.0,
    31: 7.5,
    32: 7.0,
    33: 6.5,
    34: 6.0,
    35: 5.5,
    36: 5.0,
    37: 4.5,
    38: 4.0,
    39: 3.5,
    40: 3.0,
    41: 2.5,
    42: 2.0,
    43: 1.5,
    44: 1.0,
    45: 0.5,
    46: 0.5,
    47: 0.5,
    48: 0.5,
    49: 0.5,
    50: 0.5,
}

MAJOR_EVENT_POINTS_BY_RANK = {rank: points * 2 for rank, points in STANDARD_EVENT_POINTS_BY_RANK.items()}


class UnknownEventTypeError(Exception):
    """Exception to be raised when an unknown event type is used to construct a points instance."""


class InvalidPlayerRanksError(Exception):
    """Exception to be raised when a disallowed player rank is detected."""


class Points:
    def __init__(self, event_type: SeasonModelEventType) -> None:
        self._points_by_rank = self._get_points_by_rank(event_type)

    def _get_points_by_rank(self, event_type: SeasonModelEventType):
        match event_type:
            case SeasonModelEventType.STANDARD:
                return STANDARD_EVENT_POINTS_BY_RANK

            case SeasonModelEventType.MAJOR:
                return MAJOR_EVENT_POINTS_BY_RANK

            case _:
                # Should not be reachable unless new event types are introduced.
                raise UnknownEventTypeError(f"Event type {event_type} is not recognized.")

    def player_points_from_ranks(self, player_ranks: dict[str, int]) -> dict[str, float]:
        if self._are_player_ranks_empty(player_ranks):
            return {}

        self._verify_player_ranks(player_ranks)
        players_at_each_rank = self._players_at_each_rank(player_ranks)

        # TODO: Consider adding verification of the points awarded to prove that we've
        # distributed them correctly for the ranks that are present
        return self._player_points(players_at_each_rank)

    def _are_player_ranks_empty(self, player_ranks: dict[str, int]) -> bool:
        return len(player_ranks) == 0

    def _verify_player_ranks(self, player_ranks: dict[str, int]):
        allowed_ranks = self._allowed_ranks()

        for player_name, rank in player_ranks.items():
            if rank not in allowed_ranks:
                raise InvalidPlayerRanksError(
                    f"Invalid rank ({rank}) found for player '{player_name}'."
                    f"Rank must be in the range [{min(allowed_ranks), max(allowed_ranks)}]."
                )

    def _allowed_ranks(self) -> tuple[int, ...]:
        return tuple(rank for rank in self._points_by_rank.keys())

    def _players_at_each_rank(self, player_ranks: dict[str, int]) -> dict[int, list[str]]:
        """Pivot the player ranks dictionary into one that has ranks as keys and sets of player names at each rank as values."""  # noqa: E501
        min_player_rank = min(player_ranks.values())
        max_player_rank = max(player_ranks.values())

        players_at_each_rank: dict[int, list[str]] = {}
        for rank in range(min_player_rank, max_player_rank + 1):
            players_at_each_rank[rank] = self._find_players_at_rank(rank, player_ranks)

        return players_at_each_rank

    def _find_players_at_rank(self, rank: int, player_ranks: dict[str, int]) -> list[str]:
        return [player_name for player_name, player_rank in player_ranks.items() if player_rank == rank]

    def _player_points(self, players_at_each_rank: dict[int, list[str]]) -> dict[str, float]:
        player_points: dict[str, float] = {}
        for rank, players in players_at_each_rank.items():
            num_players = len(players)
            if num_players == 0:
                continue

            points = self._points_for_players_at_rank(rank=rank, num_players=num_players)
            for player in players:
                player_points[player] = points

        return player_points

    def _points_for_players_at_rank(self, rank: int, num_players: int) -> float:
        if num_players == 1:
            return self._points_by_rank[rank]
        else:
            tied_ranks_range = range(rank, rank + num_players)
            tied_ranks_points = [self._points_by_rank[rank_] for rank_ in tied_ranks_range]
            points_for_tie = sum(tied_ranks_points) / num_players

            return points_for_tie
