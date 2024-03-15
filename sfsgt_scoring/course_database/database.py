import pathlib
from typing import List, Set, NamedTuple

from . import course

class DatabaseLoadError(Exception):
    """Exception to be raised when an error is encountered when loading the database."""


def database_from_folder(courses_dir: pathlib.Path) -> "CourseDatabase":
    courses: List[course.Course] = []
    for course_file in courses_dir.glob("*"):
        try:
            course_ = course.load_course_file(course_file)
            courses.append(course_)
        except course.CourseLoadError as exc:
            raise DatabaseLoadError(
                f"Unable to load database. Error encountere while processing file: {course_file}."
            ) from exc

    return CourseDatabase(courses)


class GetCourseError(Exception):
    """Exception to be raised when an error is encountered while searching for a course by name."""


class CourseDatabase(NamedTuple):
    courses: List[course.Course]

    def get_course(self, course_name: str) -> course.Course:
        candidate_courses = [course_ for course_ in self.courses if course_.name == course_name]
        num_candidates = len(candidate_courses)

        if num_candidates == 0:
            raise GetCourseError(f"Could not find any courses with the name {course_name} in database.")
        if num_candidates > 1:
            raise GetCourseError(f"Found more than 1 course with the name {course_name} in database.")

        return candidate_courses[0]

