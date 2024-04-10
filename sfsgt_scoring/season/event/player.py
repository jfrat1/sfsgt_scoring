from . import course, inputs, results


class EventPlayerProcessError(Exception):
    """Exception to be raised when a processing error is encountered by an EventPlayer."""


class EventPlayer:
    _FRONT_9_HOLES = tuple(hole for hole in range(1, 10))
    _BACK_9_HOLES = tuple(hole for hole in range(10, 19))
    _ALL_HOLES = _FRONT_9_HOLES + _BACK_9_HOLES

    def __init__(self, input: inputs.EventPlayerInput, course_: course.Course):
        self._input = input
        self._course = course_
        self._notable_holes = results.NotableHoles()

    def individual_result(self) -> results.IPlayerEventIndividualResult:
        if isinstance(self._input.scorecard, inputs.IncompleteScorecard):
            return results.IncompletePlayerEventInividualResult()

        adjusted_scorecard = self._adjust_scorecard_for_max_hole_strokes()
        self._note_below_par_holes(adjusted_scorecard)

        course_handicap = self._course.player_course_handicap(self._input.handicap_index)
        front_9_gross_strokes = self._front_9_gross_strokes(adjusted_scorecard)
        back_9_gross_strokes = self._back_9_gross_strokes(adjusted_scorecard)
        gross_strokes = front_9_gross_strokes + back_9_gross_strokes
        net_strokes = gross_strokes - course_handicap

        return results.PlayerEventIndividualResult(
            course_handicap=course_handicap,
            front_9_gross=front_9_gross_strokes,
            back_9_gross=back_9_gross_strokes,
            total_gross=gross_strokes,
            total_net=net_strokes,
            notable_holes=self._notable_holes,
        )

    def _adjust_scorecard_for_max_hole_strokes(self) -> inputs.Scorecard:
        if isinstance(self._input.scorecard, inputs.IncompleteScorecard):
            raise EventPlayerProcessError(
                "Processing cannot be performed with an incomplete player scorecard."
            )

        adjusted_strokes: dict[int, int] = {}
        for hole in self._ALL_HOLES:
            par = self._course.hole_par(hole)
            max_strokes = self._double_par_plus_two(par)
            strokes = self._input.scorecard.hole_strokes(hole)

            if strokes > max_strokes:
                self._notable_holes.set_hole(hole_num=hole, score_type=results.NotableHoleType.OVER_MAX)
                strokes = max_strokes

            adjusted_strokes[hole] = strokes

        return inputs.Scorecard(strokes_per_hole=adjusted_strokes)

    def _front_9_gross_strokes(self, adjusted_strokes: inputs.Scorecard):
        return sum(
            strokes
            for hole_num, strokes in adjusted_strokes.strokes_per_hole().items()
            if hole_num in self._FRONT_9_HOLES
        )

    def _back_9_gross_strokes(self, adjusted_strokes: inputs.Scorecard):
        return sum(
            strokes
            for hole_num, strokes in adjusted_strokes.strokes_per_hole().items()
            if hole_num in self._BACK_9_HOLES
        )

    def _double_par_plus_two(_, par: int) -> int:
        return 2 * par + 2

    def _note_below_par_holes(self, adjusted_strokes: inputs.Scorecard) -> None:
        for hole in range(1, 19):
            par = self._course.hole_par(hole)
            strokes = adjusted_strokes.hole_strokes(hole)

            strokes_below_par = par - strokes

            match strokes_below_par:
                case 1:
                    self._notable_holes.set_hole(hole_num=hole, score_type=results.NotableHoleType.BIRDIE)
                case 2:
                    self._notable_holes.set_hole(hole_num=hole, score_type=results.NotableHoleType.EAGLE)
                case 3:
                    self._notable_holes.set_hole(hole_num=hole, score_type=results.NotableHoleType.ALBATROSS)
