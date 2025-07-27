from season_view.google_sheet_view import features


def process_raw_player_name(name_raw: str) -> str:
    name = _canonicalize_player_name(name_raw) if features.FTR_CANONICALIZE_PLAYER_NAMES else name_raw

    match features.FTR_PLAYER_NAME_CASE:
        case features.NameCase.UPPER:
            name = name.upper()
        case features.NameCase.LOWER:
            name = name.lower()
        case features.NameCase.TITLE:
            name = name.title()

    return name


def _canonicalize_player_name(name: str) -> str:
    if "," in name:
        name_parts = name.split(",")
        if len(name_parts) != 2:
            raise ValueError(f"Player names with commas (surname first) should have only 1 comma. Got {name}")

        first_name = name_parts[1].strip()
        last_name = name_parts[0].strip()

        return " ".join([first_name, last_name])

    else:
        return name
