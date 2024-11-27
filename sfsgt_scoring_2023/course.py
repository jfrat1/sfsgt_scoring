import dataclasses
from typing import List


@dataclasses.dataclass(eq=True, frozen=True)
class Course:
    """Defines a single course with a course name, tee name, and data specific to the tee."""

    course_name: str
    tee_name: str
    par: int
    rating: float
    slope: int
    distance: int


class CourseGroup:
    """Defins a group of courses."""

    def __init__(self, course_list: List[Course]) -> None:
        """Comstruct an instance of CourseGroup based on a list of Course objects."""
        self.course_list = course_list

    def get_course(self, course_name: str) -> Course:
        """Get a specific course by name.

        Raises:
            KeyError:
                If the course group has no courses defined in it.
                If the specific course name cannot be found in the list of courses.
        """
        candidate_courses = [
            course for course in self.course_list if course.course_name == course_name
        ]
        num_candidates = len(candidate_courses)
        if num_candidates == 0:
            raise KeyError(f"Couldn't find any courses named {course_name}")

        if num_candidates > 1:
            raise KeyError(f"Found too many courses named {course_name}.")

        return candidate_courses[0]

    def course_names(self) -> List[str]:
        """List of course names in the group."""
        return [course.course_name for course in self.course_list]
