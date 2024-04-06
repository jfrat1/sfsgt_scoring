
from . import inputs, results


class Event:
    def __init__(self, input: inputs.EventInput) -> None:
        self._input = input

    def results(self) -> results.EventResult:
        # For each player in isolation, calculate:
        #   - out, in, total (gross) strokes
        #   - course handicap
        #   - net strokes
        #   - below par holes
        #
        # Cumulatively considering all players, calculate:
        #   - gross rank, net rank
        #   - gross points, net points
        #   - total event points
        #   - event rank

        # TODO - start here after refactoring of upstream modules is complete
        return None
