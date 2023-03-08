from dataclasses import dataclass
from typing import List


@dataclass()
class Tee():
    name: str
    par: int
    rating: float
    slope: int
    distance: int

@dataclass()
class Hole():
    num: int
    par: int

    def __post_init__(self):
        assert self.num <= 18, f"Hole number can't be above 18, got {self.num}"
        assert self.par <= 5, f"Hole par can't be above 5, got {self.par}"

@dataclass()
class Course():
    name: str
    tees: List[Tee]

    # Specifying holes separately from tees assumes that par
    # doesn't change for any holes when tees are changed
    holes: List[Hole]

    def available_tees(self) -> List[str]:
        return [
            tee.name for tee in self.tees
        ]

    def total_par(self) -> int:
        return sum(hole.par for hole in self.holes)

    def num_holes(self) -> int:
        return len(self.holes)





