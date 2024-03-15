import pathlib

from .config import load_season_config_file, SeasonConfig

SEASON_CONFIG_PATH = pathlib.Path(__file__).parent / "seasons"

class SeasonConfigFileNotFoundError(Exception):
    """Exception to be raised when an error encountered while loading a season config."""

def load_season_config(season: str) -> SeasonConfig:
    season_config_file_name = season + ".yaml"
    season_config_file = SEASON_CONFIG_PATH / season_config_file_name
    if not season_config_file.is_file():
        raise SeasonConfigFileNotFoundError(f"Can't locate season config file at: {season_config_file}.")

    return load_season_config_file(file_path=season_config_file)