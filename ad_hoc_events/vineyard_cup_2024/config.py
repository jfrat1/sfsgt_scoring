from typing import NamedTuple


class Player(NamedTuple):
    name: str
    handicap_index: float


class PlayerPair(NamedTuple):
    player_1: Player
    player_2: Player

    def players(self) -> tuple[Player, Player]:
        return (self.player_1, self.player_2)


class TeamPairs(NamedTuple):
    pair_1: PlayerPair
    pair_2: PlayerPair
    pair_3: PlayerPair
    pair_4: PlayerPair

    def pairs(self) -> tuple[PlayerPair, PlayerPair, PlayerPair, PlayerPair]:
        return (self.pair_1, self.pair_2, self.pair_3, self.pair_4)


class TeamIndividuals(NamedTuple):
    player_1: Player
    player_2: Player
    player_3: Player
    player_4: Player
    player_5: Player
    player_6: Player
    player_7: Player
    player_8: Player

    def players(self) -> tuple[Player, Player, Player, Player, Player, Player, Player, Player]:
        return (
            self.player_1,
            self.player_2,
            self.player_3,
            self.player_4,
            self.player_5,
            self.player_6,
            self.player_7,
            self.player_8,
        )


ERIK_PETRICH = Player(name="Erik Petrich", handicap_index=17.4)
THOMAS_KAUTH = Player(name="Thomas Kauth", handicap_index=12.8)
STEVE_HARASYM = Player(name="Steve Harasym", handicap_index=9.2)
TKS_OTHER_BOY = Player(name="TK's Other Boy (Craw)", handicap_index=8.0)
CULLAN_JACKSON = Player(name="Cullan Jackson", handicap_index=8.0)
WILL_DANIELS = Player(name="Will Daniels", handicap_index=10.1)
JOE_WIGNALL = Player(name="Joe Wignall", handicap_index=9.5)
WILLS_BOY = Player(name="Will's Boy (Zack)", handicap_index=5.0)
DAVID_ALVAREZ = Player(name="David Alvarez", handicap_index=22.9)
SCOTT_YOUNG = Player(name="Scott Young", handicap_index=18.7)
DREW_BARRETT = Player(name="Drew Barrett", handicap_index=8.4)
ZACH_AVILA = Player(name="Zach Avila", handicap_index=2.3)
STANTON_TURNER = Player(name="Stanton Turner", handicap_index=13.8)
JOHN_FRATELLO = Player(name="John Fratello", handicap_index=15.1)
OTTO_THORNTON_SILVER = Player(name="Otto Thornton-Silver", handicap_index=12.4)
TKS_BOY = Player(name="TK's Boy", handicap_index=10.0)
DREW_COLLINSHAW = Player(name="Drew Collinshaw", handicap_index=-1.0)
