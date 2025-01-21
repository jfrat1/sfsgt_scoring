from courses import Course
from season_common.scorecard import CompleteScorecard, Scorecard
from season_model.api.input import SeasonModelEventPlayerInput
from season_model.api.result import (
    NotableHoles,
    NotableHoleType,
    SeasonModelCompleteEventPlayerIndividualResult,
    SeasonModelEventPlayerIndividualResult,
    SeasonModelIncompleteEventPlayerInividualResult,
)


class PlayerIndividualResultGenerator:
    _FRONT_9_HOLES = tuple(hole for hole in range(1, 10))
    _BACK_9_HOLES = tuple(hole for hole in range(10, 19))
    _ALL_HOLES = _FRONT_9_HOLES + _BACK_9_HOLES

    def __init__(
        self,
        input: SeasonModelEventPlayerInput,
        course: Course,
        tee: str,
    ) -> None:
        self._input = input
        self._course = course
        self._tee = tee

        # Initialize a multable instance to store notable holes.
        self._notable_holes = NotableHoles()

    def generate(self) -> SeasonModelEventPlayerIndividualResult:
        if not self._input.is_complete_score:
            return SeasonModelIncompleteEventPlayerInividualResult()

        return self._complete_score_result()

    def _complete_score_result(self) -> SeasonModelCompleteEventPlayerIndividualResult:
        adjusted_scorecard = self._adjust_scorecard_for_max_hole_strokes()
        self._note_below_par_holes(adjusted_scorecard)

        # TODO: This needs to be a playing handicap which accounts for a difference in pars
        # between players (tees). For example Harding Park 18 is a par 4 for men and a par 5 for women.
        # Need to determine the lowest par of all tees being used in event. If current player's tee
        # has a higher par, they receive that offset in strokes (to the lowest-par player).
        # See rule 6.2b at https://www.usga.org/handicapping/roh/Content/rules/6%202%20Playing%20Handicap%20Calculation.htm
        course_handicap = self._course.course_handicap(
            tee=self._tee,
            player_hcp_index=self._input.handicap_index,
        )
        front_9_gross_strokes = self._front_9_gross_strokes(adjusted_scorecard)
        back_9_gross_strokes = self._back_9_gross_strokes(adjusted_scorecard)
        gross_strokes = front_9_gross_strokes + back_9_gross_strokes
        net_strokes = gross_strokes - course_handicap
        score_differential = self._course.scoring_differential(
            tee=self._tee,
            gross_strokes=gross_strokes,
        )

        return SeasonModelCompleteEventPlayerIndividualResult(
            course_handicap=course_handicap,
            front_9_gross=front_9_gross_strokes,
            back_9_gross=back_9_gross_strokes,
            total_gross=gross_strokes,
            total_net=net_strokes,
            notable_holes=self._notable_holes,
            score_differential=score_differential,
        )

    def _adjust_scorecard_for_max_hole_strokes(self) -> Scorecard:
        adjusted_strokes: dict[int, int] = {}
        for hole in self._ALL_HOLES:
            par = self._course.hole_par(hole)
            max_strokes = self._double_par_plus_two(par)
            strokes = self._input.scorecard.hole_strokes(hole)

            if strokes > max_strokes:
                self._notable_holes.set_hole(hole_num=hole, hole_type=NotableHoleType.OVER_MAX)
                strokes = max_strokes

            adjusted_strokes[hole] = strokes

        return CompleteScorecard(scores=adjusted_strokes)

    def _front_9_gross_strokes(self, adjusted_strokes: Scorecard):
        return sum(
            strokes for hole_num, strokes in adjusted_strokes.scores().items() if hole_num in self._FRONT_9_HOLES
        )

    def _back_9_gross_strokes(self, adjusted_strokes: Scorecard):
        return sum(strokes for hole_num, strokes in adjusted_strokes.scores().items() if hole_num in self._BACK_9_HOLES)

    def _double_par_plus_two(_, par: int) -> int:
        return 2 * par + 2

    def _note_below_par_holes(self, adjusted_strokes: Scorecard) -> None:
        for hole in range(1, 19):
            par = self._course.hole_par(hole)
            strokes = adjusted_strokes.hole_strokes(hole)

            strokes_below_par = par - strokes

            match strokes_below_par:
                case 1:
                    self._notable_holes.set_hole(hole_num=hole, hole_type=NotableHoleType.BIRDIE)
                case 2:
                    self._notable_holes.set_hole(hole_num=hole, hole_type=NotableHoleType.EAGLE)
                case 3:
                    self._notable_holes.set_hole(hole_num=hole, hole_type=NotableHoleType.ALBATROSS)
