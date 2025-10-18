import logging
import os

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    def __init__(self, token: str, command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token = token

    async def setup_hook(self):
        """Load all cogs dynamically from ./cogs folder"""

        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")

        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                ext = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(ext)
                except Exception as _e:
                    logger.exception("Failed to load %s", ext)

    async def on_ready(self):
        pass

    async def send_message(self, channel_id: int, message: str):
        """Send a message to a specific channel."""
        await self.wait_until_ready()
        channel = self.get_channel(channel_id)
        if channel:
            await channel.send(message)
        else:
            logger.error("Channel with ID %s not found.", channel_id)

    def run_bot(self):
        """Start the bot (blocking)."""
        super().run(self.token)


if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("DISCORD_BOT_TOKEN environment variable not set.")

    bot = DiscordBot(token, command_prefix="@")
    bot.run_bot()
