import click

from sfsgt_scoring import (
    season_config,
    season_runner,
)

@click.command()
@click.option("--season", "season_name", required=True, help="Season to be executed.")
def cli(season_name: str) -> None:
    season_cfg = season_config.load_season_config(season_name)
    runner = season_runner.SeasonRunner(season_cfg=season_cfg)
    runner.run()




if __name__ == "__main__":
    cli()