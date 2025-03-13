import contextlib
import pathlib
import tempfile
from typing import Generator

import pytest

from courses import provider

BAYLANDS_COURSE_DATA_YAML = """
{
  name: baylands,
  hole_pars: [5, 4, 5, 3, 4, 4, 4, 3, 5, 4, 4, 3, 5, 4, 3, 4, 3, 5],
  mens_tees: {
    black: {rating: 72.2, slope: 125},
    blue: {rating: 69.6, slope: 119},
    white: {rating: 66.8, slope: 110},
  },
  womens_tees: {},
}
"""

PRESIDIO_COURSE_DATA_YAML = """
{
  name: presidio,
  hole_pars: [4, 5, 4, 3, 4, 4, 3, 4, 5, 5, 4, 4, 3, 4, 3, 4, 4, 5],
  mens_tees: {
    black: {rating: 72.6, slope: 135},
    white: {rating: 71.1, slope: 132},
    blue: {rating: 69.5, slope: 129},
  },
  womens_tees: {},
}
"""

TEST_COURSE_FILES = {
    "baylands.yaml": BAYLANDS_COURSE_DATA_YAML,
    "presidio.yaml": PRESIDIO_COURSE_DATA_YAML,
}


@contextlib.contextmanager
def temp_course_data_dir(
    course_files: dict[str, str] = TEST_COURSE_FILES,
) -> Generator[pathlib.Path, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        for file_name, file_contents in course_files.items():
            (temp_path / file_name).write_text(file_contents)

        yield temp_path


def test_build_concrete_course_provider_from_folder() -> None:
    with temp_course_data_dir() as courses_dir:
        course_db = provider.build_concrete_course_provider_from_folder(courses_dir)
        course_names = {course.name for course in course_db.courses}
        expected_names = {"baylands", "presidio"}
        assert course_names == expected_names


def test_get_course_nominal() -> None:
    with temp_course_data_dir() as courses_dir:
        course_db = provider.build_concrete_course_provider_from_folder(courses_dir)
        course = course_db.get_course("baylands")

        assert course.name == "baylands"
        assert course.hole_pars[1] == 5


def test_get_course_not_found_raises_error() -> None:
    with temp_course_data_dir() as courses_dir:
        course_db = provider.build_concrete_course_provider_from_folder(courses_dir)
        with pytest.raises(provider.CourseProviderError):
            course_db.get_course("not a known course")


def test_instantiate_course_with_duplicate_course_names_raises_error() -> None:
    course_files = TEST_COURSE_FILES
    course_files["baylands_duplicate.yaml"] = BAYLANDS_COURSE_DATA_YAML
    with temp_course_data_dir(course_files=course_files) as courses_dir:
        with pytest.raises(provider.CourseProviderError):
            provider.build_concrete_course_provider_from_folder(courses_dir)
