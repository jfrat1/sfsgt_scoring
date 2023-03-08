import pytest

from ..src.course import Hole
from . import test_data

def test_tee_init():
    tee = test_data.courses.PRESIDIO_BLUE_TEE

def test_hole_init():
    hole = Hole(num=1, par=4)

def test_hole_num_too_high():
    with pytest.raises(AssertionError, match="got 19"):
        hole = Hole(num=19, par=4)

def test_hole_par_too_high():
    with pytest.raises(AssertionError, match="got 6"):
        hole = Hole(num=1, par=6)

def test_course_init():
    course = test_data.courses.PRESIDIO

def test_course_available_tees():
    course = test_data.courses.PRESIDIO
    assert course.available_tees() == [
        "Blue",
        "White",
        "Black",
    ]

def test_course_total_par():
    course = test_data.courses.PRESIDIO
    assert course.total_par() == 72

def test_course_num_holes():
    course = test_data.courses.PRESIDIO
    assert course.num_holes() == 18