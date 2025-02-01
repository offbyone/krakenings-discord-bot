import asyncio
from pathlib import Path

import click
import environ
import tomli
from rich import print

from krakenings_discord_bot.espn import Schedule, TeamsModel, schedule_for_league
from src.krakenings_discord_bot.bot import Bot


@environ.config()
class BotConfig:
    bot_token = environ.var()
    guild_id = environ.var()
    channel_id = environ.var()


@environ.config()
class WebhookConfig:
    webhook_url = environ.var()


@click.group()
def main(): ...


@main.command()
@click.option("--config-file", type=Path, default=Path("config.toml"))
@click.option("--from-json", type=Path, default=None)
@click.option("--send", is_flag=True, type=Path, default=False)
def schedule(config_file: Path, from_json: Path | None, send: bool):
    app_config: WebhookConfig = WebhookConfig.from_environ()
    config = tomli.load(config_file.open(mode="rb"))

    # testing
    if from_json:
        json_content = from_json.read_text()
        print(Schedule.model_validate_json(json_content).events)
    else:
        schedule = asyncio.run(schedule_for_league("hockey", "nhl"))
        print(repr(schedule))


@main.command()
@click.option("--from-json", type=Path, default=None)
def teams(from_json: Path | None):
    # testing
    if from_json:
        json_content = from_json.read_text()
        teams = TeamsModel.model_validate_json(json_content)
    else:
        teams = asyncio.run(teams_for_league("hockey", "nhl"))
    print(repr(teams))


@main.command()
@click.argument("team_a")
@click.argument("team_b")
def vs_logo(team_a: str, team_b: str): ...


@main.command()
def bot():
    app_config: BotConfig = BotConfig.from_environ()

    bot = Bot(app_config.bot_token, app_config.guild_id, "!")

    # connect teams here
    bot.run(app_config.bot_token)


if __name__ == "__main__":
    main()
