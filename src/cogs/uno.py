from discord.ext import commands
import sys

sys.path.insert(0, r"C:\Users\Charles\Documents\Python Scripts\Discord 3.0")
import discord


class Uno(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="test", aliases=['t'])
    async def test(self, ctx):
        for emoji in ctx.guild.emojis:
            print(emoji.id)
        emoji = self.bot.get_emoji(893523538173124640)
        await ctx.message.add_reaction("<:Red_0:893523350805168138>")


def setup(bot):
    bot.add_cog(Uno(bot))
