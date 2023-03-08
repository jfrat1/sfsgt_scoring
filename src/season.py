from dataclasses import dataclass
from typing import List

from .event import Event



@dataclass()
class Season():
    year: int
    events: List[Event]