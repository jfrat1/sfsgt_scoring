
from sfsgt_scoring.spreadsheet.google import (
    sheet as google_sheet,
)
from sfsgt_scoring.spreadsheet.google import (
    worksheet as google_ws,
)

standard_background = {
    "red": 252,
    "green": 245,
    "blue": 243,
}

birdie_background = {
    "red": 217,
    "green": 234,
    "blue": 211,
}

eagle_background = {
    "red": 255,
    "green": 187,
    "blue": 137,
}


def rgb_int_to_float(rgb_int: dict[str, int]) -> dict[str, float]:
    return {
        "red": rgb_int["red"] / 255,
        "green": rgb_int["green"] / 255,
        "blue": rgb_int["blue"] / 255,
    }


def main() -> None:
    sheet = google_sheet.GoogleSheet(sheet_id="1QgFf90TOe0gjWdgU2YiJ-pmFM6xW3wplQUK38hIbMl0")

    baylands_ws = sheet.worksheet("Baylands")

    # normal_cell_format = gspread.worksheet.CellFormat(
    #     range="D9",
    #     format={
    #         "backgroundColorStyle": {
    #             "rgbColor": rgb_int_to_float(standard_background)
    #         },
    #     },
    # )
    normal_cell_format = google_ws.RangeFormat(
        range="D9",
        format=google_ws.CellFormat(backgroundColor=google_ws.ColorRgb(**standard_background)),
    )
    birdie_cell_format = google_ws.RangeFormat(
        range="E9",
        format=google_ws.CellFormat(backgroundColor=google_ws.ColorRgb(**birdie_background)),
    )
    eagle_cell_format = google_ws.RangeFormat(
        range="I9",
        format=google_ws.CellFormat(backgroundColor=google_ws.ColorRgb(**eagle_background)),
    )
    player_names = baylands_ws.column_range_values(
        column="B",
        first_row=8,
        last_row=49,
    )

    # birdie_cell_format = gspread.worksheet.CellFormat(
    #     {
    #         "range": "E9",
    #         "format": {
    #             "backgroundColorStyle": {
    #                 "rgbColor": rgb_int_to_float(birdie_background),
    #             },
    #         },
    #     }
    # )
    # eagle_cell_format = gspread.worksheet.CellFormat(
    #     range="I9",
    #     format={
    #         "backgroundColorStyle": {
    #             "rgbColor": rgb_int_to_float(eagle_background)
    #         },
    #     },
    # )

    baylands_ws.format_multiple_ranges(
        range_formats=[normal_cell_format, birdie_cell_format, eagle_cell_format]
    )
    # baylands_ws.worksheet.batch_format([normal_cell_format, birdie_cell_format, eagle_cell_format]) . # noqa: E501
    print("here")


if __name__ == "__main__":
    main()
