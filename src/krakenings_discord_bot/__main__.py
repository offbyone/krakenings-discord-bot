from pathlib import Path

import click
import environ
import tomli

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
def schedule(config_file: Path):
    app_config: WebhookConfig = WebhookConfig.from_environ()
    config = tomli.load(config_file.open(mode="rb"))
    click.echo("schedule")


@main.command()
def bot():
    app_config: BotConfig = BotConfig.from_environ()

    bot = Bot(app_config.bot_token, app_config.guild_id, "!")

    # connect teams here
    bot.run(app_config.bot_token)


if __name__ == "__main__":
    main()
