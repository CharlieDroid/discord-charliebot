from discord.ext import commands
import sys

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import common


class Features(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="grow_castle", aliases=["gc"])
    async def grow_castle(self, ctx, waves):
        pass


def setup(bot):
    bot.add_cog(Features(bot))
