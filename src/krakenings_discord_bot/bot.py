from zoneinfo import ZoneInfo

import discord
import humanize
import pydantic
from discord.ext import commands
from pydantic_extra_types.color import Color

from krakenings_discord_bot.espn import Event

LOCAL_TIMEZONE = ZoneInfo("America/Los_Angeles")


class Bot(commands.Bot):
    def __init__(self, token: str, guild: str, command_prefix: str, **options) -> None:
        """
        Summary:
        Initialize the bot.

        Args:
            token: bot token
            guild: server id the bot should interact with
            command_prefix: [$,!,>,etc.] prefix for commands
            **options:
        """
        intents = options.pop("intents", discord.Intents.default())
        intents.guild_scheduled_events = True
        super().__init__(command_prefix, intents=intents, **options)
        self.token = token
        self.guild = guild

    async def on_ready(self) -> None:
        """
        Summary:
        Called when bot is ready to be used.
        """
        print("Logged in as", self.user)


def make_discord_payload(event: Event, include_vs: bool = True) -> dict:
    """
    Summary:
    Create a discord payload for a given event.

    Args:
    event: event to create payload for

    Returns:
    dict: discord payload
    """
    event_timestamp = event.date.astimezone(LOCAL_TIMEZONE)
    embed = {
        "description": f"{event.name} at {event_timestamp.strftime('%I:%M %p %Z')}",
        "color": discord_color(event.competitions[0].competitors[0].team.color).value,
    }
    if include_vs:
        embed["image"] = {"url": "attachment://vs.png"}

    return {
        "content": f"**Game Today** - {event.short_name}",
        "embeds": [embed],
    }


def discord_color(color: Color) -> discord.Color:
    """
    Summary:
    Convert a pydantic color to a discord color.

    Args:
    color: color to convert

    Returns:
    discord.Color: discord color
    """
    r, g, b = color.as_rgb_tuple(alpha=False)
    return discord.Color.from_rgb(r, g, b)
