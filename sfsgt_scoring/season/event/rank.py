import abc


class IEventRank(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def as_str(self) -> str: pass


class EventRank(IEventRank):
    def __init__(self, rank: int) -> None:
        self._rank = rank

    def as_str(self) -> str:
        return str(self._rank)


class NoRank(IEventRank):
    def __new__(cls):
        # Implement the singleton pattern for NoRank objects because they are
        # stateless, identical, and numerous.
        if not hasattr(cls, 'instance'):
            cls.instance = super(NoRank, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pass

    def as_str(self) -> str:
        return "No Rank"
