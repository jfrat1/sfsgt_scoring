import enum
import pathlib

import pydantic
import pydantic_yaml
import pandas as pd


FOLDER_PATH = pathlib.Path(__file__).parent


class Headers(enum.Enum):
    TeeName = "Tee Name"
    Gender = "Gender"
    Par = "Par"
    Rating = "Course Rating™"
    Slope = "Slope Rating®"


class Tee(pydantic.BaseModel):
    rating: float
    slope: int


class GenderTees(pydantic.BaseModel):
    tees: dict[str, Tee]


class Course(pydantic.BaseModel):
    name: str
    hole_pars: list[int]
    mens_tees: dict[str, Tee]
    womens_tees: dict[str, Tee]


def main() -> None:
    txt_files = FOLDER_PATH.glob("*.txt")
    for txt_file in txt_files:
        raw_df = pd.read_csv(txt_file, delimiter="\t")

        name = txt_file.name.rstrip(".txt").replace("_", " ")

        mens_tees: dict[str, Tee] = {}
        womens_tees: dict[str, Tee] = {}

        for _, tee_row in raw_df.iterrows():
            tee_name = tee_row[Headers.TeeName.value].lower()
            tee_rating = tee_row[Headers.Rating.value]
            tee_slope = tee_row[Headers.Slope.value]
            gender = tee_row[Headers.Gender.value]

            tee = Tee(rating=tee_rating, slope=tee_slope)
            if gender == "M":
                mens_tees[tee_name] = tee
            elif gender == "F":
                womens_tees[tee_name] = tee

        course = Course(name=name, hole_pars=[], mens_tees=mens_tees, womens_tees=womens_tees)
        json_file = FOLDER_PATH / "jsons" / txt_file.name.replace(".txt", ".json")
        json_file.touch(exist_ok=True)
        json_txt = course.model_dump_json(indent=2)
        json_file.write_text(json_txt)

        yaml_file = FOLDER_PATH / "yamls" / txt_file.name.replace(".txt", ".yaml")
        yaml_file.touch(exist_ok=True)
        pydantic_yaml.to_yaml_file(file=yaml_file, model=course, default_flow_style=None)


if __name__ == "__main__":
    main()
