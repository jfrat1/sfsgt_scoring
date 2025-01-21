import abc
import pathlib

from courses.course import Course, CourseError, load_course_file

DEFAULT_COURSE_DATA_PATH = pathlib.Path(__file__).parent / "data"


class CourseLoadError(Exception):
    """Exception to be raised when an error is encountered while attempting to load a course."""


class CourseProviderError(Exception):
    """Exception to be raised when an error is encountered in a course provider."""


class CourseProvider(abc.ABC):
    @abc.abstractmethod
    def get_course(self, course_name: str) -> Course:
        pass


class ConcreteCourseProvider(CourseProvider):
    def __init__(self, courses: list[Course]) -> None:
        self.courses = courses
        self._check_duplicate_course_names()

    def get_course(self, course_name: str) -> Course:
        for course in self.courses:
            if course.name.lower() == course_name.lower():
                return course

        raise CourseProviderError(f"Could not find any courses with the name {course_name}.")

    def _check_duplicate_course_names(self) -> None:
        course_names = [course.name for course in self.courses]
        num_courses = len(course_names)

        unique_courses = set(course_names)
        num_unique_courses = len(unique_courses)

        if num_unique_courses != num_courses:
            duplicates = [course for course in unique_courses if course_names.count(course) > 1]
            raise CourseProviderError(
                f"Course names must be unique. Found the following duplicate course names: {duplicates}"
            )


def build_concrete_course_provider_from_folder(courses_dir: pathlib.Path) -> ConcreteCourseProvider:
    courses: list[Course] = []
    for course_file in courses_dir.glob("*"):
        try:
            course_ = load_course_file(course_file)
            courses.append(course_)
        except CourseError as exc:
            raise CourseLoadError(
                f"Unable to load database. Error encountere while processing file: {course_file}."
            ) from exc

    return ConcreteCourseProvider(courses)


def build_default_concrete_course_provider() -> ConcreteCourseProvider:
    return build_concrete_course_provider_from_folder(courses_dir=DEFAULT_COURSE_DATA_PATH)
