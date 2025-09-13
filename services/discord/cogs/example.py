from discord.ext import commands


class ExampleCommands(commands.Cog):
    """Example cog with basic commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="hello")
    async def hello(self, ctx):
        """Responds with Hello! when user types @hello"""
        await ctx.send("Hello!")

    @commands.command(name="repeat")
    async def repeat(self, ctx, *, text: str):
        """Repeats whatever the user says"""
        await ctx.send(text)


# Required for dynamic loading
async def setup(bot: commands.Bot):
    await bot.add_cog(ExampleCommands(bot))
