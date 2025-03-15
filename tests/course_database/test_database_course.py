import contextlib
import pathlib
import tempfile
from typing import Generator

import pytest
from courses import course
from season_common import player

DEFAULT_COURSE_DATA_YAML = """
{
  name: baylands,
  hole_pars: [5, 4, 5, 3, 4, 4, 4, 3, 5, 4, 4, 3, 5, 4, 3, 4, 3, 5],
  mens_tees: {
    black: {rating: 72.2, slope: 125},
    blue: {rating: 69.6, slope: 119},
    white: {rating: 66.8, slope: 110},
  },
  womens_tees: {
    white: {rating: 71.9, slope: 122},
    green: {rating: 68.1, slope: 113},
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


COURSE_DATA_YAML_MISSING_HOLE_PARS = """
{
  name: baylands,
  hole_pars: [5, 4, 5, 3],
  mens_tees: {},
  womens_tees: {}
}
"""


def test_load_course_missing_holes_raises_error() -> None:
    with temp_course_yaml_file(yaml_data=COURSE_DATA_YAML_MISSING_HOLE_PARS) as course_file:
        with pytest.raises(course.CourseError):
            course.load_course_file(course_file)


COURSE_DATA_YAML_19_HOLE_PARS = """
{
  name: baylands,
  hole_pars: [5, 4, 5, 3, 4, 4, 4, 3, 5, 4, 4, 3, 5, 4, 3, 4, 3, 5, 3],
  mens_tees: {},
  womens_tees: {}
}
"""


def test_load_course_too_many_holes_raises_error() -> None:
    with temp_course_yaml_file(yaml_data=COURSE_DATA_YAML_19_HOLE_PARS) as course_file:
        with pytest.raises(course.CourseError):
            course.load_course_file(course_file)


COURSE_DATA_YAML_HOLE_1_HAS_PAR_6 = """
{
  name: baylands,
  hole_pars: [6, 4, 5, 3, 4, 4, 4, 3, 5, 4, 4, 3, 5, 4, 3, 4, 3, 5],
  mens_tees: {},
  womens_tees: {}
}
"""


def test_load_course_hole_has_par_6_raises_error() -> None:
    with temp_course_yaml_file(yaml_data=COURSE_DATA_YAML_HOLE_1_HAS_PAR_6) as course_file:
        with pytest.raises(course.CourseError):
            course.load_course_file(course_file)


COURSE_DATA_YAML_HOLE_1_HAS_PAR_2 = """
{
  name: baylands,
  hole_pars: [2, 4, 5, 3, 4, 4, 4, 3, 5, 4, 4, 3, 5, 4, 3, 4, 3, 5],
  tees: {}
}
"""


def test_load_course_hole_has_par_2_raises_error() -> None:
    with temp_course_yaml_file(yaml_data=COURSE_DATA_YAML_HOLE_1_HAS_PAR_2) as course_file:
        with pytest.raises(course.CourseError):
            course.load_course_file(course_file)


def test_get_tee_info_mens_tees() -> None:
    with temp_course_yaml_file() as course_file:
        course_obj = course.load_course_file(course_file)
        tee_info = course_obj.get_tee_info(tee_name="blue", player_gender=player.PlayerGender.MALE)

        assert isinstance(tee_info, course.TeeInfo)
        assert tee_info.rating == 69.6
        assert tee_info.slope == 119


def test_get_tee_info_womens_tees() -> None:
    with temp_course_yaml_file() as course_file:
        course_obj = course.load_course_file(course_file)
        tee_info = course_obj.get_tee_info(tee_name="white", player_gender=player.PlayerGender.FEMALE)

        assert isinstance(tee_info, course.TeeInfo)
        assert tee_info.rating == 71.9
        assert tee_info.slope == 122


def test_get_tee_info_cant_find_tee_name_raises_error() -> None:
    with temp_course_yaml_file() as course_file:
        course_obj = course.load_course_file(course_file)
        with pytest.raises(KeyError):
            course_obj.get_tee_info("not a valid tee name")


def test_par_property() -> None:
    with temp_course_yaml_file() as course_file:
        course_obj = course.load_course_file(course_file)
        assert course_obj.par == 72


def test_hole_par() -> None:
    with temp_course_yaml_file() as course_file:
        course_obj = course.load_course_file(course_file)
        assert course_obj.hole_par(1) == 5
        assert course_obj.hole_par(16) == 4
