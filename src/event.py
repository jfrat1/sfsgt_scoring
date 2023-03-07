from dataclasses import dataclass, field
from typing import List, Optional, Dict

from .course import Course, Tee
from .player import Player


@dataclass()
class Event():
    course: Course
    players: List[Player]
    tee_name: str

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

    def _get_course_tee(self) -> Tee:
        for tee in self.course.tees:
            if self.tee_name == tee.name:
                return tee
        
        # Shouldn't ever be able to reach this as long as we validate
        # every time we change parameters in the object
        raise ValueError('Course tee not found in available course tees')
        
    def _calc_course_handicaps(self) -> Dict[str, int]:
        player_course_handicaps = {}
        tee = self._get_course_tee()

        for player in self.players:
            course_handicap = (player.handicap * (tee.slope / 113)) + (tee.rating - tee.par)
            player_course_handicaps[player.name] = round(course_handicap, 0)

        return player_course_handicaps

    def course_handicaps(self) -> Dict[str, int]:
        return self._calc_course_handicaps()

    def set_course_tee(self, tee: str):
        self.__check_tee_is_available(tee)
        self.tee_name = tee
        self.__validate()


