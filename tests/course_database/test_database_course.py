import contextlib
import pathlib
import tempfile
from typing import Generator

import pytest

from course_database import course

DEFAULT_COURSE_DATA_YAML = """
{
  name: baylands,
  hole_pars: {
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


@contextlib.contextmanager
def temp_course_yaml_file(
    yaml_data: str = DEFAULT_COURSE_DATA_YAML,
) -> Generator[pathlib.Path, None, None]:
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="r+") as temp_file:
        temp_file_path = pathlib.Path(temp_file.name)
        temp_file_path.write_text(yaml_data)

        yield temp_file_path


def test_load_course() -> None:
    with temp_course_yaml_file() as course_file:
        course_obj = course.load_course_file(course_file)

        assert course_obj.name == "baylands"


COURSE_DATA_YAML_MISSING_HOLE_NUMBERS = """
{
  name: baylands,
  hole_pars: {
    1: 5,
    2: 4,
    3: 5,
    4: 3,
  },
  tees: {
    black: {rating: 72.2, slope: 125, distance: 6680},
    blue: {rating: 69.6, slope: 119, distance: 6110},
    white: {rating: 66.8, slope: 110, distance: 5776},
  }
}
"""


def test_load_course_missing_holes_raises_error() -> None:
    with temp_course_yaml_file(yaml_data=COURSE_DATA_YAML_MISSING_HOLE_NUMBERS) as course_file:
        with pytest.raises(course.CourseLoadError):
            course.load_course_file(course_file)


COURSE_DATA_YAML_TOO_MANY_HOLE_NUMBERS = """
{
  name: baylands,
  hole_pars: {
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
    19: 4,
  },
  tees: {
    black: {rating: 72.2, slope: 125, distance: 6680},
    blue: {rating: 69.6, slope: 119, distance: 6110},
    white: {rating: 66.8, slope: 110, distance: 5776},
  }
}
"""


def test_load_course_too_many_holes_raises_error() -> None:
    with temp_course_yaml_file(yaml_data=COURSE_DATA_YAML_TOO_MANY_HOLE_NUMBERS) as course_file:
        with pytest.raises(course.CourseLoadError):
            course.load_course_file(course_file)


COURSE_DATA_YAML_HOLE_1_HAS_PAR_6 = """
{
  name: baylands,
  hole_pars: {
    1: 6,
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


def test_load_course_hole_has_par_6_raises_error() -> None:
    with temp_course_yaml_file(yaml_data=COURSE_DATA_YAML_HOLE_1_HAS_PAR_6) as course_file:
        with pytest.raises(course.CourseLoadError):
            course.load_course_file(course_file)


COURSE_DATA_YAML_HOLE_1_HAS_PAR_2 = """
{
  name: baylands,
  hole_pars: {
    1: 2,
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


def test_load_course_hole_has_par_2_raises_error() -> None:
    with temp_course_yaml_file(yaml_data=COURSE_DATA_YAML_HOLE_1_HAS_PAR_2) as course_file:
        with pytest.raises(course.CourseLoadError):
            course.load_course_file(course_file)


def test_get_tee_info_nominal() -> None:
    with temp_course_yaml_file() as course_file:
        course_obj = course.load_course_file(course_file)
        tee_info = course_obj.get_tee_info("blue")

        assert isinstance(tee_info, course.TeeInfo)
        assert tee_info.rating == 69.6
        assert tee_info.slope == 119
        assert tee_info.distance == 6110


def test_get_tee_info_cant_find_tee_name_raises_error() -> None:
    with temp_course_yaml_file() as course_file:
        course_obj = course.load_course_file(course_file)
        with pytest.raises(KeyError):
            course_obj.get_tee_info("not a valid tee name")


def test_par_property() -> None:
    with temp_course_yaml_file() as course_file:
        course_obj = course.load_course_file(course_file)
        assert course_obj.par == 72
