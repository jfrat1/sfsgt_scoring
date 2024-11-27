import dataclasses
from typing import Generator, List


# When both eq and frozen are True, it makes Player hashable so we can use it as
# keys in a dictionary
@dataclasses.dataclass(eq=True, frozen=True)
class Player:
    """A single player with a name and handicap index."""

    name: str
    handicap: float


class PlayerGroup:
    """Defines a group of players."""

    def __init__(self, player_list: List[Player]) -> None:
        """Construct an instance of PlayerGroup based on a list of Player objects."""
        self.player_list = player_list

    def get_player(self, player_name: str) -> Player:
        """Get a single player from the group by name."""
        candidate_players = [player for player in self.player_list if player.name == player_name]
        num_candidates = len(candidate_players)
        if num_candidates == 0:
            raise KeyError(f"Couldn't find any players named {player_name}")

        if num_candidates > 1:
            raise KeyError(f"Found too many players named {player_name}.")

        return candidate_players[0]

    def player_names(self) -> List[str]:
        """List of player names in the group."""
        return [player.name for player in self.player_list]

    def __iter__(self) -> Generator[Player, None, None]:
        for player_ in self.player_list:
            yield player_

    def __getitem__(self, index: int) -> Player:
        return self.player_list[index]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PlayerGroup):
            return self.player_list == other.player_list
        else:
            return NotImplemented
