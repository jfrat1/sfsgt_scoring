import pathlib
from typing import NamedTuple

from . import course


DEFAULT_COURSE_DATABASE_PATH = pathlib.Path(__file__).parent / "data"


class DatabaseLoadError(Exception):
    """Exception to be raised when an error is encountered while attempting to load the database."""


class GetCourseError(Exception):
    """Exception to be raised when an error is encountered while searching for a course by name."""


def load_default_database() -> "CourseDatabase":
    return database_from_folder(courses_dir=DEFAULT_COURSE_DATABASE_PATH)


def database_from_folder(courses_dir: pathlib.Path) -> "CourseDatabase":
    courses: list[course.Course] = []
    for course_file in courses_dir.glob("*"):
        try:
            course_ = course.load_course_file(course_file)
            courses.append(course_)
        except course.CourseLoadError as exc:
            raise DatabaseLoadError(
                f"Unable to load database. Error encountere while processing file: {course_file}."
            ) from exc

    return CourseDatabase(courses)


class CourseDatabase(NamedTuple):
    courses: list[course.Course]

    def get_course(self, course_name: str) -> course.Course:
        candidate_courses = [course_ for course_ in self.courses if course_.name == course_name]
        num_candidates = len(candidate_courses)

        if num_candidates == 0:
            raise GetCourseError(f"Could not find any courses with the name {course_name} in database.")
        if num_candidates > 1:
            raise GetCourseError(f"Found more than 1 course with the name {course_name} in database.")

        return candidate_courses[0]

