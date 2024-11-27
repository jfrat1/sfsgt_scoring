def calc_course_handicap(handicap_index: float, par: int, rating: float, slope: int) -> int:
    return int(round(handicap_index * (slope / 113) + (rating - par)))


def calc_course_handicap_9_hole(handicap_index: float, par: int, rating: float, slope: int) -> int:
    """par, rating, and slope should be the 9-hole ratings for a course

    The handicap index is expected to be the 18 hole inded
    """
    handicap_index_9_hole = handicap_index / 2
    return int(round(handicap_index_9_hole * (slope / 113) + (rating - par)))


def calc_scoring_differential(total_score: int, rating: float, slope: int) -> float:
    return (113 / slope) * (total_score - rating)
