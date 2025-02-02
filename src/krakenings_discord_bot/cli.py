import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

import click
import environ
import httpx
import icecream
import tomli
from rich import print

from krakenings_discord_bot import init
from krakenings_discord_bot.bot import Bot, make_discord_payload
from krakenings_discord_bot.espn import (
    Event,
    Schedule,
    TeamsModel,
    fetch_image,
    schedule_for_league,
)


@dataclass
class AppConfig:
    local: bool = False


@environ.config()
class BotConfig:
    bot_token = environ.var()
    guild_id = environ.var()
    channel_id = environ.var()


@environ.config()
class WebhookConfig:
    webhook_url = environ.var()


@click.group()
@click.option("--local", is_flag=True, default=False)
@click.pass_context
def main(ctx, local):
    ctx.obj = AppConfig(local=local)
    init()
    icecream.install()


@main.command()
@click.option("--config-file", type=Path, default=Path("config.toml"))
@click.option("--send", is_flag=True, type=bool, default=False)
@click.argument("sport")
@click.argument("league")
@click.pass_obj
def schedule(obj: AppConfig, config_file: Path, sport: str, league: str, send: bool):
    app_config: WebhookConfig = WebhookConfig.from_environ()
    config = tomli.load(config_file.open(mode="rb"))

    if obj.local:
        path = Path("data") / f"espn-{sport}.json"
        schedule = Schedule.model_validate_json(path.read_text())

    else:
        schedule = schedule_for_league(sport, league)

    teams_to_check = config[sport]["teams"]

    events: list[Event] = []
    for event in schedule.events:
        if any(t in event.get_team_abbreviations() for t in teams_to_check):
            events.append(event)

    payloads = [make_discord_payload(e) for e in events]
    vs_images = [e.get_vs_image() for e in events]
    if send:
        for payload, vs_image in zip(payloads, vs_images):
            response = httpx.post(
                app_config.webhook_url,
                data={"payload_json": json.dumps(payload)},
                files={"vs-image": ("vs.png", vs_image, "image/png")},
            )
            print(response.text)
            response.raise_for_status()
    else:
        print(payloads)
    # print(schedule.events)


@main.command()
@click.argument("sport")
@click.argument("league")
@click.pass_obj
def teams(obj: AppConfig, sport: str, league: str):
    if obj.local:
        path = Path("data") / f"espn-{sport}-teams.json"
        json_content = path.read_text()
        teams = TeamsModel.model_validate_json(json_content)
    else:
        teams = teams_for_league(sport, league)

    print(repr(teams))


@main.command()
@click.argument("sport")
@click.argument("league")
@click.argument("team_a")
@click.argument("team_b")
@click.pass_obj
def vs_logo(obj: AppConfig, sport: str, league: str, team_a: str, team_b: str):
    if obj.local:
        path = Path("data") / f"espn-{sport}-teams.json"
        json_content = path.read_text()
        teams = TeamsModel.model_validate_json(json_content)
    else:
        teams = asyncio.run(teams_for_league(sport, league))

    away_team = teams.get_team(team_a)
    home_team = teams.get_team(team_b)

    import PIL
    from textual_image.renderable import Image

    from .images import Dimensions, make_vs_image

    home_team_logo = fetch_image(home_team.get_logo_url())
    away_team_logo = fetch_image(away_team.get_logo_url())
    print(Image(home_team_logo))
    print(Image(away_team_logo))

    print(Image(make_vs_image(home_team_logo, away_team_logo, Dimensions(800, 400))))


@main.command()
def bot():
    app_config: BotConfig = BotConfig.from_environ()

    bot = Bot(app_config.bot_token, app_config.guild_id, "!")

    # connect teams here
    bot.run(app_config.bot_token)


if __name__ == "__main__":
    main()
