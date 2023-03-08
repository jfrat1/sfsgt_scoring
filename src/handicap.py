

def scoring_differential(
    adjusted_gross_score: int,
    course_rating: float,
    course_slope: int,  
):
    return round(
        (113.0 / course_slope) * (adjusted_gross_score - course_rating),
        ndigits=1,
    )


def course_handicap(
    handicap_index: float,
    course_rating: float,
    course_slope: int,
    course_par: int,
) -> int:
    return int(round(
        handicap_index 
        * (course_slope / 113.0) 
        + (course_rating - course_par)
    ))