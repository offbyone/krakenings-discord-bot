import click
from src.krakenings_discord_bot.bot import Bot


@click.command()
def main():
    config = {
        "BOT_TOKEN": "your_bot_token_here",
        "GUILD_ID": "your_guild_id_here",
        "ICAL_URL": "your_ical_url_here",
        "CHANNEL_ID": "your_channel_id_here",
    }

    bot = Bot(config["BOT_TOKEN"], config["GUILD_ID"], "!")

    # connect teams here
    bot.run(config["BOT_TOKEN"])


if __name__ == "__main__":
    main()
