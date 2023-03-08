from dataclasses import dataclass, field
from typing import List, Optional, Dict

from .course import Course, Tee
from .player import Player
from . import handicap

@dataclass()
class Event():
    course: Course
    players: List[Player]
    tee_name: str
    raw_scores: Dict[str, List[int]] = field(default_factory=dict)

    def __check_tee_is_available(self, tee_name: str):
        available_tees = self.course.available_tees()
        if tee_name not in available_tees:
            raise ValueError(
                f"Specified tee '{tee_name}' not available in course tees: {available_tees}"
            )

    def __validate(self):
        self.__check_tee_is_available(self.tee_name)
    
    def __post_init__(self):
        self.__validate()

    def _course_tee(self) -> Tee:
        for tee in self.course.tees:
            if self.tee_name == tee.name:
                return tee
        
        # Shouldn't ever be able to reach this as long as we validate
        # every time we change parameters in the object
        raise ValueError('Course tee not found in available course tees')

    def _calc_course_handicaps(self) -> Dict[str, int]:
        player_course_handicaps = {}
        tee = self._course_tee()
        
        for player in self.players:
            course_handicap = handicap.course_handicap(
                handicap_index=player.handicap,
                course_rating=tee.rating,
                course_slope=tee.slope,
                course_par=tee.par,
            )
            
            # (player.handicap * (tee.slope / 113)) + (tee.rating - tee.par)
            player_course_handicaps[player.name] = round(course_handicap, 0)

        return player_course_handicaps

    def course_handicaps(self) -> Dict[str, int]:
        return self._calc_course_handicaps()

    def set_tee_name(self, tee: str):
        self.__check_tee_is_available(tee)
        self.tee_name = tee
        self.__validate()

    def player_names(self) -> List[str]:
        return [player.name for player in self.players]
    
    def num_holes(self) -> int:
        return self.course.num_holes()

    def set_player_scores(self, player_name: str, scores: List[int]) -> None:
        available_player_names = self.player_names()
        if player_name not in available_player_names:
            raise ValueError(
                f"Player name '{player_name}' not found in available player names: {available_player_names}"
            )

        if not (
            isinstance(scores, list)
            and all(isinstance(score, int) for score in scores)
        ):
            raise TypeError(f"Incorrect type for argument 'scores'. Got {type(scores)}, expected list[int]")

        if (act := len(scores)) != (exp := self.num_holes()):
            raise ValueError(
                f"Incorrect number of scores for player {player_name}. Got {act}, expected {exp}"
            )

        self.raw_scores[player_name] = scores


