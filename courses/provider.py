import abc
import pathlib

from . import course

DEFAULT_COURSE_DATA_PATH = pathlib.Path(__file__).parent / "data"


class CourseLoadError(Exception):
    """Exception to be raised when an error is encountered while attempting to load a course."""


class GetCourseError(Exception):
    """Exception to be raised when an error is encountered while searching for a course by name."""


class CourseProvider(abc.ABC):
    @abc.abstractmethod
    def get_course(self, course_name: str) -> course.Course:
        pass


class ConcreteCourseProvider(CourseProvider):
    def __init__(self, courses: list[course.Course]) -> None:
        self.courses = courses

    def get_course(self, course_name: str) -> course.Course:
        candidate_courses = [course_ for course_ in self.courses if course_.name == course_name]
        num_candidates = len(candidate_courses)

        if num_candidates == 0:
            raise GetCourseError(f"Could not find any courses with the name {course_name} in database.")
        if num_candidates > 1:
            raise GetCourseError(f"Found more than 1 course with the name {course_name} in database.")

        return candidate_courses[0]


def build_concrete_course_provider_from_folder(courses_dir: pathlib.Path) -> ConcreteCourseProvider:
    courses: list[course.Course] = []
    for course_file in courses_dir.glob("*"):
        try:
            course_ = course.load_course_file(course_file)
            courses.append(course_)
        except course.CourseError as exc:
            raise CourseLoadError(
                f"Unable to load database. Error encountere while processing file: {course_file}."
            ) from exc

    return ConcreteCourseProvider(courses)


def build_default_concrete_course_provider() -> ConcreteCourseProvider:
    return build_concrete_course_provider_from_folder(courses_dir=DEFAULT_COURSE_DATA_PATH)
