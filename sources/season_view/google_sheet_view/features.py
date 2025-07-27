import enum

# If sortable names are in the players sheet (Last, First), convert them to canonical name (First Last)
FTR_CANONICALIZE_PLAYER_NAMES = True


class NameCase(enum.Enum):
    UPPER = enum.auto()
    LOWER = enum.auto()
    TITLE = enum.auto()


# When player names are being read from worksheets, use this case.
# This allows player names to have mixed case between the players sheet and event sheets.
# Additionally, this is the case that will be used when player names are written to the
# leaderboard sheet.
FTR_PLAYER_NAME_CASE = NameCase.TITLE
