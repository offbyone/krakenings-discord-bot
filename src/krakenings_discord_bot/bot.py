import discord
from discord.ext import commands


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
