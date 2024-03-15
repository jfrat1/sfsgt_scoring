import contextlib
import tempfile
import pathlib
from typing import Generator

import pytest

from course_database import database

BAYLANDS_COURSE_DATA_YAML = """
{
  name: baylands,
  hole_par: {
    1: 5,
    2: 4,
    3: 5,
    4: 3,
    5: 4,
    6: 4,
    7: 4,
    8: 3,
    9: 5,
    10: 4,
    11: 4,
    12: 3,
    13: 5,
    14: 4,
    15: 3,
    16: 4,
    17: 3,
    18: 5,
  },
  tees: {
    black: {rating: 72.2, slope: 125, distance: 6680},
    blue: {rating: 69.6, slope: 119, distance: 6110},
    white: {rating: 66.8, slope: 110, distance: 5776},
  }
}
"""

PRESIDIO_COURSE_DATA_YAML = """
{
  name: presidio,
  hole_par: {
    1: 4,
    2: 5,
    3: 4,
    4: 3,
    5: 4,
    6: 4,
    7: 3,
    8: 4,
    9: 5,
    10: 5,
    11: 4,
    12: 4,
    13: 3,
    14: 4,
    15: 3,
    16: 4,
    17: 4,
    18: 5,
  },
  tees: {
    black: {rating: 72.6, slope: 135, distance: 6481},
    white: {rating: 71.1, slope: 132, distance: 6103},
    blue: {rating: 69.5, slope: 129, distance: 5746},
  }
}
"""

TEST_COURSE_FILES = {
    "baylands.yaml": BAYLANDS_COURSE_DATA_YAML,
    "presidio.yaml": PRESIDIO_COURSE_DATA_YAML
}

@contextlib.contextmanager
def temp_course_data_dir(course_files: dict[str, str] = TEST_COURSE_FILES) -> Generator[pathlib.Path, None, None]:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        for file_name, file_contents in course_files.items():
            (temp_path / file_name).write_text(file_contents)

        yield temp_path


def test_database_from_folder() -> None:
    with temp_course_data_dir() as courses_dir:
        course_db = database.database_from_folder(courses_dir)
        course_names = {course.name for course in course_db.courses}
        expected_names = {"baylands", "presidio"}
        assert course_names == expected_names


def test_get_course_nominal() -> None:
    with temp_course_data_dir() as courses_dir:
        course_db = database.database_from_folder(courses_dir)
        course = course_db.get_course("baylands")

        assert course.name == "baylands"
        assert course.hole_par[1] == 5

def test_get_course_not_found_raises_error() -> None:
    with temp_course_data_dir() as courses_dir:
        course_db = database.database_from_folder(courses_dir)
        with pytest.raises(database.GetCourseError):
            course_db.get_course("not a known course")

def test_get_course_multiple_found_raises_error() -> None:
    course_files = TEST_COURSE_FILES
    course_files["baylands_duplicate"] = BAYLANDS_COURSE_DATA_YAML
    with temp_course_data_dir(course_files=course_files) as courses_dir:
        course_db = database.database_from_folder(courses_dir)
        with pytest.raises(database.GetCourseError):
            course_db.get_course("baylands")